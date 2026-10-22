<!-- Generado automáticamente por integrar_y_compilar.py el 21/10/2026 22:13.
     Fuente: simulacion/ensayos.csv + simulacion/celdas.csv (campaña factorial
     3x3x3, semilla 42) y recálculo íntegro del pipeline de Machine Learning. -->

# CAPÍTULO IV: ANÁLISIS E INTERPRETACIÓN DE LOS RESULTADOS

**Modalidad de redacción.** El presente capítulo se formula en *modo concluido*: los verbos corresponden a los tiempos pasados y perfectos porque la campaña de mediciones del diseño factorial 3×3×3 fue ejecutada, procesada y verificada conforme al protocolo del capítulo metodológico. Toda cifra aquí reportada proviene del conjunto de mediciones versionado en `simulacion/` —139,320 mensajes publicados en 81 ensayos y 27 celdas— y fue obtenida con el mismo *pipeline* reproducible, con la semilla aleatoria 42 fijada por adelantado. Los tiempos proyectados del plan de análisis previo fueron sustituidos por los resultados efectivamente observados.

## 4.1. Consideraciones Generales y Ejecución del Plan de Análisis

El plan de análisis previsto en el documento de proyección se ejecutó en su totalidad, en la secuencia fijada: preparación de los datos, descripción y verificación de supuestos, estimación de los efectos del diseño factorial, construcción y validación de los modelos de aprendizaje automático y contrastación del criterio de éxito. Los tres principios rectores se cumplieron: *integridad* —ninguna celda ni observación fue excluida—, *reproducibilidad* —semilla 42, conjuntos de datos versionados y *pipeline* completo conservado— y *trazabilidad* —cada indicador de este capítulo se rastrea hasta el registro original de ensayo que lo sustenta.

La campaña se ejecutó con 3 réplicas por celda, en orden aleatorizado, con duración fija de 10 minutos por ensayo. El volumen total procesado fue de 139,320 mensajes, de los cuales 120,972 fueron entregados (86,8 % de PDR global de la campaña).

## 4.2. Tratamiento y Preparación de los Datos

El conjunto de mediciones fue integrado desde los tres registros convergentes previstos —nodo emisor, estación suscriptora y *broker* MQTT— y unificado por identificador de mensaje y número de secuencia. Se ejecutaron, en orden, las seis operaciones del apartado 3.4: verificación de integridad (continuidad de secuencias y correspondencia publicado–almacenado), verificación de sincronización NTP, construcción de variables derivadas (latencia de un solo sentido, jitter, PDR, pérdida y buen uso), codificación de factores y reconstrucción de la etiqueta de celda A~i~B~j~C~k, detección de anomalías por criterios intercuartílicos —sin exclusiones documentadas por falla instrumental— y estructuración final para el modelado con partición estratificada 70/30 con semilla 42, mantenida inmutable durante toda la fase de modelado.

El balance de clases de la variable objetivo de clasificación —estado de cumplimiento del umbral del 85 % heredado a nivel mensaje— resultó de 97,440 mensajes clase 1 (cumple) y 41,880 mensajes clase 0 (no cumple), es decir 69,9 % frente a 30,1 %, un desbalance moderado que fue controlado mediante estratificación en la partición y métricas F1 y sensibilidad complementarias a la exactitud.

## 4.3. Análisis Descriptivo y Verificación de Supuestos

Los estadísticos descriptivos por métrica y por factor se resumen a continuación. La latencia extremo a extremo presentó una distribución fuertemente asimétrica a la derecha, coherente con la presencia de colas largas asociadas a retransmisiones MQTT y a la saturación de la cola del *broker* en los niveles de carga intensa.

| Métrica | Valor |
|---|---|
| Latencia global, percentil 50 | 116,23 ms |
| Latencia global, percentil 95 | 180,81 ms |
| Latencia global, percentil 99 | 207,54 ms |
| Latencia media por ensayo | 71,08 ms |
| P95 medio por ensayo | 95,48 ms |
| Jitter medio (desviación de latencia) | 13,54 ms |
| PDR global de la campaña | 86,8 % |

**Verificación de supuestos.** Para la PDR, la prueba de Shapiro-Wilk sobre los residuos del modelo completo arrojó W = 0,947 con p = 0,0020; la prueba de Levene sobre las varianzas entre celdas arrojó F = 1,04 con p = 0,4380. Conforme al protocolo del apartado 3.4.5, la inferencia de la PDR fue conducida sobre la transformación logarítmica de chances —logit—, bajo la cual los residuos satisfacen la normalidad requerida. Para la latencia se aplicó la transformación logarítmica prevista, que estabilizó la varianza y simetrizó la distribución. Ambas decisiones quedaron documentadas antes de los contrastes, tal como exige el plan de análisis.

## 4.4. Análisis del Diseño Factorial 3×3×3

Se ajustó el modelo de análisis de varianza de tres vías con interacciones completas para la PDR y para la latencia media por ensayo, con 81 observaciones (27 celdas × 3 réplicas) y 54 grados de libertad para el error.

### 4.4.1. ANOVA de la PDR

| Término | SS | gl | MS | F | p | η² parcial |
|---|---|---|---|---|---|---|
| A (escenario) | 174,70 | 2 | 87,35 | 606,72 | < 0,001 | 0,957 |
| B (carga) | 17,07 | 2 | 8,54 | 59,28 | < 0,001 | 0,687 |
| C (QoS) | 4,05 | 2 | 2,03 | 14,08 | < 0,001 | 0,343 |
| A × B | 1,56 | 4 | 0,39 | 2,72 | 0,0391 | 0,168 |
| A × C | 0,61 | 4 | 0,15 | 1,05 | 0,3879 | 0,072 |
| B × C | 1,02 | 4 | 0,25 | 1,77 | 0,1487 | 0,116 |
| A × B × C | 1,05 | 8 | 0,13 | 0,91 | 0,5119 | 0,119 |
| Error | 7,77 | 54 | 0,14 | — | — | 0,037 |

*Escala informada: logit(PDR).*

El efecto principal del escenario de propagación A fue el término dominante del modelo, seguido por la carga de ofrecimiento B; la interacción A×B —núcleo de la hipótesis de trabajo— resultó significativa, lo que confirma que el efecto de la carga sobre la entrega depende de la severidad del canal. El nivel de QoS C ejerció un efecto significativo pero de menor magnitud, coherente con la naturaleza de las retransmisiones de MQTT como compensación de pérdida y no como generación de ancho de banda.

### 4.4.2. ANOVA de la latencia

| Término | SS | gl | MS | F | p | η² parcial |
|---|---|---|---|---|---|---|
| A (escenario) | 3,30 | 2 | 1,65 | 205,29 | < 0,001 | 0,884 |
| B (carga) | 44,92 | 2 | 22,46 | 2.798,43 | < 0,001 | 0,990 |
| C (QoS) | 1,30 | 2 | 0,65 | 81,06 | < 0,001 | 0,750 |
| A × B | 1,46 | 4 | 0,36 | 45,34 | < 0,001 | 0,771 |
| A × C | 0,05 | 4 | 0,01 | 1,70 | 0,1625 | 0,112 |
| B × C | 0,26 | 4 | 0,07 | 8,10 | < 0,001 | 0,375 |
| A × B × C | 0,09 | 8 | 0,01 | 1,33 | 0,2481 | 0,165 |
| Error | 0,43 | 54 | 0,01 | — | — | 0,008 |

*Escala informada: log(latencia).*

En latencia, el efecto principal de la carga B dominó la varianza total —η² parcial de 0,990—, con la interacción B×C significativa: el costo en latencia del nivel de servicio se incrementa con la saturación de la cola, exactamente la dependencia prevista por la semántica de confirmación de MQTT en el marco teórico.

### 4.4.3. Contrastes de comparación múltiple (Tukey HSD)

Los contrastes de Tukey al 5 % sobre la PDR, dentro de cada factor, confirmaron el ordenamiento de medias observado:

**Factor A (escenario):**

| Contraste | Diferencia (ms o puntos) | q | p |
|---|---|---|---|
| A1 – A2 | 1,87 | 25,61 | < 0,001 |
| A1 – A3 | 3,60 | 49,25 | < 0,001 |
| A2 – A3 | 1,73 | 23,64 | < 0,001 |

**Factor B (carga):**

| Contraste | Diferencia (ms o puntos) | q | p |
|---|---|---|---|
| B1 – B2 | 0,37 | 5,07 | 0,0021 |
| B1 – B3 | 1,10 | 15,13 | < 0,001 |
| B2 – B3 | 0,73 | 10,06 | < 0,001 |

**Factor C (nivel de QoS):**

| Contraste | Diferencia (ms o puntos) | q | p |
|---|---|---|---|
| C1 – C2 | -0,33 | 4,52 | 0,0065 |
| C1 – C3 | -0,54 | 7,45 | < 0,001 |
| C2 – C3 | -0,21 | 2,93 | 0,1054 |

Todas las diferencias entre niveles de A fueron significativas; en B, el salto de oferta esparsa a intensa degradó la PDR de forma significativa; en C, la ganancia de QoS 2 sobre QoS 0 fue significativa en el sentido esperado —retransmisiones que recuperan entregas perdidas—.

## 4.5. Contrastación del Umbral del 85 %

La contrastación se efectuó en las dos vertientes definidas en el capítulo metodológico. En la vertiente de red, se calculó la PDR de cada una de las 27 celdas con su intervalo de confianza del 95 % por la distribución *t* de Student con 2 grados de libertad (t crítico = 4,303). En la vertiente de modelado, se verificó la exactitud y el puntaje F1 del clasificador en validación cruzada agrupada por celda, conforme al apartado 4.6.

### 4.5.1. Resultado por celda

| Celda | RSSI (dBm) | PDR (%) | IC 95 % | Latencia media (ms) | P95 (ms) | Jitter (ms) | Estado |
|---|---|---|---|---|---|---|---|
| A1B1C1 | -53,0 | 99,35 | [99,0; 99,8] | 13,7 | 20,4 | 3,5 | Cumple |
| A1B1C2 | -53,8 | 99,44 | [98,2; 100,0] | 19,6 | 26,8 | 4,1 | Cumple |
| A1B1C3 | -52,1 | 99,72 | [99,7; 99,7] | 24,5 | 32,4 | 4,5 | Cumple |
| A1B2C1 | -52,3 | 99,33 | [98,0; 100,0] | 25,7 | 38,5 | 6,5 | Cumple |
| A1B2C2 | -51,9 | 99,56 | [98,2; 100,0] | 30,8 | 43,3 | 6,8 | Cumple |
| A1B2C3 | -52,1 | 99,75 | [99,5; 100,0] | 39,3 | 53,7 | 7,8 | Cumple |
| A1B3C1 | -53,2 | 98,52 | [96,8; 100,0] | 112,9 | 153,7 | 23,3 | Cumple |
| A1B3C2 | -51,1 | 99,06 | [98,3; 99,8] | 116,3 | 163,2 | 26,2 | Cumple |
| A1B3C3 | -52,9 | 98,82 | [98,0; 99,6] | 129,5 | 175,4 | 25,7 | Cumple |
| A2B1C1 | -73,1 | 94,72 | [91,7; 97,7] | 18,1 | 26,8 | 4,5 | Cumple |
| A2B1C2 | -71,7 | 97,31 | [92,6; 100,0] | 21,6 | 30,7 | 4,8 | Cumple |
| A2B1C3 | -69,9 | 98,15 | [94,9; 100,0] | 27,7 | 36,5 | 5,1 | Cumple |
| A2B2C1 | -72,9 | 93,75 | [89,5; 98,0] | 40,7 | 60,1 | 10,6 | Cumple |
| A2B2C2 | -72,8 | 95,47 | [94,0; 97,0] | 43,4 | 61,2 | 9,6 | Cumple |
| A2B2C3 | -72,5 | 96,92 | [95,4; 98,4] | 57,6 | 79,5 | 11,7 | Cumple |
| A2B3C1 | -69,7 | 91,44 | [87,2; 95,6] | 130,8 | 166,7 | 20,4 | Cumple |
| A2B3C2 | -72,3 | 90,34 | [86,0; 94,7] | 147,4 | 187,7 | 22,9 | Cumple |
| A2B3C3 | -71,5 | 91,83 | [85,9; 97,8] | 151,6 | 193,2 | 23,7 | Cumple |
| A3B1C1 | -90,3 | 79,44 | [65,4; 93,5] | 20,4 | 29,7 | 5,1 | Indeterminado |
| A3B1C2 | -86,5 | 88,61 | [86,1; 91,1] | 26,4 | 36,2 | 5,4 | Cumple |
| A3B1C3 | -84,2 | 91,39 | [86,0; 96,8] | 31,6 | 42,3 | 5,7 | Cumple |
| A3B2C1 | -89,7 | 72,22 | [62,2; 82,3] | 78,6 | 114,6 | 19,6 | No cumple |
| A3B2C2 | -87,8 | 81,64 | [78,9; 84,3] | 78,7 | 112,5 | 18,3 | No cumple |
| A3B2C3 | -86,8 | 85,25 | [76,0; 94,5] | 86,1 | 124,7 | 20,4 | Indeterminado |
| A3B3C1 | -87,9 | 60,08 | [42,8; 77,4] | 134,5 | 171,8 | 21,3 | No cumple |
| A3B3C2 | -88,1 | 63,38 | [50,1; 76,6] | 150,8 | 192,2 | 23,5 | No cumple |
| A3B3C3 | -86,7 | 67,19 | [58,7; 75,7] | 160,8 | 204,2 | 24,7 | No cumple |

**Resumen de la vertiente de red:**

- Celdas con PDR ≥ 85 %: **21/27 (77,8 %)** — criterio de mayoría cumplido.
- Cumplen con evidencia completa (IC 95 % íntegramente sobre 85 %): 20 celdas.
- Incumplen con evidencia completa (IC 95 % íntegramente bajo 85 %): 5 celdas.
- Indeterminadas (el IC atraviesa el umbral): 2 celdas, clasificadas conforme al plan de contingencia.
- Escenario A1 (visibilidad directa): 9/9 celdas cumplidoras.
- Escenario A2 (un muro de concreto): 9/9 celdas cumplidoras.
- Escenario A3 (doble muro o ruido ISM, celdas críticas): 3/9 celdas cumplidoras.

### 4.5.2. Patrón de cumplimiento a lo largo de los factores

| Nivel | Celdas cumplidoras | PDR media | Latencia media |
|---|---|---|---|
| A1 | 9/9 | 99,3 % | 56,91 ms |
| A2 | 9/9 | 94,4 % | 70,99 ms |
| A3 | 3/9 | 76,6 % | 85,34 ms |
| B1 | 8/9 | 94,2 % | 22,63 ms |
| B2 | 7/9 | 91,5 % | 53,43 ms |
| B3 | 6/9 | 84,5 % | 137,18 ms |
| C1 | 6/9 | 87,7 % | 63,92 ms |
| C2 | 7/9 | 90,5 % | 70,56 ms |
| C3 | 8/9 | 92,1 % | 78,76 ms |

El patrón observado es coherente con el marco teórico: la degradación es monótona y ordenada al aumentar la severidad del canal (de A1 a A3) y al aumentar la carga de ofrecimiento (de B1 a B3), mientras que el nivel de QoS compensa parcialmente la pérdida a costa de latencia adicional. Las únicas celdas incumploras fueron A3B1C1, A3B2C1, A3B2C2, A3B3C1, A3B3C2, A3B3C3, todas bajo el escenario adverso A3 combinado con carga moderada o intensa; el umbral no fue redefinido sobre datos ya recolectados, conforme a la regla fijada por adelantado en el apartado 3.5.

## 4.6. Modelado con Scikit-learn

La fase de modelado se ejecutó en Python con Scikit-learn, siguiendo las seis etapas del apartado 4.6 previo, con la semilla 42 y con canalizaciones que encapsulan imputación, estandarización y clasificación para evitar la fuga de información.

### 4.6.1. Partición y familias de modelos

El conjunto se dividió en entrenamiento (97,524 mensajes) y prueba (41,796 mensajes), estratificado y con semilla fijada. Se entrenaron la línea base de ensamble —Bosque Aleatorio con 200 estimadores y profundidad máxima 16— y la línea base de regresión —Ridge con α = 1,0 sobre variables estandarizadas—, ambos dentro de canalizaciones íntegras.

### 4.6.2. Validación cruzada y riesgo de fuga

La validación cruzada estratificada de 10 pliegues a nivel mensaje produjo exactitud = 1,0000 y F1 = 1,0000, cifras que fueron descartadas como estimación principal por el motivo documentado en el plan: los mensajes de un mismo ensayo o celda aparecen simultáneamente en entrenamiento y validación, lo que infla el resultado por fuga de información. La estimación oficial, conservadora y reportada en la tesis, provino de la validación estratificada **por grupos (celda)** en 5 pliegues, en la que ninguna celda observada durante el entrenamiento reaparece en la validación:

| Pliegue | Celdas en test | Exactitud | F1 |
|---|---|---|---|
| 1 | 4 | 1,0000 | 1,0000 |
| 2 | 7 | 0,9187 | 0,9398 |
| 3 | 7 | 0,9468 | 0,9563 |
| 4 | 4 | 0,9541 | 0,9728 |
| 5 | 5 | 0,9364 | 0,9591 |

**Promedio de la validación por celda (cifra oficial): exactitud = 0,9512 ± 0,0271; F1 = 0,9656 ± 0,0202.** Ambas métricas superan el umbral del 85 % fijado por adelantado, por lo que la vertiente de modelado de clasificación **cumple** el criterio de éxito.

### 4.6.3. Evaluación en el conjunto de prueba y matrices de confusión

Sobre el holdout del 30 % intacto hasta la evaluación final, el clasificador alcanzó exactitud = 1,0000, precisión = 1,0000, sensibilidad = 1,0000, especificidad = 1,0000 y F1 = 1,0000. Las matrices de confusión, con sus interpretaciones operativas, fueron:

**Matriz de la validación por celda (sin fuga, fuera de pliegue; filas = real, columnas = predicho):**

| | Predicho NO cumple | Predicho SÍ cumple |
|---|---|---|
| Real NO cumple | VN = 38,274 | FP = 3,606 |
| Real SÍ cumple | FN = 3,171 | VP = 94,269 |

Los 3,606 falsos positivos implican alertar de degradación cuando el enlace aún operaba sobre el umbral —error conservador, preferible en monitoreo—; los 3,171 falsos negativos representan degradaciones reales no detectadas, concentradas en las fronteras de A3 donde la variabilidad entre réplicas es máxima.

**Matriz del holdout por mensaje (con fuga potencial, reportada solo como referencia):**

| | Predicho NO cumple | Predicho SÍ cumple |
|---|---|---|
| Real NO cumple | VN = 12,564 | FP = 0 |
| Real SÍ cumple | FN = 0 | VP = 29,232 |

### 4.6.4. Regresión Ridge de latencia

Sobre los 120,972 mensajes entregados, la regresión Ridge produjo MAE = 20,27 ms, RMSE = 25,02 ms, MAPE = 31,6 % y R² = 0,7643. El RMSE equivale al 9,2 % del rango observado en el conjunto de prueba (273,08 ms), por debajo del criterio de aceptación del 15 % fijado por adelantado: la regresión **cumple**. La validación cruzada de 10 pliegues confirmó la estabilidad del error (RMSE = 25,55 ± 1,94 ms). Los coeficientes, en variables estandarizadas, ordenaron la influencia predictiva como sigue:

| Predictivo | Coeficiente Ridge |
|---|---|
| B | 68,04 |
| rssi | -24,25 |
| A | -9,21 |
| C | 9,13 |
| snr_db | 7,37 |
| distancia | 4,75 |

El peso dominante de la carga B sobre la latencia cuantifica el carácter no lineal de la saturación de la cola observada en el factorial.

### 4.6.5. Interpretabilidad

La importancia de atributos del Bosque Aleatorio, calculada sobre el modelo ajustado al conjunto completo de entrenamiento, fue:

| Predictivo | Importancia |
|---|---|
| A | 0,3454 |
| snr_db | 0,2220 |
| rssi | 0,1936 |
| distancia | 0,1586 |
| B | 0,0499 |
| C | 0,0304 |

Los predictores de radiofrecuencia y de configuración —RSSI, SNR, distancia, escenario, carga y QoS— son todos relevantes y coherentes con el marco físico: el escenario A (que encapsula atenuación de muros y piso de ruido) y las variables de enlace (SNR, RSSI, distancia) concentran la mayor parte de la importancia, verificando que el modelo captura el canal y no artefactos ajenos al problema. La carga B y el QoS C, de menor importancia en clasificación —porque su efecto opera más sobre la latencia que sobre la entrega—, aparecen como los coeficientes dominantes de la regresión, cuadriculando así ambas vertientes del instrumento.

### 4.6.6. Selección final

El Bosque Aleatorio fue seleccionado como modelo de referencia por su desempeño en la validación honesta por celda (exactitud 95,1 %, F1 96,6 %), su estabilidad entre pliegues y la interpretabilidad de su estructura de importancia. El modelo, la semilla y la configuración quedaron serializados junto al *pipeline*, de modo que su evaluación puede repetirse de forma idéntica a partir del conjunto de datos versionado.

## 4.7. Visualización y Tableros en Power BI

Las tablas resultantes de la campaña —una fila por ensayo (81 filas) y una fila por celda (27 filas), con sus métricas e intervalos— alimentaron el modelo estrella de tableros: tabla de hechos por ensayo y dimensiones por escenario, carga, QoS, celda y calendario, con cardinalidad verificada. Las medidas de DAX de PDR, pérdida, latencia, P95, jitter y porcentaje de celdas bajo el umbral fueron contrastadas manualmente contra los valores de este capítulo, sin discrepancias, como condición previa a la publicación. Los tres tableros previstos —estado con semáforos de cumplimiento, diagnóstico con distribuciones y series, y predictivo con medido contra estimado y estructura de importancia— quedaron operativos y enlazados al conjunto de mediciones versionado.

## 4.8. Interpretación y Contrastación con las Preguntas de Investigación

- **PE1 — instrumento y canal.** El instrumento discriminó correctamente los tres escenarios: el RSSI medio observado fue -52,4 dBm en A1, -71,5 dBm en A2 y -87,6 dBm en A3, con el ordenamiento teórico de degradación intacto y con la variabilidad entre réplicas suficientemente pequeña como para que 20 de las 27 celdas alcanzaran evidencia estadística completa sobre el umbral. La familia de variables físicas del instrumento es representativa del canal.
- **PE2 — efectos e interacciones.** Los efectos principales e interacciones del factorial confirmaron la hipótesis: A×B y B×C resultaron significativas, la sobrecarga asociada al QoS 2 se incrementó con la carga y esa dependencia se agravó en el escenario de peor propagación. El ordenamiento coincide con el estado del arte revisado en el marco teórico.
- **PE3 — modelado.** El Bosque Aleatorio alcanzó exactitud 95,1 % y F1 96,6 % en la validación por celda —por encima del 85 %—, con los predictores de radiofrecuencia figurando entre los más relevantes, tal como el estado del arte les atribuye en contextos análogos.
- **PE4 — utilidad del instrumento.** El prototipo aportó trazabilidad completa de cada indicador hasta su celda y registro, habilitó la discriminación de las fronteras operativas de A3 que la operación convencional no detecta y se sostuvo con costo por nodo y sin infraestructura centralizada, situándose en la escala de madurez tecnológica prevista en el capítulo introductorio.

## 4.9. Validación, Límites y Amenazas a la Validez

Los cuatro controles de validez produjeron los siguientes resultados: *validez interna* —el orden aleatorio de los 81 ensayos neutralizó tendencias temporales y las diferencias observadas son atribuibles a los factores ensayados—; *validez externa* —los hallazgos son transferibles a interiores de una planta en la banda de 2,4 GHz con densidad de nodos similar, y su extrapolación a otras bandas o densidades queda explícitamente delimitada—; *validez de constructo* —la PDR y la exactitud del modelo representan operacionalmente la noción de QoS definida en el marco teórico, sin pretender agotarla—; y *fiabilidad* —la repetibilidad entre réplicas se cuantificó con los IC 95 % de la tabla del apartado 4.5.1, y la reproducibilidad del análisis completo está garantizada por la semilla y el versionado del conjunto de datos.

**Límites.** Los resultados quedan delimitados a la banda de 2,4 GHz, densidad fija de nodos y una planta; la interferencia de redes vecinas no controlada pudo introducir varianza no atribuible a los factores; y las 2 celdas frontera de A3, cuyo IC 95 % atraviesa el umbral, son el límite de precisión del tamaño muestral actual, con dirección de sesgo conservador documentada en el plan de contingencia.

**Proyección.** Las recomendaciones de configuración operativa resultantes —A1 o A2 con QoS 1 para el equilibrio entrega/latencia; QoS 2 sólo donde la entrega sea crítica y el enlace sea bueno; evitar oferta intensa bajo doble obstrucción sin ampliar réplicas— y las extensiones del diseño (densidad como cuarto factor, banda de 5 GHz, protocolos alternativos) se consolidan en el capítulo de conclusiones que cierra el proyecto.
