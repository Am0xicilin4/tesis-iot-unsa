# CAPÍTULO IV: ANÁLISIS E INTERPRETACIÓN DE LOS RESULTADOS

**Modalidad de redacción.** El presente capítulo se formula íntegramente en *modo proyectado*: los verbos corresponden al tiempo futuro y al condicional. La redacción en estos tiempos obedece a una razón de rigor: la campaña de mediciones no se ha ejecutado y, por tanto, no existen resultados que reportar. Este documento describe el análisis *previsto*, los procedimientos que *se ejecutarán*, los criterios que *se aplicarán* y las ramas de interpretación que *se activarían* según el comportamiento de los datos. En ningún apartado se anticipan valores numéricos de medición, de desempeño de modelos o de indicadores de tablero: toda cifra que aparezca corresponderá exclusivamente a un umbral, a un nivel de factor o a un parámetro metodológico fijado por adelantado en los capítulos precedentes.

## 4.1. Consideraciones Generales y Plan de Análisis

El plan de análisis seguirá la secuencia fijada en el protocolo experimental: primero *preparar* los datos, luego *describir* y *verificar* su calidad estadística, después *estimar los efectos* del diseño factorial, a continuación *construir y validar* los modelos de aprendizaje automático, y finalmente *comunicar* los hallazgos mediante tableros y *contrastarlos* con las preguntas de investigación. Cada etapa posee un producto verificable y un criterio de paso a la etapa siguiente.

El análisis se regirá por tres principios: (i) *integridad* —no se excluirán celdas ni observaciones sin registro documentado—; (ii) *reproducibilidad* —se fijarán semillas aleatorias, se versionará el conjunto de datos y se conservará el *pipeline* completo de análisis—; y (iii) *trazabilidad* —cada indicador publicado deberá poder rastrearse hasta el registro original que lo sustenta. La base de datos resultante de la campaña se denominará, de aquí en adelante, el *conjunto de mediciones*.

## 4.2. Tratamiento y Preparación de los Datos

El conjunto de mediciones *será* integrado desde tres registros convergentes: el registro de publicación de los nodos emisores, el registro de recepción de la estación suscriptora y el registro del *broker* MQTT. El primer paso *consistirá* en la unión de los tres conjuntos por el identificador único de mensaje y el número de secuencia, operación que *permitirá* discriminar la pérdida ocurrida en el enlace inalámbrico de la pérdida ocurrida en la cola del *broker*.

Sobre la tabla unificada *se ejecutarán* las siguientes operaciones, en el orden indicado:

1. **Verificación de integridad.** *Se comprobará* la continuidad de los números de secuencia, la existencia de marcas de tiempo válidas, la ausencia de campos nulos en las variables críticas y la correspondencia entre el número de mensajes publicados y el número de registros almacenados. Los registros inconsistentes *serán* marcados y, en su caso, *serán* excluidos únicamente con causa documentada en el cuaderno de campo.
2. **Verificación de sincronización.** *Se analizará* el desfase de los relojes informado por cada sesión de NTP; cuando el desfase *supere* la tolerancia declarada en el protocolo, la sesión respectiva *será* declarada inválida y sus ensayos *se repetirán*.
3. **Construcción de variables derivadas.** *Se calcularán* la latencia de un solo sentido y la latencia de ida y vuelta a partir de las marcas de tiempo, el jitter como desviación típica de las series móviles de retardo, la PDR y la pérdida como proporciones por celda y por réplica, el buen uso como carga útil por unidad de tiempo y los índices de radiofrecuencia como promedios y percentiles por ensayo.
4. **Codificación de factores.** Los escenarios, los niveles de carga y los niveles de QoS *serán* codificados como variables categóricas ordenadas, y la etiqueta de celda factorial *será* reconstruida de modo que cada observación *quede* identificada con su combinación A<sub>i</sub>B<sub>j</sub>C<sub>k</sub>.
5. **Detección de anomalías.** *Se aplicarán* criterios univariados predefinidos —basados en rangos intercuartílicos— para identificar valores atípicos; los valores detectados *serán* inspeccionados contra el cuaderno de campo y *se conservarán* en el conjunto de análisis salvo que exista evidencia documentada de falla instrumental.
6. **Estructuración para el modelado.** *Se conformarán* la matriz de predictores —RSSI, SNR, nivel de ruido, distancia, escenario, carga y nivel de QoS— y las variables objetivo —estado de cumplimiento del umbral, latencia y jitter—, con una partición estratificada entre entrenamiento y prueba que *se mantendrá* inmutable durante toda la fase de modelado.

[INSERTAR AQUÍ FLUJOGRAMA DE: Flujo de tratamiento y preparación de datos — unión de tres registros, verificación, variables derivadas, codificación, detección de anomalías y partición]

## 4.3. Análisis Descriptivo y Verificación de Supuestos

*Se calcularán* estadísticos descriptivos —media, mediana, desviación típica, coeficiente de variación y percentiles 50, 95 y 99— para cada métrica de QoS desagregada por factor y por celda. *Se construirán* histogramas y gráficos de caja por celda, que *permitirán* visualizar la asimetría de las distribuciones de latencia, la presencia de colas largas asociadas a retransmisiones y la dispersión de la PDR entre réplicas. *Se elaborarán* mapas de calor de PDR y de latencia media sobre las 27 celdas del diseño, cuya lectura preliminar *ofrecerá* una primera imagen del terreno de cumplimiento del umbral.

Para cada variable respuesta *se verificarán* los supuestos del modelo de análisis de varianza: normalidad de los residuos mediante la prueba de Shapiro-Wilk, homogeneidad de varianzas mediante la prueba de Levene y aditividad del modelo. Cuando la normalidad *resulte* rechazada, *se aplicarán* transformaciones —logarítmica para la latencia, arcseno para las proporciones— y, si los supuestos *persisten* incumplidos, *se recurrirá* a la alternativa no paramétrica correspondiente, cuyo resultado *se reportará* en paralelo al del modelo paramétrico. La decisión tomada *quedará* documentada con su justificación antes de proceder a los contrastes.

[INSERTAR AQUÍ GRÁFICO: Comportamiento previsto de la latencia extremo a extremo frente a la carga de ofrecimiento, diferenciado por nivel de QoS MQTT]

[INSERTAR AQUÍ GRÁFICO: Mapa de calor previsto de PDR y latencia media sobre las 27 celdas del diseño factorial]

## 4.4. Análisis del Diseño Factorial 3×3×3

*Se ajustará* el modelo de análisis de varianza de tres vías con interacciones para cada variable respuesta, conforme a la expresión definida en el capítulo metodológico. La lectura de resultados *seguirá* un orden fijo:

1. *Se evaluará*, en primer lugar, la interacción de tres factores A×B×C; si *resulta* significativa, la interpretación *se hará* por capas de factores, ya que los efectos principales *dejarían* de ser interpretables aisladamente.
2. *Se estimarán* las interacciones de dos factores (A×B, A×C, B×C), con especial atención a A×B —la dependencia del efecto de la carga respecto del escenario de propagación— y a B×C —la dependencia del efecto de la carga respecto del nivel de servicio MQTT—, que corresponden al núcleo de la hipótesis de trabajo.
3. *Se cuantificarán* los efectos principales de cada factor, con sus intervalos de confianza y sus tamaños de efecto.
4. *Se aplicarán* contrastes de comparación múltiple por el método de Tukey para establecer, dentro de cada factor, qué niveles difieren significativamente.
5. *Se calculará* la contribución porcentual de cada término a la varianza total, indicador que *será* utilizado para ordenar los hallazgos por relevancia práctica y no únicamente por significancia estadística.

Sobre la base del mismo modelo, *se elaborarán* los intervalos de confianza de la PDR por celda y *se clasificarán* las 27 celdas en dos categorías: aquellas cuyo intervalo *se ubica* íntegramente por encima del umbral del 85%, aquellas cuyo intervalo *se ubica* íntegramente por debajo y aquellas cuyo intervalo *lo atraviesa*, categoría que *será* interpretada como evidencia insuficiente y, en consecuencia, *activará* el paso de ampliación de evidencia del plan de contingencia.

[INSERTAR AQUÍ GRÁFICO: Diagrama de interacciones previsto — A×B, A×C, B×C y contribución porcentual de cada término a la varianza total]

## 4.5. Contrastación del Umbral del 85%

La contrastación *se efectuará* en las dos vertientes definidas en el capítulo metodológico. En la vertiente de red, *se verificará* si la PDR de cada celda alcanza o supera el 85%; *se determinará* el número y la identidad de las celdas cumplidoras; y *se describirá* el patrón de distribución del cumplimiento a lo largo de los factores. En la vertiente de modelado, *se verificará* si el desempeño del modelo en validación cruzada alcanza o supera el 85% de exactitud y, de manera complementaria, si el puntaje *F*1 respalda ese resultado.

Las ramas de decisión *quedarán* formuladas de la siguiente manera:

- **Si** la vertiente de red alcanza el umbral en la mayoría de las celdas y el patrón *resulta* coherente con lo previsto teóricamente —mejor desempeño en visibilidad directa, degradación creciente con la carga y diferencias ordenadas entre niveles de QoS—, *se concluirá* que el prototipo permite verificar el criterio de éxito y *se aceptará* la hipótesis de trabajo en esa dimensión.
- **Si** el cumplimiento *resulta* parcial y concentrado en condiciones específicas, *se concluirá* que el umbral es alcanzable sólo bajo condiciones delimitadas, *se identificarán* las fronteras operativas y *se formularán* recomendaciones de configuración para cada escenario.
- **Si** ninguna celda *alcanza* el umbral, *se activará* el plan de contingencia de cinco pasos en el orden establecido, y el análisis *continuará* únicamente después de cerrar cada paso con su criterio correspondiente.
- **Si** el modelo predictivo no alcanza la exactitud del 85%, *se discriminará* si la causa *reside* en la insufuencia de predictores, en el desbalance de clases, en la varianza intrínseca de la respuesta o en la especificación del algoritmo, y *se procederá* conforme a los pasos 3, 4 y 5 del plan de contingencia.

[INSERTAR AQUÍ FLUJOGRAMA DE: Árbol de decisión de contrastación del umbral del 85% — vertiente de red, vertiente de modelado y activación del plan de contingencia]

## 4.6. Modelado con Scikit-learn

La fase de modelado *se ejecutará* en el entorno de Python empleando la biblioteca Scikit-learn, siguiendo un flujo reproducible de seis etapas. El *dataset* de entrada *será* el conjunto tabular descrito en el apartado 3.4.5 del capítulo metodológico, integrado con los datos recolectados por los nodos ESP32 y el *broker* MQTT durante la campaña de mediciones.

### 4.6.1. Etapa 1 — Partición y preprocesamiento

El conjunto de datos *será* dividido en entrenamiento (70%) y prueba (30%), con estratificación cuando la variable objetivo sea discreta y semilla fijada por adelantado —valor 42—. Sobre el conjunto de entrenamiento *se aplicarán*, en orden: imputación de ausentes por mediana, codificación ordinal de las variables categóricas ordenadas —escenario, carga y nivel de QoS—, estandarización de las variables continuas —RSSI, SNR, ruido y distancia— para los algoritmos sensibles a la escala, y verificación del balance de clases en la vertiente de clasificación. Todos los pasos *quedarán* encapsulados en canalizaciones (*pipelines*) que *se ajustarán* exclusivamente sobre el entrenamiento, con el propósito de evitar la fuga de información. El conjunto de prueba *permanecerá* intacto hasta la evaluación final.

### 4.6.2. Etapa 2 — Selección de familias de modelos

*Se entrenarán*, como mínimo, cuatro modelos: una regresión logística como línea base interpretable, un árbol de decisión como modelo de referencia no lineal, un bosque aleatorio como método de ensamble principal y una regresión Ridge como línea base de la vertiente continua. La selección *no* se hará a priori: *se compararán* con las mismas métricas y el mismo esquema de validación.

[INSERTAR AQUÍ TABLA: Comparación de modelos entrenados — algoritmo, tipo, hiperparámetros ajustados, exactitud/RMSE en validación cruzada y tiempo de entrenamiento]

### 4.6.3. Etapa 3 — Ajuste de hiperparámetros

*Se buscarán* las configuraciones óptimas mediante validación cruzada en 10 pliegues con búsqueda en malla o aleatorizada —número y profundidad de estimadores, mínimo de muestras por hoja, parámetro de regularización—, asegurando que el conjunto de prueba *permanezca* intacto durante toda la búsqueda.

### 4.6.4. Etapa 4 — Evaluación sobre el conjunto de prueba

Una vez elegido el modelo ganador, *se calcularán* las métricas definitivas sobre el conjunto de prueba reservado:

- **Clasificación.** *Se obtendrán* exactitud, precisión, sensibilidad, especificidad, puntaje *F*1, área bajo la curva ROC y matriz de confusión. La matriz de confusión *se presentará* como tabla con los cuatro valores —verdaderos positivos, verdaderos negativos, falsos positivos y falsos negativos—, de modo que los tipos de error *puedan* interpretarse en términos operativos: un falso positivo implica alertar de degradación cuando el enlace funciona bien; un falso negativo implica no detectar una degradación real.
- **Regresión.** *Se calcularán* el error absoluto medio —MAE—, la raíz del error cuadrático medio —RMSE—, el error porcentual absoluto medio —MAPE— y el coeficiente de determinación —R²—. El RMSE *se expresará* en milisegundos —misma unidad que la variable objetivo—, de modo que su valor *represente* el error típico de predicción de manera directamente interpretable.

Los resultados *se reportarán* con sus intervalos de confianza obtenidos por remuestreo —*bootstrap* con 1.000 iteraciones—.

[INSERTAR AQUÍ TABLA: Métricas de evaluación del modelo ganador — clasificación (exactitud, precisión, sensibilidad, F1, AUC-ROC) y regresión (MAE, RMSE, MAPE, R²) con intervalos de confianza]

[INSERTAR AQUÍ TABLA: Matriz de confusión del modelo de clasificación — verdaderos positivos, verdaderos negativos, falsos positivos y falsos negativos con sus porcentajes]

### 4.6.5. Etapa 5 — Interpretabilidad

*Se obtendrán* la importancia de atributos del bosque aleatorio y los coeficientes de la regresión regularizada; *se contrastarán* ambos criterios; y *se verificará* si los predictores de radiofrecuencia y de configuración —RSSI, SNR, distancia, carga y nivel de QoS— figuran entre los más relevantes. Este paso *será* el que vincule el modelo con el marco físico de la investigación: un modelo con desempeño elevado pero cuyos predictores dominantes *sean* ajenos al problema planteado *será* considerado insuficiente para los fines de la tesis.

[INSERTAR AQUÍ GRÁFICO: Importancia de predictores del modelo — barras horizontales ordenadas por relevancia, con RSSI, SNR, distancia, carga, QoS y escenario]

### 4.6.6. Etapa 6 — Comparación y selección final

*Se elegirá* el modelo que ofrezca el mejor compromiso entre desempeño, estabilidad entre pliegues e interpretabilidad, y *se documentarán* las razones de la selección. *Se conservarán* el modelo serializado, la semilla aleatoria y la configuración final, de modo que su evaluación *pueda* repetirse de forma idéntica.

[INSERTAR AQUÍ FLUJOGRAMA DEL PIPELINE DE MACHINE LEARNING: Recolección — nodos ESP32 y broker MQTT, Preprocesamiento — limpieza, codificación y escalado, División — 70/30 estratificada, Entrenamiento — validación cruzada en 10 pliegues, Evaluación — conjunto de prueba y Predicción — modelo serializado]

**Ramas condicionales.** Si el modelo seleccionado alcanza la exactitud y el puntaje *F*1 del 85% en validación cruzada y en el conjunto de prueba, *se concluirá* que la correlación entre variables físicas de radiofrecuencia y variables dinámicas de red *es* modelable con precisión suficiente para fines de evaluación de QoS, y *se aceptará* la hipótesis en esa dimensión. Si el desempeño *resulta* inferior, *se analizarán* las causas técnicas —predictores insuficientes, ruido de medición, efecto de factores no controlados, tamaño muestral, desbalance de clases—, *se aplicarán* los ajustes correspondientes y, en última instancia, *se reportará* el desempeño alcanzado sin forzar el cumplimiento. Si la importancia de predictores *mostrara* que el nivel de QoS o la carga dominan al RSSI, *se concluirá* que el comportamiento de la red interior en las condiciones ensayadas está gobernado más por la capa de aplicación y de acceso que por la atenuación, hallazgo que *sería* coherente con la hipótesis de conflicto estructural entre capas planteada en la introducción.

## 4.7. Visualización y Tableros en Power BI

Los resultados *serán* trasladados a Power BI mediante la importación del conjunto de mediciones y de las tablas resumen producidas por el análisis estadístico y por las predicciones del modelo.

**Modelado de datos.** *Se construirá* un modelo estrella: una tabla de hechos con una fila por mensaje o por ensayo, y tablas de dimensión por escenario de propagación, nivel de carga, nivel de QoS, celda factorial y calendario. *Se definirán* relaciones unívocas entre hechos y dimensiones y *se verificará* la cardinalidad antes de publicar.

**Medidas y lógica de negocio.** *Se crearán* medidas de DAX para la PDR, la pérdida, la latencia media y percentil 95, el jitter, el buen uso y el porcentaje de celdas que cumplen el umbral, incluyendo el cálculo condicional de cumplimiento respecto del 85% y la variación de cada indicador respecto de la línea base. Todas las medidas *serán* validadas mediante contraste manual contra los valores calculados directamente en el entorno de análisis.

**Tableros previstos.** *Se diseñarán* al menos tres tableros: (i) un *tablero de estado*, con semáforos de cumplimiento del umbral por celda y por métrica; (ii) un *tablero de diagnóstico*, con series temporales de latencia y jitter, mapas de calor por escenario y distribuciones de RSSI; y (iii) un *tablero predictivo*, con la comparación entre los valores medidos y los valores estimados por el modelo, la importancia de predictores y el porcentaje de aciertos de clasificación. *Se configurarán* filtros cruzados por escenario, carga y nivel de QoS, así como la posibilidad de profundizar (*drill-through*) desde el indicador agregado hasta el registro individual.

**Verificación de coherencia.** Antes de la publicación, *se contrastará* cada indicador visualizado contra el valor calculado en el procesamiento estadístico; cualquier discrepancia *impedirá* la publicación del tablero hasta ser resuelta. Los tableros *quedarán* enlazados al conjunto de mediciones versionado, de modo que su actualización *sea* reproducible ante la adición de nuevas campañas.

[INSERTAR AQUÍ TABLA: Modelo estrella y esquema de relaciones para los tableros de control en Power BI]

[INSERTAR AQUÍ IMAGEN TÉCNICA: Esquema de los tableros de Power BI — estado, diagnóstico y predictivo, con filtros cruzados y drill-through]

## 4.8. Interpretación y Contrastación con las Preguntas de Investigación

La interpretación *se organizará* siguiendo el sistema de preguntas formulado en el capítulo introductorio:

- **Respecto de la PE1.** *Se evaluará* el ajuste del modelo de pérdida de trayecto calibrado al escenario mediante el error medio cuadrático y el coeficiente de determinación, y *se discutirá* la correspondencia entre el RSSI observado y la condición de obstrucción de cada escenario. Si el modelo *resulta* adecuado, *se afirmará* que la familia de variables físicas del instrumento es representativa del canal; de lo contrario, *se explicitarán* las fuentes de dispersión no capturadas —multipropagación, ocupación del local, interferencia vecina— y su efecto sobre el análisis posterior.
- **Respecto de la PE2.** *Se interpretarán* los efectos principales e interacciones del factorial a la luz de los marcos teóricos del acceso al medio y de la semántica de confirmación de MQTT: *se examinará*, por ejemplo, si la sobrecarga asociada al nivel QoS 2 *se incrementa* con la carga y si esa dependencia *se atenúa* o *se agrava* según el escenario de propagación. Los hallazgos *se contrastarán* con el ordenamiento cualitativo reportado en el estado del arte, *se señalarán* las coincidencias y las divergencias y *se argumentarán* estas últimas a partir de las diferencias de entorno y de carga.
- **Respecto de la PE3.** *Se discutirá* el desempeño relativo de los algoritmos evaluados, la estabilidad entre pliegues, la estructura de importancia de predictores y la capacidad del modelo para discriminar el cumplimiento del umbral. *Se relacionará* la magnitud de la contribución de los predictores de radiofrecuencia con la importancia que el estado del arte les atribuye en contextos distintos.
- **Respecto de la PE4.** *Se evaluará* la utilidad del instrumento a partir de la cobertura de información que aporta respecto de la operación convencional, la trazabilidad de los tableros y la estimación de costo por nodo, y *se situará* el resultado en una escala explícita de madurez tecnológica.

La contrastación final *incluirá* una tabla de correspondencia entre cada pregunta, cada objetivo específico, la evidencia producida y la conclusión alcanzada, de modo que la coherencia interna del trabajo *pueda* verificarse de un solo vistazo.

[INSERTAR AQUÍ TABLA: Matriz de correspondencia PE1–PE4 — pregunta, objetivo específico, evidencia producida y conclusión prevista]

## 4.9. Validación, Límites y Amenazas a la Validez

*Se someterá* el conjunto de resultados a cuatro controles de validez:

- **Validez interna.** *Se verificará* que las diferencias observadas *sean* atribuibles a los factores ensayados, descartando por registro documentado interferencias exógenas no controladas; *se revisará* si el orden aleatorio de los ensayos *neutralizó* posibles tendencias temporales.
- **Validez externa.** *Se discutirá* cuidadosamente la transferibilidad de los hallazgos a escenarios distintos del ensayado, considerando la banda de operación, la densidad fija de nodos, la geometría de las instalaciones y el protocolo de transporte evaluado.
- **Validez de constructo.** *Se argumentará* en qué medida la PDR y la exactitud del modelo *representan* la noción de calidad de servicio definida en el marco teórico, y *se reconocerán* los aspectos de la experiencia de calidad que el instrumento no captura —carga de trabajo del usuario, semántica de la aplicación, seguridad—.
- **Fiabilidad.** *Se reportarán* la repetibilidad de las métricas entre réplicas, la consistencia entre los tres registros convergentes y la reproducibilidad del análisis completo a partir del conjunto de datos versionado.

**Límites previstos.** *Se anticipa* que los resultados quedan delimitados a la banda de 2,4 GHz, a una densidad de nodos constante y a interiores de una planta; que la interferencia de redes vecinas no controladas *podría* introducir varianza no atribuible a los factores; y que el tamaño muestral *podría* limitar la precisión de las estimaciones en celdas de respuesta dispersa. Estas amenazas *serán* tratadas explícitamente en las conclusiones, con indicación de su dirección probable —sesgo conservador o sesgo optimista— sobre los hallazgos.

**Proyección.** En función de los resultados obtenidos, *se formularán* recomendaciones de configuración operativa para redes interiores —escenario, carga y nivel de QoS recomendados por condición—, *se propondrán* extensiones del diseño —incorporación de la densidad de nodos como cuarto factor, evaluación en banda de 5 GHz, incorporación de protocolos alternativos de transporte— y *se definirá* la ruta para elevar el prototipo a un grado de madurez tecnológica superior mediante pruebas en instalaciones y condiciones de operación reales.
