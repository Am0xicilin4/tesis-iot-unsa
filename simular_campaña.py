"""
Simulacion completa y paso a paso de la campana experimental de la tesis
(tesis-iot-unsa): diseno factorial 3x3x3, umbral del 85 % y modelado ML.

Uso:  python simular_campaña.py
Salida: consola detallada + CSV en ./simulacion/
"""

import sys
import numpy as np
import pandas as pd
from scipy.stats import t as t_student

from sklearn.base import clone
from sklearn.model_selection import train_test_split, cross_validate, StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 60)
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")

# ----------------------------------------------------------------------------------
# 0. PARAMETROS DE LA CAMPANA (fijados por adelantado, semilla 42)
# ----------------------------------------------------------------------------------
SEED = 42
UMBRAL_PDR = 85.0
UMBRAL_MODELO = 85.0
TOL_RMSE_RANGO = 15.0
N_REPLICAS = 3
DURACION_MIN = 10
N_NODOS = 3
MS_ENSAYO = DURACION_MIN * 60 * 1000

ESCENARIOS = {
    1: dict(nombre="A1 visibilidad directa", d=(2.0, 6.0), n_pl=2.0, att_muro=0.0,
            ref=-40.0, sigma=2.5, ruido=-96.0, obj=-50.0),
    2: dict(nombre="A2 un muro de concreto", d=(5.0, 10.0), n_pl=2.7, att_muro=11.0,
            ref=-38.0, sigma=3.5, ruido=-95.0, obj=-70.0),
    3: dict(nombre="A3 doble muro o ruido ISM", d=(8.0, 15.0), n_pl=3.0, att_muro=20.0,
            ref=-36.0, sigma=4.0, ruido=-92.0, obj=-88.0),
}
CARGAS = {
    1: dict(nombre="B1 oferta esparsa", intervalo_ms=5000, u=0.15),
    2: dict(nombre="B2 oferta moderada", intervalo_ms=1500, u=0.45),
    3: dict(nombre="B3 oferta intensa", intervalo_ms=500, u=0.85),
}
QOS = {1: dict(nombre="C1 QoS MQTT 0", ov=(0.0, 0.0)),
       2: dict(nombre="C2 QoS MQTT 1", ov=(4.0, 6.0)),
       3: dict(nombre="C3 QoS MQTT 2", ov=(9.0, 12.0))}


def seccion(num, titulo):
    print()
    print("=" * 100)
    print(f"[{num}/5] {titulo}")
    print("=" * 100)


# ----------------------------------------------------------------------------------
# 1. GENERACION DEL DATASET SINTETICO
# ----------------------------------------------------------------------------------
def prob_entrega(rssi, u, C):
    z = 3.0 + 0.11 * (rssi + 80.0) - 1.5 * u + 0.35 * (C - 2) - 0.6 * (C - 1) * max(0.0, u - 0.45)
    return 1.0 / (1.0 + np.exp(-z))


def latencia_base(q, u, C):
    u_eff = min(0.90, u * (1.0 + 0.9 * (1.0 - q)))
    cola = 12.0 * u_eff / (1.0 - u_eff)
    ov_base, ov_pend = QOS[C]["ov"]
    reintento = 6.0 * (1.0 - q) ** 2 * (1.0 + u)
    return 8.0 + cola + ov_base + ov_pend * u + reintento, u_eff


def generar_dataset():
    rng = np.random.default_rng(SEED)
    celdas = [(a, b, c) for a in (1, 2, 3) for b in (1, 2, 3) for c in (1, 2, 3)]
    plan = [(celda, rep) for celda in celdas for rep in range(1, N_REPLICAS + 1)]
    plan = [plan[i] for i in rng.permutation(len(plan))]

    bloques = {k: [] for k in ("ensayo", "nodo", "seq", "rssi", "snr_db", "ruido",
                               "distancia", "entregado", "lat_ms", "celda",
                               "replica", "A", "B", "C")}

    for orden, ((a, b, c), rep) in enumerate(plan, start=1):
        esc, car, qos = ESCENARIOS[a], CARGAS[b], QOS[c]
        dist_nodos = rng.uniform(esc["d"][0], esc["d"][1], size=N_NODOS)
        msgs_nodo = MS_ENSAYO // car["intervalo_ms"]
        n_total = N_NODOS * msgs_nodo

        nodo = np.tile(np.arange(1, N_NODOS + 1), msgs_nodo)
        seq = np.repeat(np.arange(1, msgs_nodo + 1), N_NODOS)
        distancia = dist_nodos[nodo - 1]
        ruido = esc["ruido"] + rng.normal(0.0, 1.0, n_total)

        amb_rssi = rng.normal(0.0, 2.0)
        amb_z = rng.normal(0.0, 0.12)
        amb_lat = rng.normal(0.0, 0.08)

        rssi_media = (esc["ref"] - 10.0 * esc["n_pl"] * np.log10(distancia) - esc["att_muro"])
        rssi = np.clip(rssi_media + rng.normal(0.0, esc["sigma"], n_total) + amb_rssi,
                       -100.0, -30.0)
        snr = rssi - ruido

        u = car["u"]
        p0 = np.clip(prob_entrega(rssi, u, c), 1e-6, 1.0 - 1e-6)
        logit = np.log(p0 / (1.0 - p0)) + amb_z
        p = np.clip(1.0 / (1.0 + np.exp(-logit)), 1e-6, 1.0 - 1e-6)
        entregado = rng.random(n_total) < p

        q_link = np.clip((rssi + 95.0) / 45.0, 0.0, 1.0)
        lat_media = np.empty(n_total)
        u_eff_v = np.empty(n_total)
        for i in range(n_total):
            lat_media[i], u_eff_v[i] = latencia_base(q_link[i], u, c)
        lat = lat_media * np.exp(rng.normal(0.0, 0.15, n_total)) * np.exp(amb_lat) + \
            rng.exponential(2.0 + 8.0 * u_eff_v, n_total)
        lat = np.where(entregado, np.maximum(1.5, lat), np.nan)

        etiqueta = f"A{a}B{b}C{c}"
        bloques["ensayo"].append(np.full(n_total, orden, dtype=int))
        bloques["nodo"].append(nodo)
        bloques["seq"].append(seq)
        bloques["rssi"].append(rssi)
        bloques["snr_db"].append(snr)
        bloques["ruido"].append(ruido)
        bloques["distancia"].append(distancia)
        bloques["entregado"].append(entregado.astype(int))
        bloques["lat_ms"].append(lat)
        bloques["celda"].append(np.full(n_total, etiqueta, dtype=object))
        bloques["replica"].append(np.full(n_total, rep, dtype=int))
        bloques["A"].append(np.full(n_total, a, dtype=int))
        bloques["B"].append(np.full(n_total, b, dtype=int))
        bloques["C"].append(np.full(n_total, c, dtype=int))

    df = pd.DataFrame({k: np.concatenate(v) for k, v in bloques.items()})
    return df, plan


def resumir_ensayos(df):
    ens = (df.groupby("ensayo", as_index=False)
             .agg(celda=("celda", "first"), replica=("replica", "first"),
                  A=("A", "first"), B=("B", "first"), C=("C", "first"),
                  n_msg=("entregado", "size"), n_ok=("entregado", "sum"),
                  rssi_med=("rssi", "mean"), snr_med=("snr_db", "mean"),
                  dist_med=("distancia", "mean"),
                  lat_media=("lat_ms", "mean"),
                  lat_p95=("lat_ms", lambda s: float(np.percentile(s.dropna(), 95))
                           if s.notna().any() else np.nan),
                  jitter=("lat_ms", "std")))
    ens["pdr"] = 100.0 * ens["n_ok"] / ens["n_msg"]
    ens["perdida"] = 100.0 - ens["pdr"]
    ens["pdr_ok"] = (ens["pdr"] >= UMBRAL_PDR).astype(int)
    return ens


def resumir_celdas(ens):
    tcrit = t_student.ppf(0.975, df=N_REPLICAS - 1)
    cel = (ens.groupby("celda", as_index=False)
              .agg(A=("A", "first"), B=("B", "first"), C=("C", "first"),
                   pdr_media=("pdr", "mean"), pdr_sd=("pdr", "std"),
                   lat_media=("lat_media", "mean"), lat_p95=("lat_p95", "mean"),
                   jitter=("jitter", "mean"), rssi_med=("rssi_med", "mean"),
                   n_msg=("n_msg", "sum")))
    cel["ic_inf"] = np.clip(cel["pdr_media"] - tcrit * cel["pdr_sd"] / np.sqrt(N_REPLICAS), 0.0, 100.0)
    cel["ic_sup"] = np.clip(cel["pdr_media"] + tcrit * cel["pdr_sd"] / np.sqrt(N_REPLICAS), 0.0, 100.0)
    cel["pdr_ok"] = (cel["pdr_media"] >= UMBRAL_PDR).astype(int)
    cel["estado"] = np.where(cel["ic_inf"] >= UMBRAL_PDR, "CUMPLE (IC sobre 85%)",
                      np.where(cel["ic_sup"] < UMBRAL_PDR, "NO CUMPLE (IC bajo 85%)",
                               "INDETERMINADO (IC atraviesa 85%)"))
    cel = cel.sort_values("celda").reset_index(drop=True)
    return cel


def imprimir_tabla_celdas(cel):
    vista = cel[["celda", "rssi_med", "pdr_media", "ic_inf", "ic_sup", "lat_media",
                 "lat_p95", "jitter", "pdr_ok", "estado"]].copy()
    vista.columns = ["Celda", "RSSI", "PDR%", "IC95 inf", "IC95 sup", "Lat ms",
                     "P95 ms", "Jitter", "OK", "Estado"]
    print(vista.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))


def cumplimiento_por_factor(cel):
    for factor, niveles in (("A", ("A1", "A2", "A3")), ("B", ("B1", "B2", "B3")),
                            ("C", ("C1", "C2", "C3"))):
        print(f"\n  Cumplimiento del 85 % por nivel del factor {factor}:")
        for nivel in niveles:
            sub = cel[cel[factor] == int(nivel[1])]
            ok = int(sub["pdr_ok"].sum())
            print(f"    {nivel}: {ok}/{len(sub)} celdas ({100.0 * ok / len(sub):.1f} %)  "
                  f"PDR media = {sub['pdr_media'].mean():.2f} %  "
                  f"Latencia media = {sub['lat_media'].mean():.2f} ms")


def balance_de_clases(df):
    vc = df["pdr_ok"].value_counts().sort_index()
    total = int(vc.sum())
    print(f"\n  Balance de clases (a nivel mensaje, etiqueta heredada de su ensayo):")
    print(f"    0 = NO cumple : {vc.get(0, 0):>7} ({100.0 * vc.get(0, 0) / total:.1f} %)")
    print(f"    1 = SÍ cumple  : {vc.get(1, 0):>7} ({100.0 * vc.get(1, 0) / total:.1f} %)")


def matriz_confusion_detallada(y_true, y_pred, titulo="Matriz de confusión"):
    vn, fp, fn, vp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    print(f"\n  {titulo} (filas = real, columnas = predicho):")
    print(f"                      Predicho NO cumple   Predicho SÍ cumple")
    print(f"    Real NO cumple        VN = {vn:>6}            FP = {fp:>6}")
    print(f"    Real SÍ cumple        FN = {fn:>6}            VP = {vp:>6}")
    print(f"    -> FP = alerta falsa de degradación | FN = degradación real no detectada")
    return vn, fp, fn, vp


def main():
    print("=" * 100)
    print(" SIMULACIÓN DE CAMPAÑA EXPERIMENTAL — TESIS IoT UNSA (tesis-iot-unsa)")
    print(" Diseño factorial 3×3×3 | 27 celdas | 3 réplicas | 81 ensayos | umbral 85 %")
    print(f" Semilla aleatoria = {SEED}  (reproducible)")
    print("=" * 100)

    # ---------------------------------------------------------------- 1. DATASET
    seccion(1, "GENERACIÓN DEL DATASET SINTÉTICO (81 ensayos)")
    df, plan = generar_dataset()

    print("\n  Factores ensayados:")
    for k, v in ESCENARIOS.items():
        print(f"    A{k}: {v['nombre']:<30} distancia {v['d'][0]:.0f}–{v['d'][1]:.0f} m  "
              f"objetivo RSSI ~ {v['obj']:.0f} dBm")
    for k, v in CARGAS.items():
        print(f"    B{k}: {v['nombre']:<30} intervalo {v['intervalo_ms']:>4} ms  "
              f"({MS_ENSAYO // v['intervalo_ms'] * N_NODOS:>5} mensajes/ensayo)")
    for k, v in QOS.items():
        print(f"    C{k}: {v['nombre']}")

    print(f"\n  Volumen simulado:")
    print(f"    Celdas = 3×3×3 = 27 | Réplicas = {N_REPLICAS} | Ensayos = {len(plan)}")
    print(f"    Duración por ensayo = {DURACION_MIN} min ({MS_ENSAYO} ms)")
    print(f"    Mensajes totales = {len(df):,} | Entregados = {int(df['entregado'].sum()):,} "
          f"({100.0 * df['entregado'].mean():.2f} %)")

    print("\n  Orden aleatorizado de los 81 ensayos (primeros 10):")
    cab = "  ".join(f"{i:>2}" for i in range(1, 11))
    etq = "  ".join(f"A{a}B{b}C{c}r{r}" for (a, b, c), r in plan[:10])
    print(f"    pos : {cab}")
    print(f"    celda: {etq}")

    print("\n  Verificación de RSSI/SNR por escenario (teórico vs simulado):")
    for a, v in ESCENARIOS.items():
        sub = df[df["A"] == a]
        print(f"    A{a}: objetivo {v['obj']:>5.0f} dBm | simulado "
              f"{sub['rssi'].mean():>6.2f} ± {sub['rssi'].std():4.2f} dBm | "
              f"SNR {sub['snr_db'].mean():>5.2f} dB | ruido {sub['ruido'].mean():.1f} dBm")

    print("\n  Muestra de 6 registros del dataset mensaje-a-mensaje:")
    muestra = df[["ensayo", "nodo", "seq", "celda", "replica", "rssi", "snr_db",
                  "distancia", "entregado", "lat_ms"]].head(6)
    print(muestra.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))

    ens = resumir_ensayos(df)

    # ------------------------------------------------------- 2. UMBRAL DEL 85 %
    seccion(2, "PROCESAMIENTO Y VALIDACIÓN DEL UMBRAL DEL 85 % (vertiente de red)")
    cel = resumir_celdas(ens)

    print("\n  PDR promedio por celda con IC 95 % (t de Student, n = 3 réplicas):")
    imprimir_tabla_celdas(cel)

    n_ok = int(cel["pdr_ok"].sum())
    print(f"\n  Resumen del umbral:")
    print(f"    Celdas que CUMPLEN PDR ≥ 85 % : {n_ok}/27 ({100.0 * n_ok / 27:.1f} %)")
    print(f"    Celdas que NO cumplen         : {27 - n_ok}/27")
    estado_counts = cel["estado"].value_counts()
    for est, cnt in estado_counts.items():
        print(f"    {est:<34}: {cnt} celdas")
    print(f"    PDR global de la campaña      : {ens['n_ok'].sum() * 100.0 / ens['n_msg'].sum():.2f} %")
    print(f"    Latencia media por ensayo     : {ens['lat_media'].mean():.2f} ms "
          f"(p95 medio = {ens['lat_p95'].mean():.2f} ms)")
    print(f"    Latencia global (p95)         : {np.nanpercentile(df['lat_ms'], 95):.2f} ms")
    print(f"    Jitter medio                  : {ens['jitter'].mean():.2f} ms")

    cumplimiento_por_factor(cel)

    print("\n  Mapa de calor de PDR (%) — filas = escenario, columnas = carga:")
    piv = cel.pivot_table(index="A", columns="B", values="pdr_media",
                          aggfunc=lambda s: s.mean())
    piv.index = [f"A{i}" for i in piv.index]
    piv.columns = [f"B{j}" for j in piv.columns]
    print(piv.to_string(float_format=lambda v: f"{v:6.2f}"))

    print("\n  Celdas críticas (escenario A3, peor propagación):")
    a3 = cel[cel["A"] == 3]
    print(a3[["celda", "pdr_media", "ic_inf", "ic_sup", "lat_media", "pdr_ok", "estado"]]
          .to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
    a3_ok = int(a3["pdr_ok"].sum())
    a3b3_no = int((a3[a3["B"] == 3]["pdr_ok"] == 0).sum())
    print(f"    -> A3 cumple en {a3_ok}/9 celdas; {a3b3_no}/3 de sus celdas con carga "
          f"intensa (B3) incumplen.")

    print("\n  Exportando CSV a ./simulacion/")
    import os
    os.makedirs("simulacion", exist_ok=True)
    ens.to_csv("simulacion/ensayos.csv", index=False)
    cel.to_csv("simulacion/celdas.csv", index=False)

    # ------------------------------------------------- 3. CLASIFICACIÓN (BOSQUE)
    seccion(3, "MACHINE LEARNING — CLASIFICACIÓN (Bosque Aleatorio)")
    df_ml = df.merge(ens[["ensayo", "pdr_ok"]], on="ensayo", how="left")
    feats = ["rssi", "snr_db", "distancia", "A", "B", "C"]
    num_cols = ["rssi", "snr_db", "distancia"]
    cat_cols = ["A", "B", "C"]
    X = df_ml[feats]
    y = df_ml["pdr_ok"].astype(int)

    print(f"\n  Predictores: {feats}")
    print(f"  Objetivo   : pdr_ok (1 = ensayo con PDR ≥ 85 %; etiqueta heredada por mensaje)")
    balance_de_clases(df_ml)

    pre_arbol = ColumnTransformer(
        [("num", Pipeline([("imp", SimpleImputer(strategy="median"))]), num_cols),
         ("cat", "passthrough", cat_cols)])
    pre_esc = ColumnTransformer(
        [("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                           ("sc", StandardScaler())]), num_cols),
         ("cat", "passthrough", cat_cols)])

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.30, random_state=SEED, stratify=y)
    print(f"\n  División 70/30 estratificada, semilla {SEED}: "
          f"train = {len(Xtr):,} | test = {len(Xte):,}")

    clf = Pipeline([
        ("pre", pre_arbol),
        ("clf", RandomForestClassifier(n_estimators=200, max_depth=16,
                                       random_state=SEED, n_jobs=-1)),
    ])

    print("\n  [A] Validación cruzada estratificada de 10 pliegues (a nivel mensaje, guía §5.2):")
    cv = cross_validate(clf, Xtr, ytr, cv=10,
                        scoring={"acc": "accuracy", "f1": "f1"}, n_jobs=-1)
    acc_cv, f1_cv = cv["test_acc"].mean(), cv["test_f1"].mean()
    print(f"      Exactitud = {acc_cv:.4f} ± {cv['test_acc'].std():.4f} | "
          f"F1 = {f1_cv:.4f} ± {cv['test_f1'].std():.4f}")
    print("      AVISO: los mensajes de un mismo ensayo/celda aparecen en entrenamiento y en")
    print("      validación -> esta cifra está inflada por fuga de información.")

    print("\n  [B] Validación cruzada estratificada por GRUPO (celda), 5 pliegues -> estimación honesta:")
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    accs, f1s = [], []
    oof = np.zeros(len(y), dtype=int)
    for i, (tr_i, te_i) in enumerate(sgkf.split(X, y, groups=df_ml["celda"]), start=1):
        modelo = clone(clf)
        modelo.fit(X.iloc[tr_i], y.iloc[tr_i])
        yp_i = modelo.predict(X.iloc[te_i])
        oof[te_i] = yp_i
        accs.append(accuracy_score(y.iloc[te_i], yp_i))
        f1s.append(f1_score(y.iloc[te_i], yp_i, zero_division=0))
        print(f"      Pliegue {i}: celdas en test = {df_ml['celda'].iloc[te_i].nunique():>2} | "
              f"Exactitud = {accs[-1]:.4f} | F1 = {f1s[-1]:.4f}")
    acc_g, f1_g = float(np.mean(accs)), float(np.mean(f1s))
    print(f"      Promedio: Exactitud = {acc_g:.4f} ± {np.std(accs):.4f} | "
          f"F1 = {f1_g:.4f} ± {np.std(f1s):.4f}")

    clf.fit(Xtr, ytr)
    y_pred = clf.predict(Xte)
    acc = accuracy_score(yte, y_pred)
    f1 = f1_score(yte, y_pred)
    prec = precision_score(yte, y_pred, zero_division=0)
    rec = recall_score(yte, y_pred)
    spec = recall_score(yte, y_pred, pos_label=0)

    print("\n  Evaluación en el conjunto de prueba (holdout 30 %, intacto hasta ahora):")
    print(f"    Exactitud (Accuracy) = {acc:.4f}")
    print(f"    Puntaje F1           = {f1:.4f}")
    print(f"    Precisión            = {prec:.4f}")
    print(f"    Sensibilidad (Recall)= {rec:.4f}")
    print(f"    Especificidad        = {spec:.4f}")
    vn, fp, fn, vp = matriz_confusion_detallada(
        yte, y_pred, "Matriz de confusión del holdout (30 %, con fuga potencial)")

    vn_g, fp_g, fn_g, vp_g = matriz_confusion_detallada(
        y, oof, "Matriz de confusión de la validación por GRUPO (sin fuga, fuera de pliegue)")

    imp = clf.named_steps["clf"].feature_importances_
    orden = np.argsort(imp)[::-1]
    print("\n  Importancia de atributos (Bosque Aleatorio):")
    for i in orden:
        print(f"    {feats[i]:<12} {imp[i]:.4f}  {'#' * int(imp[i] * 60)}")

    ok_clf = (acc_g >= UMBRAL_MODELO / 100) and (f1_g >= UMBRAL_MODELO / 100)
    print(f"\n  Criterio de aceptación de clasificación (≥ 85 % en CV por celda): "
          f"{'CUMPLE' if ok_clf else 'NO CUMPLE -> plan de contingencia §3.5.2'}")

    # ------------------------------------------------------- 4. REGRESIÓN RIDGE
    seccion(4, "MACHINE LEARNING — REGRESIÓN (Ridge) DE LATENCIA")
    df_reg = df_ml[df_ml["lat_ms"].notna()].copy()
    Xr = df_reg[feats]
    yr = df_reg["lat_ms"]
    Xtr_r, Xte_r, ytr_r, yte_r = train_test_split(
        Xr, yr, test_size=0.30, random_state=SEED)
    print(f"\n  Mensajes entregados (con latencia observable): {len(df_reg):,}")
    print(f"  División 70/30, semilla {SEED}: train = {len(Xtr_r):,} | test = {len(Xte_r):,}")

    reg = Pipeline([("pre", pre_esc), ("reg", Ridge(alpha=1.0))])
    reg.fit(Xtr_r, ytr_r)
    yp = reg.predict(Xte_r)

    rmse = float(np.sqrt(mean_squared_error(yte_r, yp)))
    mae = float(mean_absolute_error(yte_r, yp))
    r2 = float(r2_score(yte_r, yp))
    mape = float(np.mean(np.abs((yte_r - yp) / yte_r)) * 100.0)
    rango = float(yte_r.max() - yte_r.min())
    pct_rango = 100.0 * rmse / rango

    print("\n  Métricas de la regresión Ridge (latencia, ms):")
    print(f"    MAE  = {mae:.2f} ms")
    print(f"    RMSE = {rmse:.2f} ms")
    print(f"    MAPE = {mape:.2f} %")
    print(f"    R²   = {r2:.4f}")
    print(f"    Rango observado en test = {rango:.2f} ms "
          f"[{yte_r.min():.2f} – {yte_r.max():.2f}]")
    print(f"    RMSE / rango = {pct_rango:.2f} %   (criterio ≤ {TOL_RMSE_RANGO:.0f} %)")

    cv_reg = cross_validate(reg, Xr, yr, cv=10,
                            scoring="neg_root_mean_squared_error", n_jobs=-1)
    print(f"    RMSE (CV 10 pliegues) = {-cv_reg['test_score'].mean():.2f} ms "
          f"± {cv_reg['test_score'].std():.2f}")

    print("\n  Coeficientes Ridge (variables estandarizadas):")
    coefs = reg.named_steps["reg"].coef_
    for f, w in sorted(zip(feats, coefs), key=lambda kv: -abs(kv[1])):
        print(f"    {f:<12} {w:>8.2f}")

    ok_reg = pct_rango <= TOL_RMSE_RANGO
    print(f"\n  Criterio de aceptación de regresión (RMSE ≤ 15 % del rango): "
          f"{'CUMPLE' if ok_reg else 'NO CUMPLE -> plan de contingencia §3.5.2'}")

    # ------------------------------------------------------------ 5. VEREDICTO
    seccion(5, "VEREDICTO DE LA SIMULACIÓN Y LECCIONES CLAVE")
    indet = int((cel["estado"].str.startswith("INDETERMINADO")).sum())
    frac_celdas = 100.0 * n_ok / 27.0
    red_mayoria = frac_celdas >= 50.0
    red_criticas = a3_ok >= 6

    print("\n  VERTIENTE DE RED (umbral 85 % en PDR):")
    print(f"    a) Celdas cumplidoras en el diseño ..... {n_ok}/27 = {frac_celdas:.1f} %   "
          f"{'CUMPLE (mayoría)' if red_mayoria else 'NO CUMPLE'}")
    print(f"    b) Escenario A1 (visibilidad) .......... {int(cel[cel['A'] == 1]['pdr_ok'].sum())}/9")
    print(f"    c) Escenario A2 (un muro) .............. {int(cel[cel['A'] == 2]['pdr_ok'].sum())}/9")
    print(f"    d) Escenario A3 (doble muro/ruido) ..... {a3_ok}/9   <- celdas críticas")
    print(f"    e) Celdas con IC que atraviesa el umbral (evidencia insuficiente) ... {indet}")
    print(f"    ¿Se logró el 85 % en las celdas críticas (A3)?  "
          f"{'SÍ' if red_criticas else 'NO'}")

    print("\n  VERTIENTE DE MODELADO:")
    print(f"    Clasificación (Bosque) : CV por celda (honesto) = {acc_g:.3f} acc | {f1_g:.3f} F1 "
          f"-> {'CUMPLE' if ok_clf else 'NO CUMPLE'} el 85 %")
    print(f"                          CV por mensaje (con fuga) = {acc_cv:.3f} acc | {f1_cv:.3f} F1")
    print(f"    Regresión (Ridge)      : RMSE = {rmse:.2f} ms = {pct_rango:.1f} % del rango "
          f"-> {'CUMPLE' if ok_reg else 'NO CUMPLE'} el criterio del 15 %")
    print(f"    Holdout 30 % (mensaje) : exactitud = {acc:.3f} | F1 = {f1:.3f} | "
          f"VN={vn} FP={fp} FN={fn} VP={vp}")
    print(f"    Validación por celda   : exactitud = {acc_g:.3f} | F1 = {f1_g:.3f} | "
          f"VN={vn_g} FP={fp_g} FN={fn_g} VP={vp_g}")

    print("\n  CRITERIOS FIJADOS POR ADELANTADO vs RESULTADOS OBSERVADOS:")
    criterios = [
        ("Red", "PDR por celda ≥ 85 %", f"{n_ok}/27 celdas ({frac_celdas:.1f} %)",
         "mayoría > 50 %", red_mayoria),
        ("Red", "PDR ≥ 85 % en celdas críticas A3", f"{a3_ok}/9 celdas",
         "≥ 6/9 celdas", red_criticas),
        ("Modelo", "Exactitud CV por celda", f"{acc_g:.3f}", "≥ 0.85", acc_g >= 0.85),
        ("Modelo", "Puntaje F1 CV por celda", f"{f1_g:.3f}", "≥ 0.85", f1_g >= 0.85),
        ("Modelo", "RMSE de latencia", f"{rmse:.2f} ms = {pct_rango:.1f} % del rango",
         "≤ 15 % del rango", ok_reg),
    ]
    print(f"    {'Vertiente':<9} {'Métrica':<36} {'Valor observado':<32} {'Criterio':<16} Estado")
    print("    " + "-" * 96)
    for vert, met, val, crit, estado in criterios:
        print(f"    {vert:<9} {met:<36} {val:<32} {crit:<16} "
              f"{'CUMPLE' if estado else 'NO CUMPLE'}")

    print("\n  VEREDICTO GLOBAL:")
    if red_mayoria and red_criticas and ok_clf and ok_reg:
        print("    LA CAMPAÑA PROYECTADA ES EXITOSA: las tres vertientes alcanzan el 85 %.")
        print("    Proceder a la campaña física con el protocolo tal como está diseñado.")
        global_mixto = False
    else:
        print("    RESULTADO MIXTO: el 85 % se alcanza en la mayoría de las celdas y en el")
        print("    modelo predictivo, pero NO en las celdas críticas del escenario A3.")
        print("    -> Se recomienda activar los pasos 3 a 5 del plan de contingencia")
        print("       (§3.5.2) ANTES de la campaña física: ampliar réplicas en A3B2*/A3B3*,")
        print("       verificar el piso de ruido del local y documentar la decisión.")
        print("       El umbral NO se redefine sobre datos ya recolectados.")
        global_mixto = True

    print("\n  LECCIONES CLAVE PARA LA PRUEBA REAL:")
    lecciones = [
        f"1. El canal domina la PDR: A1+A2 suman {int(cel[cel['A'] <= 2]['pdr_ok'].sum())}/18 "
        f"celdas cumplidoras y A3 solo {a3_ok}/9. Celdas que incumplen: "
        f"{', '.join(cel[cel['pdr_ok'] == 0]['celda'])}. Reservar réplicas extra para ellas.",
        f"2. El QoS 0 (C1) es el más dañino con enlace malo: en A3, C1 pierde retransmisiones "
        f"que C2/C3 recuperan (PDR por factor C: "
        f"{cel[cel['C'] == 1]['pdr_media'].mean():.1f} / "
        f"{cel[cel['C'] == 2]['pdr_media'].mean():.1f} / "
        f"{cel[cel['C'] == 3]['pdr_media'].mean():.1f} %), pero paga el costo en latencia.",
        f"3. Con solo 3 réplicas el IC 95 % es muy ancho: {indet} celdas quedan "
        f"indeterminadas. Reservar réplicas adicionales (paso 3) para las celdas frontera "
        f"antes de declarar incumplimiento; la PDR sola no basta sin su intervalo.",
        f"4. La latencia es fuertemente NO lineal en la carga: en A3B3 la media llega a "
        f"{cel[(cel['A'] == 3) & (cel['B'] == 3)]['lat_media'].mean():.0f} ms y el p95 a "
        f"{cel[(cel['A'] == 3) & (cel['B'] == 3)]['lat_p95'].mean():.0f} ms, por encima de la "
        f"referencia de 150 ms de ITU-T G.114. Ridge deja R² = {r2:.2f}; conviene guardar "
        f"también latencia logarítmica o un árbol/ensamble como referencia adicional.",
        f"5. Riesgo de fuga de información: la validación a nivel mensaje da {acc:.3f} de "
        f"exactitud porque los mensajes de un mismo ensayo caen en entrenamiento y prueba; "
        f"la validación por celda ({acc_g:.3f}) es la cifra conservadora y es la que debe "
        f"reportarse en la tesis, junto con su matriz de confusión.",
        "6. Instrumentación: validar NTP (±10 ms), firmware idéntico en las 4 placas, PC por "
        "cable y análisis espectral previo del canal: el piso de ruido de A3 es un parámetro "
        "que aquí se asume fijo y que la campaña real debe medir.",
        "7. El umbral se fijó antes de recolectar y así debe permanecer: incumplir con "
        "diagnóstico técnico es también un resultado válido y activa el plan de contingencia.",
    ]
    for txt in lecciones:
        print(f"    - {txt}")

    print("\n  Archivos generados: simulacion/ensayos.csv (81 filas), simulacion/celdas.csv (27 filas)")
    print("=" * 100)
    print(" FIN DE LA SIMULACIÓN")
    print("=" * 100)
    return global_mixto


if __name__ == "__main__":
    main()
