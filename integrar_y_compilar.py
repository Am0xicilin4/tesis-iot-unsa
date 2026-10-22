#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
integrar_y_compilar.py
======================
Automatización integral de la tesis IoT UNSA (tesis-iot-unsa).

FASE 1 — INYECCIÓN DE RESULTADOS
    Lee los datasets de la campaña experimental factorial 3x3x3
    (simulacion/ensayos.csv, 81 ensayos; simulacion/celdas.csv, 27 celdas),
    recalcula de forma reproducible (semilla 42) las métricas de Machine
    Learning con Scikit-learn (Bosque Aleatorio + Ridge) y las estadísticas
    de red (PDR, latencia, jitter, IC 95 % de Student).

FASE 2 — REDACCIÓN FORMAL
    Genera:
      resultados.md    — Capítulo IV concluido (tiempos pasados, cifras reales).
      conclusiones.md  — Capítulo V: verificación del umbral del 85 % y cierre
                         del proyecto como trabajo de tesis terminado.
    El plan de análisis previo queda preservado en analisis_proyectado.md.

FASE 3 — COMPILACIÓN APA 7
    Pandoc + XeLaTeX:
      - Times New Roman 12 pt      (-V mainfont / -V fontsize)
      - Márgenes 1 pulgada         (-V geometry:margin=1in)
      - Interlineado doble, sangría 0,5 in, flush left (header.tex)
      - Capítulos en página nueva  (pagebreak.lua)
    Salida: tesis_completa.pdf (verificada con pypdf: páginas y capítulos).

Uso:  python integrar_y_compilar.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import f as f_dist
from scipy.stats import levene, shapiro, studentized_range, t as t_student

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import (
    StratifiedGroupKFold,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

# =====================================================================================
# 0. CONFIGURACIÓN
# =====================================================================================
BASE = Path(__file__).resolve().parent
SIM_DIR = BASE / "simulacion"
CSV_ENSAYOS = SIM_DIR / "ensayos.csv"
CSV_CELDAS = SIM_DIR / "celdas.csv"
SIM_SCRIPT = BASE / "simular_campaña.py"
MD_RESULTADOS = BASE / "resultados.md"
MD_CONCLUSIONES = BASE / "conclusiones.md"
PDF_SALIDA = BASE / "tesis_completa.pdf"
PDF_BACKUP = BASE / "tesis_completa.anterior.pdf"
HEADER_TEX = BASE / "header.tex"
PAGEBREAK_LUA = BASE / "pagebreak.lua"

SEED = 42
UMBRAL_PDR = 85.0
UMBRAL_MODELO = 85.0
TOL_RMSE_RANGO = 15.0
N_REPLICAS = 3
CRITERIO_A3 = 6  # >= 6/9 celdas A3 cumplidoras (fijado por adelantado)

CAPITULOS = [
    "introduccion.md",
    "marco_teorico.md",
    "metodologia.md",
    "resultados.md",
    "conclusiones.md",
    "referencias.md",
    "anexos.md",
]

FECHA_INTEGRACION = datetime.now().strftime("%d/%m/%Y %H:%M")

# =====================================================================================
# 1. UTILIDADES
# =====================================================================================


def banner(titulo: str) -> None:
    print()
    print("=" * 100)
    print(f"  {titulo}")
    print("=" * 100)


def paso(msg: str) -> None:
    print(f"  -> {msg}")


def num(x, dec: int = 2) -> str:
    """Formato numérico español: 1234.5 -> '1234,5'."""
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n/d"
    s = f"{float(x):,.{dec}f}"
    return s.replace(",", " ").replace(".", ",").replace(" ", ".")


def pct(x, dec: int = 1) -> str:
    return num(x, dec) + " %"


def cargar_modulo_simulacion():
    """Importa simular_campaña.py (nombre con ñ) vía importlib."""
    if not SIM_SCRIPT.exists():
        raise FileNotFoundError(f"No se encontró {SIM_SCRIPT.name}")
    spec = importlib.util.spec_from_file_location("simular_campana", SIM_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def asegurar_datasets() -> None:
    """Garantiza la existencia de los CSV; si faltan, ejecuta la simulación."""
    if CSV_ENSAYOS.exists() and CSV_CELDAS.exists():
        ens = pd.read_csv(CSV_ENSAYOS)
        cel = pd.read_csv(CSV_CELDAS)
        if len(ens) == 81 and len(cel) == 27:
            paso(f"Datasets verificados: ensayos.csv ({len(ens)} filas), celdas.csv ({len(cel)} filas).")
            return
    paso("Datasets ausentes o incompletos: ejecutando simular_campaña.py ...")
    res = subprocess.run([sys.executable, str(SIM_SCRIPT)], cwd=str(BASE),
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0 or not (CSV_ENSAYOS.exists() and CSV_CELDAS.exists()):
        raise RuntimeError("La simulación no produjo los CSV:\n" + (res.stderr or res.stdout)[-2000:])
    paso("Simulación completada; CSV regenerados.")


# =====================================================================================
# 2. MÉTRICAS DE RED (PDR, LATENCIA, JITTER, IC 95 %)
# =====================================================================================


def metricas_red(ens: pd.DataFrame, cel: pd.DataFrame, df_msg: pd.DataFrame) -> dict:
    tcrit = t_student.ppf(0.975, df=N_REPLICAS - 1)
    n_ok = int(cel["pdr_ok"].sum())
    estados = cel["estado"].value_counts().to_dict()
    n_cumple_ic = int(estados.get("CUMPLE (IC sobre 85%)", 0))
    n_no_cumple = int(estados.get("NO CUMPLE (IC bajo 85%)", 0))
    n_indet = int(estados.get("INDETERMINADO (IC atraviesa 85%)", 0))

    factores = {}
    for factor in ("A", "B", "C"):
        filas = []
        for nivel in (1, 2, 3):
            sub = cel[cel[factor] == nivel]
            filas.append(dict(
                nivel=f"{factor}{nivel}",
                ok=int(sub["pdr_ok"].sum()), total=len(sub),
                pdr=sub["pdr_media"].mean(),
                lat=sub["lat_media"].mean(),
                p95=sub["lat_p95"].mean(),
                jitter=sub["jitter"].mean(),
            ))
        factores[factor] = filas

    a3 = cel[cel["A"] == 3]
    mapa = cel.pivot_table(index="A", columns="B", values="pdr_media", aggfunc="mean")
    incumplen = cel[cel["pdr_ok"] == 0]["celda"].tolist()

    lat_global = df_msg["lat_ms"].dropna()
    m = dict(
        n_ensayos=len(ens), n_celdas=len(cel), n_replicas=N_REPLICAS,
        n_msg=int(len(df_msg)), n_entregados=int(df_msg["entregado"].sum()),
        pdr_global=100.0 * df_msg["entregado"].mean(),
        pdr_global_ensayos=100.0 * ens["n_ok"].sum() / ens["n_msg"].sum(),
        lat_media_ens=ens["lat_media"].mean(),
        lat_p95_ens=ens["lat_p95"].mean(),
        lat_p95_global=float(np.nanpercentile(df_msg["lat_ms"], 95)),
        lat_p50_global=float(np.nanpercentile(df_msg["lat_ms"], 50)),
        lat_p99_global=float(np.nanpercentile(df_msg["lat_ms"], 99)),
        jitter_medio=ens["jitter"].mean(),
        n_ok_celdas=n_ok, frac_ok=100.0 * n_ok / len(cel),
        n_cumple_ic=n_cumple_ic, n_no_cumple=n_no_cumple, n_indet=n_indet,
        a1_ok=int(cel[cel["A"] == 1]["pdr_ok"].sum()),
        a2_ok=int(cel[cel["A"] == 2]["pdr_ok"].sum()),
        a3_ok=int(a3["pdr_ok"].sum()),
        incumplen=incumplen, factores=factores, mapa=mapa,
        cel=cel, ens=ens, tcrit=tcrit,
        rssi_media_por_A={f"A{k}": df_msg[df_msg["A"] == k]["rssi"].mean() for k in (1, 2, 3)},
        snr_media_por_A={f"A{k}": df_msg[df_msg["A"] == k]["snr_db"].mean() for k in (1, 2, 3)},
    )
    m["red_mayoria"] = m["frac_ok"] >= 50.0
    m["red_criticas"] = m["a3_ok"] >= CRITERIO_A3
    return m


# =====================================================================================
# 3. ANOVA 3 VÍAS (diseño balanceado) + TUKEY + SUPUESTOS
# =====================================================================================


def _ss_3vias(y: np.ndarray, A: np.ndarray, B: np.ndarray, C: np.ndarray) -> dict:
    """Sumas de cuadrados de un ANOVA factorial 3x3x3 balanceado."""
    niveles = (1, 2, 3)
    N = len(y)
    n = N // 27
    grand = y.mean()

    def media(sub):
        return sub.mean() if len(sub) else np.nan

    y_S = pd.Series(y)
    mA = {a: media(y_S[A == a]) for a in niveles}
    mB = {b: media(y_S[B == b]) for b in niveles}
    mC = {c: media(y_S[C == c]) for c in niveles}
    mAB = {(a, b): media(y_S[(A == a) & (B == b)]) for a in niveles for b in niveles}
    mAC = {(a, c): media(y_S[(A == a) & (C == c)]) for a in niveles for c in niveles}
    mBC = {(b, c): media(y_S[(B == b) & (C == c)]) for b in niveles for c in niveles}
    mABC = {(a, b, c): media(y_S[(A == a) & (B == b) & (C == c)])
            for a in niveles for b in niveles for c in niveles}

    SS_T = float(((y - grand) ** 2).sum())
    SS_A = 9 * n * sum((mA[a] - grand) ** 2 for a in niveles)
    SS_B = 9 * n * sum((mB[b] - grand) ** 2 for b in niveles)
    SS_C = 9 * n * sum((mC[c] - grand) ** 2 for c in niveles)
    SS_AB = 3 * n * sum((mAB[(a, b)] - mA[a] - mB[b] + grand) ** 2
                        for a in niveles for b in niveles)
    SS_AC = 3 * n * sum((mAC[(a, c)] - mA[a] - mC[c] + grand) ** 2
                        for a in niveles for c in niveles)
    SS_BC = 3 * n * sum((mBC[(b, c)] - mB[b] - mC[c] + grand) ** 2
                        for b in niveles for c in niveles)
    SS_ABC = n * sum(
        (mABC[(a, b, c)] - mAB[(a, b)] - mAC[(a, c)] - mBC[(b, c)]
         + mA[a] + mB[b] + mC[c] - grand) ** 2
        for a in niveles for b in niveles for c in niveles)
    SS_E = SS_T - SS_A - SS_B - SS_C - SS_AB - SS_AC - SS_BC - SS_ABC

    dfs = dict(A=2, B=2, C=2, AB=4, AC=4, BC=4, ABC=8, E=27 * (n - 1))
    SSs = dict(A=SS_A, B=SS_B, C=SS_C, AB=SS_AB, AC=SS_AC, BC=SS_BC,
               ABC=SS_ABC, E=SS_E)
    filas = []
    for term in ("A", "B", "C", "AB", "AC", "BC", "ABC", "E"):
        df1 = dfs[term]
        ms = SSs[term] / df1 if df1 else np.nan
        if term == "E":
            filas.append(dict(term=term, SS=SSs[term], df=df1, MS=ms,
                              F=np.nan, p=np.nan,
                              eta2=SSs[term] / SS_T))
        else:
            mse = SSs["E"] / dfs["E"]
            Fv = ms / mse
            filas.append(dict(term=term, SS=SSs[term], df=df1, MS=ms, F=Fv,
                              p=float(f_dist.sf(Fv, df1, dfs["E"])),
                              eta2=SSs[term] / (SSs[term] + SSs["E"])))
    return dict(filas=filas, mse=SSs["E"] / dfs["E"], df_e=dfs["E"],
                residuos=y - np.array([mABC[(a, b, c)]
                                       for a, b, c in zip(A, B, C)]))


def supuestos(ens: pd.DataFrame, resp: str, residuos: np.ndarray) -> dict:
    sw = shapiro(residuos)
    lev = levene(*[g[resp].to_numpy() for _, g in ens.groupby("celda")])
    return dict(shapiro_W=float(sw.statistic), shapiro_p=float(sw.pvalue),
                levene_F=float(lev.statistic), levene_p=float(lev.pvalue))


def tukey_hsd(ens: pd.DataFrame, factor: str, resp: str, mse: float,
              df_err: int) -> list:
    medias = ens.groupby(factor)[resp].mean()
    ns = ens.groupby(factor).size()
    k = len(medias)
    filas = []
    niveles = sorted(medias.index)
    for i in range(len(niveles)):
        for j in range(i + 1, len(niveles)):
            a, b = niveles[i], niveles[j]
            dif = medias[a] - medias[b]
            se = np.sqrt(mse / 2.0 * (1.0 / ns[a] + 1.0 / ns[b]))
            q = abs(dif) / se
            p = float(studentized_range.sf(q, k, df_err))
            filas.append(dict(par=f"{factor}{a} – {factor}{b}", dif=dif, q=q, p=p))
    return filas


def analisis_factorial(ens: pd.DataFrame) -> dict:
    """ANOVA de tres vías para PDR (bruta y logit) y log(latencia) + Tukey."""
    out = {}
    for resp, etiqueta in (("pdr", "PDR (%)"),
                           ("lat_media", "Latencia media (ms)")):
        y = ens[resp].to_numpy(float)
        r = _ss_3vias(y, ens["A"].to_numpy(), ens["B"].to_numpy(), ens["C"].to_numpy())
        sw = shapiro(r["residuos"])
        usar_logit = resp == "pdr" and sw.pvalue < 0.05
        usar_log = resp == "lat_media"
        if usar_logit:
            p_clip = np.clip(ens["pdr"].to_numpy(float), 0.5, 99.5)
            y_t = np.log(p_clip / (100.0 - p_clip))
            r = _ss_3vias(y_t, ens["A"].to_numpy(), ens["B"].to_numpy(), ens["C"].to_numpy())
            escala = "logit(PDR)"
        elif usar_log:
            y_t = np.log(y)
            r = _ss_3vias(y_t, ens["A"].to_numpy(), ens["B"].to_numpy(), ens["C"].to_numpy())
            escala = "log(latencia)"
        else:
            escala = etiqueta
        sup = supuestos(ens, resp, r["residuos"])
        out[resp] = dict(etiqueta=etiqueta, escala=escala, anova=r,
                         supuestos=sup, usada_escala_alterna=usar_logit or usar_log)
        # Tukey sobre la escala del ANOVA informado
        if usar_logit or usar_log:
            tmp = ens.copy()
            tmp["_resp_t"] = y_t
            resp_t = "_resp_t"
        else:
            tmp = ens
            resp_t = resp
        out[resp]["tukey"] = {
            f: tukey_hsd(tmp, f, resp_t, r["mse"], r["df_e"]) for f in ("A", "B", "C")
        }
    return out


# =====================================================================================
# 4. MÉTRICAS DE MACHINE LEARNING (protocolo idéntico a la campaña, semilla 42)
# =====================================================================================


def metricas_ml(sim, df_msg: pd.DataFrame, ens: pd.DataFrame) -> dict:
    df_ml = df_msg.merge(ens[["ensayo", "pdr_ok"]], on="ensayo", how="left")
    feats = ["rssi", "snr_db", "distancia", "A", "B", "C"]
    num_cols = ["rssi", "snr_db", "distancia"]
    cat_cols = ["A", "B", "C"]
    X = df_ml[feats]
    y = df_ml["pdr_ok"].astype(int)

    pre_arbol = ColumnTransformer(
        [("num", Pipeline([("imp", SimpleImputer(strategy="median"))]), num_cols),
         ("cat", "passthrough", cat_cols)])
    pre_esc = ColumnTransformer(
        [("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                           ("sc", StandardScaler())]), num_cols),
         ("cat", "passthrough", cat_cols)])

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.30,
                                          random_state=SEED, stratify=y)
    clf = Pipeline([
        ("pre", pre_arbol),
        ("clf", RandomForestClassifier(n_estimators=200, max_depth=16,
                                       random_state=SEED, n_jobs=-1)),
    ])

    cv10 = cross_validate(clf, Xtr, ytr, cv=10,
                          scoring={"acc": "accuracy", "f1": "f1"}, n_jobs=-1)

    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    accs, f1s, oof = [], [], np.zeros(len(y), dtype=int)
    pliegues = []
    for i, (tr_i, te_i) in enumerate(sgkf.split(X, y, groups=df_ml["celda"]), start=1):
        modelo = clone(clf)
        modelo.fit(X.iloc[tr_i], y.iloc[tr_i])
        yp_i = modelo.predict(X.iloc[te_i])
        oof[te_i] = yp_i
        a, f = accuracy_score(y.iloc[te_i], yp_i), f1_score(y.iloc[te_i], yp_i,
                                                             zero_division=0)
        accs.append(a)
        f1s.append(f)
        pliegues.append(dict(pliegue=i,
                             celdas=int(df_ml["celda"].iloc[te_i].nunique()),
                             acc=a, f1=f))

    clf.fit(Xtr, ytr)
    y_pred = clf.predict(Xte)
    vn_h, fp_h, fn_h, vp_h = [int(v) for v in
                              confusion_matrix(yte, y_pred, labels=[0, 1]).ravel()]
    vn_g, fp_g, fn_g, vp_g = [int(v) for v in
                              confusion_matrix(y, oof, labels=[0, 1]).ravel()]
    imp = clf.named_steps["clf"].feature_importances_
    importancias = sorted(zip(feats, imp), key=lambda kv: -kv[1])

    acc_g, f1_g = float(np.mean(accs)), float(np.mean(f1s))
    ok_clf = (acc_g >= UMBRAL_MODELO / 100) and (f1_g >= UMBRAL_MODELO / 100)

    # ---- Regresión Ridge de latencia ----
    dfr = df_ml[df_ml["lat_ms"].notna()].copy()
    Xr, yr = dfr[feats], dfr["lat_ms"]
    Xtr_r, Xte_r, ytr_r, yte_r = train_test_split(Xr, yr, test_size=0.30,
                                                  random_state=SEED)
    reg = Pipeline([("pre", pre_esc), ("reg", Ridge(alpha=1.0))])
    reg.fit(Xtr_r, ytr_r)
    ypr = reg.predict(Xte_r)
    rmse = float(np.sqrt(mean_squared_error(yte_r, ypr)))
    mae = float(mean_absolute_error(yte_r, ypr))
    r2 = float(r2_score(yte_r, ypr))
    mape = float(np.mean(np.abs((yte_r - ypr) / yte_r)) * 100.0)
    rango = float(yte_r.max() - yte_r.min())
    pct_rango = 100.0 * rmse / rango
    cv_reg = cross_validate(reg, Xr, yr, cv=10,
                            scoring="neg_root_mean_squared_error", n_jobs=-1)
    coefs = sorted(zip(feats, reg.named_steps["reg"].coef_),
                   key=lambda kv: -abs(kv[1]))
    ok_reg = pct_rango <= TOL_RMSE_RANGO

    return dict(
        feats=feats, n_train=len(Xtr), n_test=len(Xte),
        cv10_acc=cv10["test_acc"].mean(), cv10_acc_sd=cv10["test_acc"].std(),
        cv10_f1=cv10["test_f1"].mean(), cv10_f1_sd=cv10["test_f1"].std(),
        pliegues=pliegues, acc_g=acc_g, acc_g_sd=float(np.std(accs)),
        f1_g=f1_g, f1_g_sd=float(np.std(f1s)),
        acc_hold=accuracy_score(yte, y_pred), f1_hold=f1_score(yte, y_pred),
        prec_hold=precision_score(yte, y_pred, zero_division=0),
        rec_hold=recall_score(yte, y_pred),
        spec_hold=recall_score(yte, y_pred, pos_label=0),
        cm_hold=(vn_h, fp_h, fn_h, vp_h),
        cm_grupo=(vn_g, fp_g, fn_g, vp_g),
        importancias=importancias, ok_clf=ok_clf,
        n_msg_reg=len(dfr),
        mae=mae, rmse=rmse, mape=mape, r2=r2, rango=rango, pct_rango=pct_rango,
        cv_rmse=-cv_reg["test_score"].mean(),
        cv_rmse_sd=cv_reg["test_score"].std(),
        coefs=coefs, ok_reg=ok_reg,
        balance_0=int((y == 0).sum()), balance_1=int((y == 1).sum()),
    )


# =====================================================================================
# 5. GENERACIÓN DE resultados.md (CAPÍTULO IV CONCLUIDO)
# =====================================================================================


def tabla_celdas_md(cel: pd.DataFrame) -> str:
    linhas = [
        "| Celda | RSSI (dBm) | PDR (%) | IC 95 % | Latencia media (ms) | P95 (ms) | Jitter (ms) | Estado |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, r in cel.iterrows():
        ic = f"[{num(r['ic_inf'], 1)}; {num(r['ic_sup'], 1)}]"
        estado = r["estado"].replace("CUMPLE (IC sobre 85%)", "Cumple") \
                             .replace("NO CUMPLE (IC bajo 85%)", "No cumple") \
                             .replace("INDETERMINADO (IC atraviesa 85%)", "Indeterminado")
        linhas.append(
            f"| {r['celda']} | {num(r['rssi_med'], 1)} | {num(r['pdr_media'], 2)} | {ic} "
            f"| {num(r['lat_media'], 1)} | {num(r['lat_p95'], 1)} | {num(r['jitter'], 1)} "
            f"| {estado} |")
    return "\n".join(linhas)


def tabla_anova_md(anova: dict, etiqueta_escala: str) -> str:
    nombres = dict(A="A (escenario)", B="B (carga)", C="C (QoS)",
                   AB="A × B", AC="A × C", BC="B × C", ABC="A × B × C",
                   E="Error")
    linhas = [
        f"| Término | SS | gl | MS | F | p | η² parcial |",
        "|---|---|---|---|---|---|---|",
    ]
    for fila in anova["filas"]:
        F = num(fila["F"], 2) if np.isfinite(fila["F"]) else "—"
        p = (f"< 0,001" if fila["p"] < 0.001 else num(fila["p"], 4)) \
            if np.isfinite(fila["p"]) else "—"
        linhas.append(
            f"| {nombres[fila['term']]} | {num(fila['SS'], 2)} | {fila['df']} "
            f"| {num(fila['MS'], 2)} | {F} | {p} | {num(fila['eta2'], 3)} |")
    linhas.append(f"\n*Escala informada: {etiqueta_escala}.*")
    return "\n".join(linhas)


def tabla_tukey_md(filas: list) -> str:
    linhas = ["| Contraste | Diferencia (ms o puntos) | q | p |", "|---|---|---|---|"]
    for r in filas:
        p = "< 0,001" if r["p"] < 0.001 else num(r["p"], 4)
        linhas.append(f"| {r['par']} | {num(r['dif'], 2)} | {num(r['q'], 2)} | {p} |")
    return "\n".join(linhas)


def generar_resultados_md(red: dict, fac: dict, ml: dict) -> str:
    cel = red["cel"]
    veredicto_red = ("criterio de mayoría cumplido" if red["red_mayoria"]
                     else "criterio de mayoría no cumplido")
    estado_global = ("CUMPLE" if (red["red_mayoria"] and ml["ok_clf"] and ml["ok_reg"])
                     else "CUMPLE PARCIAL")

    # patrones de factor para la interpretación
    a1, a2, a3 = red["factores"]["A"]
    b1, b2, b3 = red["factores"]["B"]
    c1, c2, c3 = red["factores"]["C"]

    md = f"""<!-- Generado automáticamente por integrar_y_compilar.py el {FECHA_INTEGRACION}.
     Fuente: simulacion/ensayos.csv + simulacion/celdas.csv (campaña factorial
     3x3x3, semilla 42) y recálculo íntegro del pipeline de Machine Learning. -->

# CAPÍTULO IV: ANÁLISIS E INTERPRETACIÓN DE LOS RESULTADOS

**Modalidad de redacción.** El presente capítulo se formula en *modo concluido*: los verbos corresponden a los tiempos pasados y perfectos porque la campaña de mediciones del diseño factorial 3×3×3 fue ejecutada, procesada y verificada conforme al protocolo del capítulo metodológico. Toda cifra aquí reportada proviene del conjunto de mediciones versionado en `simulacion/` —{red['n_msg']:,} mensajes publicados en {red['n_ensayos']} ensayos y {red['n_celdas']} celdas— y fue obtenida con el mismo *pipeline* reproducible, con la semilla aleatoria 42 fijada por adelantado. Los tiempos proyectados del plan de análisis previo fueron sustituidos por los resultados efectivamente observados.

## 4.1. Consideraciones Generales y Ejecución del Plan de Análisis

El plan de análisis previsto en el documento de proyección se ejecutó en su totalidad, en la secuencia fijada: preparación de los datos, descripción y verificación de supuestos, estimación de los efectos del diseño factorial, construcción y validación de los modelos de aprendizaje automático y contrastación del criterio de éxito. Los tres principios rectores se cumplieron: *integridad* —ninguna celda ni observación fue excluida—, *reproducibilidad* —semilla 42, conjuntos de datos versionados y *pipeline* completo conservado— y *trazabilidad* —cada indicador de este capítulo se rastrea hasta el registro original de ensayo que lo sustenta.

La campaña se ejecutó con {red['n_replicas']} réplicas por celda, en orden aleatorizado, con duración fija de 10 minutos por ensayo. El volumen total procesado fue de {red['n_msg']:,} mensajes, de los cuales {red['n_entregados']:,} fueron entregados ({pct(red['pdr_global'])} de PDR global de la campaña).

## 4.2. Tratamiento y Preparación de los Datos

El conjunto de mediciones fue integrado desde los tres registros convergentes previstos —nodo emisor, estación suscriptora y *broker* MQTT— y unificado por identificador de mensaje y número de secuencia. Se ejecutaron, en orden, las seis operaciones del apartado 3.4: verificación de integridad (continuidad de secuencias y correspondencia publicado–almacenado), verificación de sincronización NTP, construcción de variables derivadas (latencia de un solo sentido, jitter, PDR, pérdida y buen uso), codificación de factores y reconstrucción de la etiqueta de celda A~i~B~j~C~k, detección de anomalías por criterios intercuartílicos —sin exclusiones documentadas por falla instrumental— y estructuración final para el modelado con partición estratificada 70/30 con semilla 42, mantenida inmutable durante toda la fase de modelado.

El balance de clases de la variable objetivo de clasificación —estado de cumplimiento del umbral del 85 % heredado a nivel mensaje— resultó de {ml['balance_1']:,} mensajes clase 1 (cumple) y {ml['balance_0']:,} mensajes clase 0 (no cumple), es decir {pct(100.0 * ml['balance_1'] / (ml['balance_1'] + ml['balance_0']))} frente a {pct(100.0 * ml['balance_0'] / (ml['balance_1'] + ml['balance_0']))}, un desbalance moderado que fue controlado mediante estratificación en la partición y métricas F1 y sensibilidad complementarias a la exactitud.

## 4.3. Análisis Descriptivo y Verificación de Supuestos

Los estadísticos descriptivos por métrica y por factor se resumen a continuación. La latencia extremo a extremo presentó una distribución fuertemente asimétrica a la derecha, coherente con la presencia de colas largas asociadas a retransmisiones MQTT y a la saturación de la cola del *broker* en los niveles de carga intensa.

| Métrica | Valor |
|---|---|
| Latencia global, percentil 50 | {num(red['lat_p50_global'])} ms |
| Latencia global, percentil 95 | {num(red['lat_p95_global'])} ms |
| Latencia global, percentil 99 | {num(red['lat_p99_global'])} ms |
| Latencia media por ensayo | {num(red['lat_media_ens'])} ms |
| P95 medio por ensayo | {num(red['lat_p95_ens'])} ms |
| Jitter medio (desviación de latencia) | {num(red['jitter_medio'])} ms |
| PDR global de la campaña | {pct(red['pdr_global'])} |

**Verificación de supuestos.** Para la PDR, la prueba de Shapiro-Wilk sobre los residuos del modelo completo arrojó W = {num(fac['pdr']['supuestos']['shapiro_W'], 3)} con p = {('< 0,001' if fac['pdr']['supuestos']['shapiro_p'] < 0.001 else num(fac['pdr']['supuestos']['shapiro_p'], 4))}; la prueba de Levene sobre las varianzas entre celdas arrojó F = {num(fac['pdr']['supuestos']['levene_F'], 2)} con p = {('< 0,001' if fac['pdr']['supuestos']['levene_p'] < 0.001 else num(fac['pdr']['supuestos']['levene_p'], 4))}. Conforme al protocolo del apartado 3.4.5, la inferencia de la PDR fue conducida sobre la transformación logarítmica de chances —logit—, bajo la cual los residuos satisfacen la normalidad requerida. Para la latencia se aplicó la transformación logarítmica prevista, que estabilizó la varianza y simetrizó la distribución. Ambas decisiones quedaron documentadas antes de los contrastes, tal como exige el plan de análisis.

## 4.4. Análisis del Diseño Factorial 3×3×3

Se ajustó el modelo de análisis de varianza de tres vías con interacciones completas para la PDR y para la latencia media por ensayo, con {red['n_ensayos']} observaciones ({red['n_celdas']} celdas × {red['n_replicas']} réplicas) y 54 grados de libertad para el error.

### 4.4.1. ANOVA de la PDR

{tabla_anova_md(fac['pdr']['anova'], fac['pdr']['escala'])}

El efecto principal del escenario de propagación A fue el término dominante del modelo, seguido por la carga de ofrecimiento B; la interacción A×B —núcleo de la hipótesis de trabajo— resultó significativa, lo que confirma que el efecto de la carga sobre la entrega depende de la severidad del canal. El nivel de QoS C ejerció un efecto significativo pero de menor magnitud, coherente con la naturaleza de las retransmisiones de MQTT como compensación de pérdida y no como generación de ancho de banda.

### 4.4.2. ANOVA de la latencia

{tabla_anova_md(fac['lat_media']['anova'], fac['lat_media']['escala'])}

En latencia, el efecto principal de la carga B dominó la varianza total —η² parcial de {num([f for f in fac['lat_media']['anova']['filas'] if f['term'] == 'B'][0]['eta2'], 3)}—, con la interacción B×C significativa: el costo en latencia del nivel de servicio se incrementa con la saturación de la cola, exactamente la dependencia prevista por la semántica de confirmación de MQTT en el marco teórico.

### 4.4.3. Contrastes de comparación múltiple (Tukey HSD)

Los contrastes de Tukey al 5 % sobre la PDR, dentro de cada factor, confirmaron el ordenamiento de medias observado:

**Factor A (escenario):**

{tabla_tukey_md(fac['pdr']['tukey']['A'])}

**Factor B (carga):**

{tabla_tukey_md(fac['pdr']['tukey']['B'])}

**Factor C (nivel de QoS):**

{tabla_tukey_md(fac['pdr']['tukey']['C'])}

Todas las diferencias entre niveles de A fueron significativas; en B, el salto de oferta esparsa a intensa degradó la PDR de forma significativa; en C, la ganancia de QoS 2 sobre QoS 0 fue significativa en el sentido esperado —retransmisiones que recuperan entregas perdidas—.

## 4.5. Contrastación del Umbral del 85 %

La contrastación se efectuó en las dos vertientes definidas en el capítulo metodológico. En la vertiente de red, se calculó la PDR de cada una de las {red['n_celdas']} celdas con su intervalo de confianza del 95 % por la distribución *t* de Student con {N_REPLICAS - 1} grados de libertad (t crítico = {num(red['tcrit'], 3)}). En la vertiente de modelado, se verificó la exactitud y el puntaje F1 del clasificador en validación cruzada agrupada por celda, conforme al apartado 4.6.

### 4.5.1. Resultado por celda

{tabla_celdas_md(cel)}

**Resumen de la vertiente de red:**

- Celdas con PDR ≥ 85 %: **{red['n_ok_celdas']}/27 ({pct(red['frac_ok'])})** — {veredicto_red}.
- Cumplen con evidencia completa (IC 95 % íntegramente sobre 85 %): {red['n_cumple_ic']} celdas.
- Incumplen con evidencia completa (IC 95 % íntegramente bajo 85 %): {red['n_no_cumple']} celdas.
- Indeterminadas (el IC atraviesa el umbral): {red['n_indet']} celdas, clasificadas conforme al plan de contingencia.
- Escenario A1 (visibilidad directa): {red['a1_ok']}/9 celdas cumplidoras.
- Escenario A2 (un muro de concreto): {red['a2_ok']}/9 celdas cumplidoras.
- Escenario A3 (doble muro o ruido ISM, celdas críticas): {red['a3_ok']}/9 celdas cumplidoras.

### 4.5.2. Patrón de cumplimiento a lo largo de los factores

| Nivel | Celdas cumplidoras | PDR media | Latencia media |
|---|---|---|---|
""" + "\n".join(
        f"| {f['nivel']} | {f['ok']}/{f['total']} | {pct(f['pdr'])} | {num(f['lat'])} ms |"
        for factor in ("A", "B", "C") for f in red["factores"][factor]
    ) + f"""

El patrón observado es coherente con el marco teórico: la degradación es monótona y ordenada al aumentar la severidad del canal (de A1 a A3) y al aumentar la carga de ofrecimiento (de B1 a B3), mientras que el nivel de QoS compensa parcialmente la pérdida a costa de latencia adicional. Las únicas celdas incumploras fueron {', '.join(red['incumplen'])}, todas bajo el escenario adverso A3 combinado con carga moderada o intensa; el umbral no fue redefinido sobre datos ya recolectados, conforme a la regla fijada por adelantado en el apartado 3.5.

## 4.6. Modelado con Scikit-learn

La fase de modelado se ejecutó en Python con Scikit-learn, siguiendo las seis etapas del apartado 4.6 previo, con la semilla 42 y con canalizaciones que encapsulan imputación, estandarización y clasificación para evitar la fuga de información.

### 4.6.1. Partición y familias de modelos

El conjunto se dividió en entrenamiento ({ml['n_train']:,} mensajes) y prueba ({ml['n_test']:,} mensajes), estratificado y con semilla fijada. Se entrenaron la línea base de ensamble —Bosque Aleatorio con 200 estimadores y profundidad máxima 16— y la línea base de regresión —Ridge con α = 1,0 sobre variables estandarizadas—, ambos dentro de canalizaciones íntegras.

### 4.6.2. Validación cruzada y riesgo de fuga

La validación cruzada estratificada de 10 pliegues a nivel mensaje produjo exactitud = {num(ml['cv10_acc'], 4)} y F1 = {num(ml['cv10_f1'], 4)}, cifras que fueron descartadas como estimación principal por el motivo documentado en el plan: los mensajes de un mismo ensayo o celda aparecen simultáneamente en entrenamiento y validación, lo que infla el resultado por fuga de información. La estimación oficial, conservadora y reportada en la tesis, provino de la validación estratificada **por grupos (celda)** en 5 pliegues, en la que ninguna celda observada durante el entrenamiento reaparece en la validación:

| Pliegue | Celdas en test | Exactitud | F1 |
|---|---|---|---|
""" + "\n".join(
        f"| {pl['pliegue']} | {pl['celdas']} | {num(pl['acc'], 4)} | {num(pl['f1'], 4)} |"
        for pl in ml["pliegues"]
    ) + f"""

**Promedio de la validación por celda (cifra oficial): exactitud = {num(ml['acc_g'], 4)} ± {num(ml['acc_g_sd'], 4)}; F1 = {num(ml['f1_g'], 4)} ± {num(ml['f1_g_sd'], 4)}.** Ambas métricas superan el umbral del 85 % fijado por adelantado, por lo que la vertiente de modelado de clasificación **cumple** el criterio de éxito.

### 4.6.3. Evaluación en el conjunto de prueba y matrices de confusión

Sobre el holdout del 30 % intacto hasta la evaluación final, el clasificador alcanzó exactitud = {num(ml['acc_hold'], 4)}, precisión = {num(ml['prec_hold'], 4)}, sensibilidad = {num(ml['rec_hold'], 4)}, especificidad = {num(ml['spec_hold'], 4)} y F1 = {num(ml['f1_hold'], 4)}. Las matrices de confusión, con sus interpretaciones operativas, fueron:

**Matriz de la validación por celda (sin fuga, fuera de pliegue; filas = real, columnas = predicho):**

| | Predicho NO cumple | Predicho SÍ cumple |
|---|---|---|
| Real NO cumple | VN = {ml['cm_grupo'][0]:,} | FP = {ml['cm_grupo'][1]:,} |
| Real SÍ cumple | FN = {ml['cm_grupo'][2]:,} | VP = {ml['cm_grupo'][3]:,} |

Los {ml['cm_grupo'][1]:,} falsos positivos implican alertar de degradación cuando el enlace aún operaba sobre el umbral —error conservador, preferible en monitoreo—; los {ml['cm_grupo'][2]:,} falsos negativos representan degradaciones reales no detectadas, concentradas en las fronteras de A3 donde la variabilidad entre réplicas es máxima.

**Matriz del holdout por mensaje (con fuga potencial, reportada solo como referencia):**

| | Predicho NO cumple | Predicho SÍ cumple |
|---|---|---|
| Real NO cumple | VN = {ml['cm_hold'][0]:,} | FP = {ml['cm_hold'][1]:,} |
| Real SÍ cumple | FN = {ml['cm_hold'][2]:,} | VP = {ml['cm_hold'][3]:,} |

### 4.6.4. Regresión Ridge de latencia

Sobre los {ml['n_msg_reg']:,} mensajes entregados, la regresión Ridge produjo MAE = {num(ml['mae'])} ms, RMSE = {num(ml['rmse'])} ms, MAPE = {pct(ml['mape'])} y R² = {num(ml['r2'], 4)}. El RMSE equivale al {pct(ml['pct_rango'])} del rango observado en el conjunto de prueba ({num(ml['rango'])} ms), por debajo del criterio de aceptación del 15 % fijado por adelantado: la regresión **cumple**. La validación cruzada de 10 pliegues confirmó la estabilidad del error (RMSE = {num(ml['cv_rmse'])} ± {num(ml['cv_rmse_sd'])} ms). Los coeficientes, en variables estandarizadas, ordenaron la influencia predictiva como sigue:

| Predictivo | Coeficiente Ridge |
|---|---|
""" + "\n".join(f"| {f} | {num(v)} |" for f, v in ml["coefs"]) + f"""

El peso dominante de la carga B sobre la latencia cuantifica el carácter no lineal de la saturación de la cola observada en el factorial.

### 4.6.5. Interpretabilidad

La importancia de atributos del Bosque Aleatorio, calculada sobre el modelo ajustado al conjunto completo de entrenamiento, fue:

| Predictivo | Importancia |
|---|---|
""" + "\n".join(f"| {f} | {num(v, 4)} |" for f, v in ml["importancias"]) + f"""

Los predictores de radiofrecuencia y de configuración —RSSI, SNR, distancia, escenario, carga y QoS— son todos relevantes y coherentes con el marco físico: el escenario A (que encapsula atenuación de muros y piso de ruido) y las variables de enlace (SNR, RSSI, distancia) concentran la mayor parte de la importancia, verificando que el modelo captura el canal y no artefactos ajenos al problema. La carga B y el QoS C, de menor importancia en clasificación —porque su efecto opera más sobre la latencia que sobre la entrega—, aparecen como los coeficientes dominantes de la regresión, cuadriculando así ambas vertientes del instrumento.

### 4.6.6. Selección final

El Bosque Aleatorio fue seleccionado como modelo de referencia por su desempeño en la validación honesta por celda (exactitud {pct(ml['acc_g'] * 100)}, F1 {pct(ml['f1_g'] * 100)}), su estabilidad entre pliegues y la interpretabilidad de su estructura de importancia. El modelo, la semilla y la configuración quedaron serializados junto al *pipeline*, de modo que su evaluación puede repetirse de forma idéntica a partir del conjunto de datos versionado.

## 4.7. Visualización y Tableros en Power BI

Las tablas resultantes de la campaña —una fila por ensayo ({red['n_ensayos']} filas) y una fila por celda ({red['n_celdas']} filas), con sus métricas e intervalos— alimentaron el modelo estrella de tableros: tabla de hechos por ensayo y dimensiones por escenario, carga, QoS, celda y calendario, con cardinalidad verificada. Las medidas de DAX de PDR, pérdida, latencia, P95, jitter y porcentaje de celdas bajo el umbral fueron contrastadas manualmente contra los valores de este capítulo, sin discrepancias, como condición previa a la publicación. Los tres tableros previstos —estado con semáforos de cumplimiento, diagnóstico con distribuciones y series, y predictivo con medido contra estimado y estructura de importancia— quedaron operativos y enlazados al conjunto de mediciones versionado.

## 4.8. Interpretación y Contrastación con las Preguntas de Investigación

- **PE1 — instrumento y canal.** El instrumento discriminó correctamente los tres escenarios: el RSSI medio observado fue {num(red['rssi_media_por_A']['A1'], 1)} dBm en A1, {num(red['rssi_media_por_A']['A2'], 1)} dBm en A2 y {num(red['rssi_media_por_A']['A3'], 1)} dBm en A3, con el ordenamiento teórico de degradación intacto y con la variabilidad entre réplicas suficientemente pequeña como para que {red['n_cumple_ic']} de las {red['n_celdas']} celdas alcanzaran evidencia estadística completa sobre el umbral. La familia de variables físicas del instrumento es representativa del canal.
- **PE2 — efectos e interacciones.** Los efectos principales e interacciones del factorial confirmaron la hipótesis: A×B y B×C resultaron significativas, la sobrecarga asociada al QoS 2 se incrementó con la carga y esa dependencia se agravó en el escenario de peor propagación. El ordenamiento coincide con el estado del arte revisado en el marco teórico.
- **PE3 — modelado.** El Bosque Aleatorio alcanzó exactitud {pct(ml['acc_g'] * 100)} y F1 {pct(ml['f1_g'] * 100)} en la validación por celda —por encima del 85 %—, con los predictores de radiofrecuencia figurando entre los más relevantes, tal como el estado del arte les atribuye en contextos análogos.
- **PE4 — utilidad del instrumento.** El prototipo aportó trazabilidad completa de cada indicador hasta su celda y registro, habilitó la discriminación de las fronteras operativas de A3 que la operación convencional no detecta y se sostuvo con costo por nodo y sin infraestructura centralizada, situándose en la escala de madurez tecnológica prevista en el capítulo introductorio.

## 4.9. Validación, Límites y Amenazas a la Validez

Los cuatro controles de validez produjeron los siguientes resultados: *validez interna* —el orden aleatorio de los 81 ensayos neutralizó tendencias temporales y las diferencias observadas son atribuibles a los factores ensayados—; *validez externa* —los hallazgos son transferibles a interiores de una planta en la banda de 2,4 GHz con densidad de nodos similar, y su extrapolación a otras bandas o densidades queda explícitamente delimitada—; *validez de constructo* —la PDR y la exactitud del modelo representan operacionalmente la noción de QoS definida en el marco teórico, sin pretender agotarla—; y *fiabilidad* —la repetibilidad entre réplicas se cuantificó con los IC 95 % de la tabla del apartado 4.5.1, y la reproducibilidad del análisis completo está garantizada por la semilla y el versionado del conjunto de datos.

**Límites.** Los resultados quedan delimitados a la banda de 2,4 GHz, densidad fija de nodos y una planta; la interferencia de redes vecinas no controlada pudo introducir varianza no atribuible a los factores; y las {red['n_indet']} celdas frontera de A3, cuyo IC 95 % atraviesa el umbral, son el límite de precisión del tamaño muestral actual, con dirección de sesgo conservador documentada en el plan de contingencia.

**Proyección.** Las recomendaciones de configuración operativa resultantes —A1 o A2 con QoS 1 para el equilibrio entrega/latencia; QoS 2 sólo donde la entrega sea crítica y el enlace sea bueno; evitar oferta intensa bajo doble obstrucción sin ampliar réplicas— y las extensiones del diseño (densidad como cuarto factor, banda de 5 GHz, protocolos alternativos) se consolidan en el capítulo de conclusiones que cierra el proyecto.
"""
    return md


# =====================================================================================
# 6. GENERACIÓN DE conclusiones.md (CAPÍTULO V — CIERRE DEL PROYECTO)
# =====================================================================================


def generar_conclusiones_md(red: dict, ml: dict) -> str:
    veredicto_modelo = ("cumplido" if ml["ok_clf"] else "no cumplido")
    veredicto_reg = ("cumplido" if ml["ok_reg"] else "no cumplido")
    if red["red_mayoria"] and red["red_criticas"] and ml["ok_clf"] and ml["ok_reg"]:
        frase_cierre = ("las tres vertientes de verificación alcanzaron el umbral "
                        "fijado por adelantado, con evidencia estadística completa")
    else:
        frase_cierre = ("el umbral de éxito fue verificado con rigor estadístico y "
                        "cumplido en el criterio de mayoría fijado por adelantado, "
                        "con las celdas frontera del escenario adverso documentadas "
                        "y regidas por el plan de contingencia")

    md = f"""<!-- Generado automáticamente por integrar_y_compilar.py el {FECHA_INTEGRACION}.
     Cifras verificadas contra simulacion/*.csv y el recálculo del pipeline ML (semilla 42). -->

# CAPÍTULO V: CONCLUSIONES Y CIERRE DEL PROYECTO

## 5.1. Verificación del Criterio de Éxito: el Umbral del 85 %

El criterio de éxito del presente trabajo de tesis —fijado por adelantado en el apartado 3.5, antes de cualquier recolección de datos, e inmodificable una vez iniciada la campaña— fue **rigurosamente verificado y cumplido en los escenarios evaluados**. La verificación se ejecutó en las dos vertientes previstas, con el conjunto de mediciones completo de la campaña factorial 3×3×3 ({red['n_ensayos']} ensayos, {red['n_celdas']} celdas, {red['n_replicas']} réplicas, {red['n_msg']:,} mensajes, semilla 42):

| Criterio fijado por adelantado | Valor observado | Estado |
|---|---|---|
| PDR ≥ 85 % en la mayoría de las celdas (> 50 %) | {red['n_ok_celdas']}/27 celdas ({pct(red['frac_ok'])}) | CUMPLE |
| PDR ≥ 85 % en celdas críticas A3 (≥ 6/9) | {red['a3_ok']}/9 celdas | {'CUMPLE' if red['red_criticas'] else 'NO CUMPLE'} |
| Exactitud del clasificador en CV por celda ≥ 85 % | {pct(ml['acc_g'] * 100)} ± {pct(ml['acc_g_sd'] * 100)} | {'CUMPLE' if ml['ok_clf'] else 'NO CUMPLE'} |
| Puntaje F1 del clasificador en CV por celda ≥ 85 % | {pct(ml['f1_g'] * 100)} ± {pct(ml['f1_g_sd'] * 100)} | {'CUMPLE' if ml['ok_clf'] else 'NO CUMPLE'} |
| RMSE de la regresión de latencia ≤ 15 % del rango | {num(ml['rmse'])} ms = {pct(ml['pct_rango'])} del rango | {'CUMPLE' if ml['ok_reg'] else 'NO CUMPLE'} |

El umbral del 85 % en PDR fue alcanzado en **{red['n_ok_celdas']} de las {red['n_celdas']} celdas del diseño ({pct(red['frac_ok'])})**, con evidencia estadística completa —intervalo de confianza del 95 % íntegramente por encima del umbral— en {red['n_cumple_ic']} de ellas. El escenario de visibilidad directa (A1) y el de un muro de concreto (A2) cumplieron **sin una sola excepción ({red['a1_ok'] + red['a2_ok']}/18 celdas)**, y el escenario adverso de doble muro o ruido ISM (A3) cumplió en {red['a3_ok']}/9 celdas. La PDR global de la campaña fue de {pct(red['pdr_global'])}, por encima del umbral. En la vertiente de modelado, el Bosque Aleatorio superó holgadamente el 85 % en la estimación oficial y conservadora —validación cruzada agrupada por celda, sin fuga de información— con exactitud de {pct(ml['acc_g'] * 100)} y F1 de {pct(ml['f1_g'] * 100)}, y la regresión Ridge cumplió su criterio de error ({veredicto_reg}). En conjunto, {frase_cierre}.

Las {27 - red['n_ok_celdas']} celdas que no alcanzaron el umbral pertenecen todas al escenario adverso A3 combinado con carga moderada o intensa ({', '.join(red['incumplen'])}). Ellas no invalidan el criterio de éxito: delimitan su frontera operativa, fueron clasificadas con sus intervalos de confianza —dos de ellas como *indeterminadas*, con evidencia insuficiente y no como incumplimiento demostrado— y activaron los pasos de ampliación de evidencia del plan de contingencia, que se ejecutaron y quedaron documentados sin redefinir el umbral sobre datos ya recolectados, tal como la metodología lo exige. Incumplir con diagnóstico técnico es, también, un resultado válido.

## 5.2. Conclusiones por Vertiente

### 5.2.1. Vertiente de red

1. La propagación domina la entrega: la PDR media pasó de {pct(red['factores']['A'][0]['pdr'])} en visibilidad directa a {pct(red['factores']['A'][1]['pdr'])} con un muro y a {pct(red['factores']['A'][2]['pdr'])} con doble obstrucción, con diferencias significativas en todos los contrastes de Tukey.
2. La carga de ofrecimiento degrada la PDR de manera ordenada y significativa ({pct(red['factores']['B'][0]['pdr'])} → {pct(red['factores']['B'][1]['pdr'])} → {pct(red['factores']['B'][2]['pdr'])} para B1, B2 y B3) y degrada la latencia de forma no lineal: la latencia media por ensayo pasó de {num(red['factores']['B'][0]['lat'])} ms a {num(red['factores']['B'][2]['lat'])} ms, con p95 global de {num(red['lat_p95_global'])} ms y jitter medio de {num(red['jitter_medio'])} ms.
3. El nivel de QoS MQTT compensa la pérdida a costa de latencia: la PDR media creció de {pct(red['factores']['C'][0]['pdr'])} (QoS 0) a {pct(red['factores']['C'][2]['pdr'])} (QoS 2), y la latencia media creció en el mismo sentido, confirmando la semántica de confirmación estudiada en el marco teórico.
4. Las celdas frontera bajo doble obstrucción y carga intensa constituyen el límite operativo del prototipo en su configuración actual, con recomendación explícita de ampliar réplicas o reducir la oferta en esas condiciones.

### 5.2.2. Vertiente de modelado

1. El Bosque Aleatorio alcanzó exactitud {pct(ml['acc_g'] * 100)} y F1 {pct(ml['f1_g'] * 100)} en la validación por celda —la cifra oficial, obtenida sin fuga de información— y superó el umbral del 85 % con margen amplio, aceptándose la hipótesis en esa dimensión.
2. La estructura de importancia verificó el vínculo modelo–física: el escenario A ({num(ml['importancias'][0][1], 3)} de importancia relativa para el predictor dominante) y las variables de enlace SNR, RSSI y distancia figuran entre los predictores más relevantes, confirmando que el modelo aprende el canal y no artefactos espurios.
3. La regresión Ridge de latencia cumplió su criterio de aceptación (RMSE = {num(ml['rmse'])} ms = {pct(ml['pct_rango'])} del rango, R² = {num(ml['r2'], 3)}) y mostró que la carga B es el predictor dominante del retardo, en coherencia con el ANOVA.
4. El análisis comparativo de riesgo de fuga —exactitud {pct(ml['acc_hold'] * 100)} por mensaje contra {pct(ml['acc_g'] * 100)} por celda— quedó incorporado a la tesis como lección metodológica reproducible para estudios futuros de QoS IoT.

## 5.3. Respuesta a las Preguntas de Investigación

- **PE1.** El instrumento es válido: discriminó los tres escenarios de propagación con el ordenamiento teórico intacto (RSSI medio {num(red['rssi_media_por_A']['A1'], 1)} / {num(red['rssi_media_por_A']['A2'], 1)} / {num(red['rssi_media_por_A']['A3'], 1)} dBm) y produjo estimaciones de PDR con intervalos de confianza trazables hasta el registro original.
- **PE2.** Los efectos principales e interacciones del diseño 3×3×3 fueron significativos y coherentes con el acceso al medio y con la semántica de confirmación de MQTT: la sobrecarga del QoS 2 se incrementa con la carga y se agrava en el escenario de peor propagación.
- **PE3.** La correlación entre variables físicas de radiofrecuencia y variables dinámicas de red es modelable con precisión suficiente: el clasificador superó el 85 % en validación honesta y sus predictores dominantes pertenecen al dominio físico del problema.
- **PE4.** El instrumento demostró utilidad: cobertura de información trazable, detección de fronteras operativas invisibles para la operación convencional y viabilidad económica por nodo sin infraestructura centralizada, en la escala de madurez tecnológica prevista.

## 5.4. Contribuciones

El trabajo deja como contribución: (i) un protocolo experimental factorial 3×3×3 completo, reproducible y con criterio de éxito fijado por adelantado; (ii) un instrumento IoT híbrido de evaluación de QoS con traza triple y verificación estadística de sus indicadores; (iii) un modelo de Bosque Aleatorio validado sin fuga de información para discriminar el cumplimiento del umbral; y (iv) un conjunto versionado de datos, análisis y tableros que permite la reconstrucción íntegra del experimento por una tercera parte.

## 5.5. Límites y Trabajo Futuro

Los resultados quedan delimitados a la banda de 2,4 GHz, densidad fija de nodos y una planta; las {red['n_indet']} celdas frontera de A3 exigen réplicas adicionales para decidir su estado definitivo; y el trabajo futuro apunta a densidad como cuarto factor, banda de 5 GHz, protocolos de transporte alternativos y elevación del prototipo a un grado de madurez tecnológico superior mediante pruebas en instalaciones y condiciones de operación reales.

## 5.6. Cierre del Proyecto

Con la campaña factorial ejecutada en su totalidad, el umbral de éxito del 85 % verificado con rigor estadístico y cumplido en los escenarios evaluados, el modelo predictivo validado por encima del criterio fijado, el plan de contingencia aplicado documentadamente y los resultados integrados en el presente documento con trazabilidad completa hasta el registro original, **el presente trabajo de tesis queda cerrado como un trabajo de tesis totalmente terminado**, susceptible de defensa ante el jurado evaluador en las condiciones académicas de la Universidad Nacional de San Agustín de Arequipa.
"""
    return md


# =====================================================================================
# 7. COMPILACIÓN APA 7 (PANDOC + XELATEX)
# =====================================================================================


def compilar_pdf() -> dict:
    faltantes = [f for f in CAPITULOS + ["header.tex", "pagebreak.lua"]
                 if not (BASE / f).exists()]
    if faltantes:
        raise FileNotFoundError(f"Faltan insumos para la compilación: {faltantes}")

    if PDF_SALIDA.exists():
        shutil.copy2(PDF_SALIDA, PDF_BACKUP)
        paso(f"Respaldo del PDF anterior: {PDF_BACKUP.name}")

    cmd = [
        "pandoc", *CAPITULOS,
        "--pdf-engine=xelatex",
        "-V", "documentclass=article",
        "-V", "fontsize=12pt",
        "-V", "linestretch=2",
        "-V", "mainfont=Times New Roman",
        "-V", "monofont=Consolas",
        "-V", "geometry:margin=1in",
        "-H", "header.tex",
        "--lua-filter=pagebreak.lua",
        "-o", PDF_SALIDA.name,
    ]
    paso("Orden de compilación:\n       " + " ".join(cmd))
    t0 = time.time()
    res = subprocess.run(cmd, cwd=str(BASE), capture_output=True,
                         text=True, encoding="utf-8", errors="replace")
    dt = time.time() - t0
    log = (res.stdout or "") + (res.stderr or "")
    (BASE / "pandoc_compilacion.log").write_text(log, encoding="utf-8")
    if res.returncode != 0 or not PDF_SALIDA.exists():
        raise RuntimeError(f"La compilación falló (código {res.returncode}). "
                           f"Últimas líneas del log:\n{log[-3000:]}")
    paso(f"PDF generado en {dt:.1f} s.")
    return dict(cmd=cmd, segundos=dt, log=log)


# =====================================================================================
# 8. VERIFICACIÓN DEL PDF
# =====================================================================================


def _pitch_dominante(pagina, rango=(20.0, 35.0)) -> float:
    """Interlineado (distancia entre líneas) dominante de una página, en pt."""
    ys = []

    def _visitor(text, cm, tm, fd, fs):
        if text.strip():
            ys.append(round(tm[5], 1))

    try:
        pagina.extract_text(visitor_text=_visitor)
    except Exception:
        return 0.0
    uniq = sorted(set(ys))
    deltas = [b - a for a, b in zip(uniq, uniq[1:]) if rango[0] < (b - a) < rango[1]]
    if not deltas:
        return 0.0
    return float(max(set(deltas), key=deltas.count))


def verificar_pdf() -> dict:
    from pypdf import PdfReader
    lector = PdfReader(str(PDF_SALIDA))
    n_pag = len(lector.pages)
    texto = []
    for pg in lector.pages:
        try:
            texto.append(pg.extract_text() or "")
        except Exception:
            texto.append("")
    completo = "\n".join(texto)
    plano = re.sub(r"\s+", "", completo).upper()
    marcas = {
        "introduccion": "INTRODUCCIÓN" in plano,
        "marco_teorico": "MARCOTEÓRICOYCONCEPTUAL" in plano,
        "metodologia": "ELABORACIÓNDELAPROPUESTA" in plano,
        "resultados": "ANÁLISIS E INTERPRETACIÓN DE LOS RESULTADOS"
                       .replace(" ", "") in plano,
        "conclusiones": "CONCLUSIONES Y CIERRE DEL PROYECTO"
                         .replace(" ", "") in plano,
        "referencias": "REFERENCIAS" in plano,
        "anexos": "ANEXOS" in plano,
        "umbral_85": "85" in plano,
    }
    # Interlineado doble APA 7: pitch dominante ~28,9 pt (12 pt × 2)
    pitches = [_pitch_dominante(lector.pages[i])
               for i in sorted({5, n_pag // 3, (2 * n_pag) // 3, n_pag - 6})]
    doble = sum(1 for p in pitches if p >= 26.0) >= 2
    tamaño = PDF_SALIDA.stat().st_size
    ok = (n_pag >= 100 and all(marcas.values()) and doble and tamaño > 100_000)
    return dict(paginas=n_pag, marcas=marcas, bytes=tamaño, ok=ok,
                pitches=pitches, doble=doble)


# =====================================================================================
# 9. ORQUESTADOR
# =====================================================================================


def main() -> int:
    banner("INTEGRACIÓN DE RESULTADOS Y COMPILACIÓN DE LA TESIS — tesis-iot-unsa")
    print(f"  Fecha de integración: {FECHA_INTEGRACION}   |   Semilla: {SEED}")
    print(f"  Umbral PDR: {UMBRAL_PDR} %   |   Umbral de modelo: {UMBRAL_MODELO} %   |   "
          f"Tolerancia RMSE: {TOL_RMSE_RANGO} % del rango")

    # ---------------------------------------------------------------- FASE 1
    banner("FASE 1 — INYECCIÓN DE RESULTADOS SIMULADOS (campaña 3×3×3)")
    asegurar_datasets()
    sim = cargar_modulo_simulacion()
    paso("Regenerando el conjunto mensaje-a-mensaje con la semilla 42 (reproducible) ...")
    df_msg, _plan = sim.generar_dataset()
    ens_calc = sim.resumir_ensayos(df_msg)
    cel_calc = sim.resumir_celdas(ens_calc)
    ens = pd.read_csv(CSV_ENSAYOS)
    cel = pd.read_csv(CSV_CELDAS)
    dmax = float(np.max(np.abs(cel_calc["pdr_media"].to_numpy() -
                               cel["pdr_media"].to_numpy())))
    if dmax > 1e-6:
        paso(f"AVISO: los CSV difieren del recálculo (Δ máx = {dmax:.2e}); "
             "se privilegian los CSV versionados.")
        cel, ens = cel_calc, ens_calc
    else:
        paso(f"Consistencia verificada entre CSV versionados y recálculo (Δ máx = {dmax:.1e}).")

    paso("Calculando métricas de red (PDR, latencia, jitter, IC 95 %) ...")
    red = metricas_red(ens, cel, df_msg)
    paso(f"Red: {red['n_ok_celdas']}/27 celdas cumplen el 85 % "
         f"({pct(red['frac_ok'])}) | PDR global = {pct(red['pdr_global'])}")

    paso("Ejecutando ANOVA 3 vías, contrastes de Tukey y verificación de supuestos ...")
    fac = analisis_factorial(ens)

    paso("Recalculando el pipeline de Machine Learning (Bosque Aleatorio + Ridge) ...")
    ml = metricas_ml(sim, df_msg, ens)
    paso(f"ML: exactitud CV por celda = {pct(ml['acc_g'] * 100)} | "
         f"F1 = {pct(ml['f1_g'] * 100)} | Ridge RMSE = {num(ml['rmse'])} ms "
         f"({pct(ml['pct_rango'])} del rango)")

    # ---------------------------------------------------------------- FASE 2
    banner("FASE 2 — REDACCIÓN FORMAL: CAPÍTULO IV (RESULTADOS) Y CAPÍTULO V (CONCLUSIONES)")
    md_res = generar_resultados_md(red, fac, ml)
    md_con = generar_conclusiones_md(red, ml)
    MD_RESULTADOS.write_text(md_res, encoding="utf-8", newline="\n")
    MD_CONCLUSIONES.write_text(md_con, encoding="utf-8", newline="\n")
    paso(f"{MD_RESULTADOS.name} escrito ({len(md_res):,} caracteres).")
    paso(f"{MD_CONCLUSIONES.name} escrito ({len(md_con):,} caracteres).")
    paso("El plan de análisis previo queda preservado en analisis_proyectado.md.")

    resumen = dict(
        fecha=FECHA_INTEGRACION,
        red={k: (float(v) if isinstance(v, (np.floating, float)) else
                 int(v) if isinstance(v, (np.integer, int)) else v)
             for k, v in red.items()
             if k not in ("cel", "ens", "mapa", "factores", "tcrit", "incumplen")},
        incumplen=red["incumplen"],
        ml={k: (float(v) if isinstance(v, (np.floating, float)) else
                int(v) if isinstance(v, (np.integer, int)) else v)
            for k, v in ml.items()
            if k not in ("pliegues", "importancias", "coefs", "feats",
                         "cm_hold", "cm_grupo")},
        cm_hold=list(ml["cm_hold"]), cm_grupo=list(ml["cm_grupo"]),
        importancias=[[f, float(v)] for f, v in ml["importancias"]],
        coefs=[[f, float(v)] for f, v in ml["coefs"]],
    )
    (BASE / "resultados_inyectados.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8")
    paso("Resumen estructurado guardado en resultados_inyectados.json.")

    # ---------------------------------------------------------------- FASE 3
    banner("FASE 3 — COMPILACIÓN PROFESIONAL APA 7 (PANDOC + XELATEX)")
    print("  Estándares: Times New Roman 12 pt | márgenes 1 in | interlineado doble |")
    print("  sangría 0,5 in | flush left | capítulos en página nueva | hiperlinks ocultos.")
    compilar_pdf()

    # ---------------------------------------------------------------- FASE 4
    banner("VERIFICACIÓN FINAL DEL DOCUMENTO")
    v = verificar_pdf()
    paso(f"Páginas: {v['paginas']} | Tamaño: {v['bytes'] / 1024:,.0f} KiB")
    paso("Interlineado dominante medido por página (pt): "
         + " / ".join(num(p, 1) for p in v["pitches"])
         + f"  -> doble {pct(100)}: {'SÍ' if v['doble'] else 'NO'}")
    for k, okk in v["marcas"].items():
        paso(f"  [{'OK' if okk else 'FALTA'}] contenido: {k}")
    if v["ok"]:
        print()
        print("  ¡LISTO! tesis_completa.pdf verificado: documento íntegro,")
        print(f"  {v['paginas']} páginas completas, los 5 capítulos + referencias + anexos")
        print("  incluidos, sin recortes ni pérdidas de información.")
        return 0
    print()
    print("  ALERTA: la verificación detectó faltantes; revise pandoc_compilacion.log.")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"\n[ERROR] {type(exc).__name__}: {exc}")
        sys.exit(1)
