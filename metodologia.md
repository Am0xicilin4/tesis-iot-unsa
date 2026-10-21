# CAPÍTULO III: ELABORACIÓN DE LA PROPUESTA

El presente capítulo describe la propuesta en su integridad: las generalidades del diseño de investigación (3.1), el esquema del prototipo (3.2), la definición operacional de las variables (3.3), el diseño factorial experimental 3×3×3 que estructura la campaña de mediciones (3.4), el criterio de éxito del 85% con su plan de contingencia explícito de cinco pasos (3.5), el alcance de la intervención (3.6) y el procedimiento de validación que garantiza el rigor científico de los resultados (3.7).

## 3.1. Generalidades

### 3.1.1. Tipo, nivel, enfoque y método de investigación

**Tipo.** La investigación es *aplicada*, porque su finalidad inmediata es producir un artefacto —el prototipo IoT híbrido— y un conjunto de reglas de uso —el protocolo de evaluación del QoS— que resuelven una problemática concreta de ingeniería. Es también de carácter *experimental*, porque manipula deliberadamente factores de un sistema y observa la respuesta bajo condiciones controladas, lo que habilita la atribución causal de los cambios observados.

**Nivel.** El nivel es *explicativo-correlacional*: la primera fase explica la influencia de los factores experimentales sobre las métricas de calidad de servicio mediante análisis de varianza; la segunda establece la relación estadística y predictiva entre las variables físicas de radiofrecuencia y las variables dinámicas de red mediante modelos de aprendizaje automático. El nivel explicativo se justifica por el carácter manipulado de los factores; el correlacional, por el carácter observacional de los índices de radiofrecuencia, que no se manipulan sino que se miden.

**Enfoque.** Cuantitativo, con uso secundario de información de carácter cualitativo únicamente en la documentación de incidentes operativos (observaciones del laboratorio, notas de campo sobre condiciones ambientales) que se emplean como contexto interpretativo y no como evidencia estadística.

**Método.** Método experimental con dos momentos complementarios: (i) *medición y comparación* bajo un diseño factorial completo, que responde a la PE2; y (ii) *modelado predictivo supervisado*, que responde a la PE3. Ambos momentos comparten la misma base de datos, generada por un único instrumento de adquisición, condición que garantiza la coherencia entre el análisis de efectos y el análisis de correlación.

### 3.1.2. Lugar de ejecución

La investigación se ejecuta en instalaciones interiores de tipo institucional —aulas, laboratorios y pasillos de circulación— que presentan las condiciones requeridas: presencia de infraestructura Wi-Fi en la banda de 2,4 GHz, geometrías cerradas con mobiliario y tabiquería convencionales, y posibilidad de disponer las estaciones del experimento en distancias y obstrucciones controladas. El *broker* MQTT y la estación de adquisición se operan en una red local del propio escenario, de modo que el trayecto de cada mensaje esté íntegramente bajo control del experimentador y la influencia de Internet sobre la latencia quede excluida de las mediciones, salvo en los ensayos expresamente destinados a evaluar el escenario remoto.

### 3.1.3. Material y equipos

| Componente | Especificación funcional | Rol en el experimento |
|---|---|---|
| Nodos emisores (3 unidades) | Placa ESP32 con interfaz Wi-Fi IEEE 802.11 b/g/n, firmware propio con biblioteca MQTT y lectura de RSSI/SNR del controlador | Generan la carga de tráfico y reportan los índices de radiofrecuencia en cada publicación |
| Nodo suscriptor (1 unidad) | Placa ESP32 con conexión Wi-Fi y marca de tiempo local | Registra la recepción, calcula la latencia extremo a extremo y verifica la unicidad de los mensajes |
| Punto de acceso inalámbrico | Router o punto de acceso doméstico/institucional operativo en un canal fijo no solapado de 2,4 GHz | Define el medio de acceso y las condiciones de contienda |
| *Broker* MQTT | *Broker* de código abierto (por ejemplo, Mosquitto) instalado en la estación de adquisición, con registro (*logging*) de sesión y de mensajes | Enruta y confirma los mensajes según el nivel de QoS ensayado |
| Estación de adquisición | Computadora con sistema operativo, servidor de base de datos y sincronización NTP | Almacena las series temporales sincronizadas de ambas familias de variables |
| Estación de análisis | Computadora con entorno de programación Python, bibliotecas de análisis de datos, Scikit-learn y Power BI | Ejecuta el procesamiento, el modelado y la construcción de tableros |
| Instrumentación complementaria | Medidor de campo o aplicación de medición Wi-Fi para verificación independiente del RSSI; plancha de planta del escenario con distancias marcadas | Verificación cruzada del instrumento y levantamiento geométrico del escenario |

La selección del hardware obedece al criterio de costo por nodo compatible con despliegues masivos, al que se alude en la PE4; la lista de materiales y su presupuesto corresponden a los anexos del documento final.

[INSERTAR AQUÍ TABLA: Especificación técnica y costos de los componentes del prototipo físico ESP32]

[INSERTAR AQUÍ IMAGEN TÉCNICA: Topología de nodos ESP32 — nodos emisores N1–N3, suscriptor y punto de acceso en el escenario experimental]

### 3.1.4. Procedimientos

La ejecución se organiza en cinco fases secuenciales, con entregables verificables en cada una de ellas:

1. **Diseño y construcción del prototipo.** Definición de la arquitectura de mensajes, codificación de los campos de la publicación (identificador de nodo, marca de tiempo de emisión, contador de secuencia, RSSI, SNR, nivel de ruido, escenario y nivel de QoS), integración del *broker* y de la base de datos, y pruebas de integración en mesa.
2. **Calibración del instrumento.** Verificación de la sincronización de relojes mediante NTP, medición de referencia en un trayecto conocido para el ajuste del modelo de pérdida de distancia, y validación cruzada del RSSI reportado por el ESP32 con un instrumento independiente. Criterio de salida: error de sincronización y de medición dentro de los tolerancias declarados en el protocolo.
3. **Campaña de mediciones.** Ejecución de la matriz factorial completa con el número de réplicas predefinido, en orden aleatorizado de ensayos, registrando todas las condiciones y todo incidente en el cuaderno de campo.
4. **Procesamiento y modelado.** Tratamiento estadístico de los datos, verificación de supuestos, análisis de varianza, entrenamiento y validación de los modelos de Machine Learning con Scikit-learn.
5. **Comunicación de resultados y validación.** Construcción de los tableros de Power BI, contrastación con el criterio de éxito, aplicación del plan de contingencia cuando corresponda y redacción de conclusiones.

[INSERTAR AQUÍ FLUJOGRAMA DE: Las cinco fases secuenciales de ejecución de la investigación con sus entregables verificables]

## 3.2. Esquema de la Propuesta

La propuesta se compone de cuatro capas funcionales que se interconectan de la siguiente manera:

```
 CAPA 1 — CAPTACIÓN Y EMISIÓN (nodos instrumentados)
 ┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐
 │  Nodo ESP32 (N1)   │   │  Nodo ESP32 (N2)   │   │  Nodo ESP32 (N3)   │
 │  + marca de tiempo │   │  + marca de tiempo │   │  + marca de tiempo │
 │  + RSSI / SNR      │   │  + RSSI / SNR      │   │  + RSSI / SNR      │
 └─────────┬──────────┘   └─────────┬──────────┘   └─────────┬──────────┘
           └───────────────┬────────┴────────────┬───────────┘
                           ▼                     ▼
 CAPA 2 — MEDIO INALÁBRICO     ┌──────────────────────────────┐
 (Wi-Fi IEEE 802.11, 2,4 GHz)  │ Punto de acceso (canal fijo  │
 escenarios A1 / A2 / A3       │ no solapado, CSMA/CA, DCF)   │
                               └──────────────┬───────────────┘
                                              ▼
 CAPA 3 — TRANSPORTE Y ALMACENAMIENTO
                    ┌────────────────────────────────────────┐
                    │  Broker MQTT (QoS 0 / 1 / 2 = C1/C2/C3) │
                    └────────────────────┬───────────────────┘
                                         ▼
                    ┌────────────────────────────────────────┐
                    │  Estación de adquisición + base de      │
                    │  datos (series sincronizadas por NTP)   │
                    └────────────────────┬───────────────────┘
                                         ▼
 CAPA 4 — ANÁLISIS Y COMUNICACIÓN
          ┌──────────────────────────┬───────────────────────────┐
          │ Scikit-learn             │ Power BI                  │
          │ ANOVA 3 factores,        │ tableros de KPI,          │
          │ modelos de clasificación │ estados del umbral 85 %,  │
          │ y regresión, importancia │ tendencias por escenario  │
          │ de predictores           │ y alertas de degradación  │
          └──────────────────────────┴───────────────────────────┘
```

La lectura del esquema es la siguiente: los nodos de la capa 1 emiten publicaciones MQTT que contienen, en una misma unidad de registro, la variable temporal de la aplicación y los índices de radiofrecuencia; la capa 2 condiciona esa transmisión conforme al escenario de propagación vigente y a las reglas de acceso al medio; la capa 3 materializa el nivel de servicio ensayado y almacena el resultado; y la capa 4 transforma el conjunto de registros en evidencia estadística, en modelo predictivo y en indicadores comunicables. La originalidad de la propuesta reside en la capa 1: el instrumento de medición es *el propio nodo de la red*, de modo que la obtención de las variables físicas no requiere de un analizador de espectro ni de una sonda comercial.

[INSERTAR AQUÍ IMAGEN TÉCNICA: Diagrama de arquitectura del prototipo con las cuatro capas funcionales — captación, medio inalámbrico, transporte/almacenamiento y análisis]

## 3.3. Variables de la Investigación

**Variables independientes (factores experimentales).**

- **A — Escenario de propagación.** Tres niveles: A1, visibilidad directa a corta distancia sin obstáculos interpuestos; A2, sin visibilidad directa con un tabique o barrera de mobiliario interpuesto; A3, sin visibilidad directa con doble barrera o trayecto de pasillo de longitud superior.
- **B — Carga de ofrecimiento.** Tres niveles definidos por el intervalo de publicación: B1, oferta esparsa; B2, oferta moderada; B3, oferta intensa.
- **C — Nivel de servicio MQTT.** Tres niveles: C1 (QoS 0), C2 (QoS 1) y C3 (QoS 2).

La combinación de los tres factores con tres niveles produce un **diseño factorial completo 3×3×3 con 27 combinaciones de tratamiento**.

**Variables dependientes (respuestas).**

1. PDR, en porcentaje — variable de referencia para el umbral del 85%.
2. Latencia extremo a extremo, en milisegundos (media y percentil 95).
3. Jitter, en milisegundos (desviación típica de los retardos).
4. Pérdida de paquetes, en porcentaje.
5. Buen uso, en kilobits por segundo.

**Variables medidas o covariables físicas** (no manipuladas, registradas en cada publicación): RSSI, SNR, nivel de ruido de fondo, distancia entre emisor y receptor, número y tipo de obstáculos del trayecto.

**Variables intervinientes o de control:** densidad de nodos fija (tres emisores y un suscriptor), canal Wi-Fi fijo no solapado, tamaño de carga útil constante, firmware idéntico en todos los nodos, ubicación fija del punto de acceso y del *broker*, sincronización NTP activa, y horario de ejecución registrado. El control de estas variables es lo que permite atribuir las diferencias observadas a los tres factores ensayados.

[INSERTAR AQUÍ TABLA: Definición operacional de variables — independientes (factores A/B/C), dependientes (PDR, latencia, jitter, pérdida, buen uso), covariables físicas y de control]

## 3.4. Diseño Experimental Factorial 3×3×3

### 3.4.1. Justificación del diseño

El problema descrito en la realidad problemática es de naturaleza *interactiva*: se sospecha que la degradación del QoS no es aditiva, es decir, que el efecto de una carga elevada sobre la latencia no es el mismo en visibilidad directa que tras doble muro, y que el nivel de servicio MQTT modula esa diferencia. Un diseño de un solo factor a la vez (*one-factor-at-a-time*) es incapaz de detectar interacciones y exige un número mayor de ensayos para una cobertura menor. El diseño factorial completo estima simultáneamente los tres efectos principales y las tres interacciones de dos factores más la de tres factores, con eficiencia muestral apreciable, y ofrece además una estructura natural para el análisis de varianza.

### 3.4.2. Matriz experimental

| Factor | Niveles | Descripción |
|---|---|---|
| A — Escenario de propagación | A1 / A2 / A3 | Visibilidad directa / sin visibilidad leve / sin visibilidad severa |
| B — Carga de ofrecimiento | B1 / B2 / B3 | Intervalo de publicación esparsa / moderado / intenso |
| C — Nivel de servicio MQTT | C1 / C2 / C3 | QoS 0 / QoS 1 / QoS 2 |

La matriz resultante contiene las 27 celdas A<sub>i</sub>B<sub>j</sub>C<sub>k</sub>. Cada celda se ejecuta con un número definido de réplicas —mínimo tres— ordenadas de forma aleatoria en el tiempo para neutralizar el efecto de posibles tendencias temporales (variación de la interferencia de red vecina a lo largo del día). Cada réplica corresponde a un ensayo de duración fija con un número mínimo preestablecido de mensajes publicados, de modo que las métricas de proporción (PDR, pérdida) se calculen sobre una base muestral suficiente.

El volumen total de observaciones resulta de 27 celdas multiplicado por el número de réplicas; a cada mensaje individual se le asocian, además de su resultado de entrega, su marca de tiempo, los índices de radiofrecuencia reportados por el nodo y la etiqueta de celda, lo que conforma un conjunto de datos tabular apto tanto para el análisis de varianza como para el aprendizaje automático.

[INSERTAR AQUÍ TABLA: Matriz completa del diseño factorial 3×3×3 — 27 celdas A_iB_jC_k con niveles descriptos]

[INSERTAR AQUÍ FLUJOGRAMA DE: Flujo del diseño factorial 3×3×3 — factores, niveles, réplicas y orden aleatorizado de ensayos]

### 3.4.3. Instrumentación de la medición

- **Sincronización.** Todos los nodos sincronizan su reloj por NTP antes de cada ensayo; la latencia de un solo sentido se calcula como diferencia de marcas de tiempo entre publicación y recepción. Como control de calidad, se registra el desfase de sincronización observado en cada sesión.
- **Registro doble.** Cada publicación transporta la información de radiofrecuencia; el suscriptor registra la recepción; el *broker* conserva el registro de entrega y de confirmación. La triangulación de los tres registros permite distinguir un mensaje perdido en el enlace inalámbrico de uno perdido en la cola del *broker*.
- **Etiquetado.** Cada registro lleva los campos de escenario, carga, nivel de QoS, réplica y número de secuencia, lo que permite reconstruir íntegramente la matriz experimental desde la base de datos.
- **Trazabilidad.** Se conservan la versión del firmware, la configuración del punto de acceso, la versión del *broker*, la plancha del escenario con las distancias medidas y el cuaderno de campo.

### 3.4.4. Análisis estadístico previsto

El análisis de los datos del diseño se plantea mediante un **análisis de varianza de tres vías** con modelo de efectos fijos:

Y = μ + A<sub>i</sub> + B<sub>j</sub> + C<sub>k</sub> + (AB)<sub>ij</sub> + (AC)<sub>ik</sub> + (BC)<sub>jk</sub> + (ABC)<sub>ijk</sub> + ε

donde Y es la respuesta considerada (PDR, latencia, jitter, pérdida o buen uso) y ε el error experimental. El procedimiento contempla:

1. Verificación de los supuestos mediante la prueba de Shapiro-Wilk sobre los residuos y la prueba de Levene sobre la homogeneidad de varianzas; cuando las respuestas de proporción violen los supuestos, se aplicará una transformación logarítmica o arcseno sobre los porcentajes, y, en su defecto, se recurrirá a pruebas no paramétricas alternativas.
2. Estimación de los efectos principales y de las interacciones con un nivel de significancia fijado por adelantado en α = 0,05.
3. Contrastes de comparación múltiple por el método de Tukey para las diferencias entre niveles de un mismo factor, con intervalos de confianza reportados.
4. Estimación de tamaños de efecto y de la varianza explicada por cada término del modelo, de modo que la significancia estadística no se interprete desligada de la relevancia práctica.
5. Verificación del cumplimiento o incumplimiento del umbral del 85% celda por celda, con el intervalo de confianza correspondiente.

[INSERTAR AQUÍ FLUJOGRAMA DE: Procedimiento del ANOVA de tres vías — verificación de supuestos, efectos e interacciones, contrastes de Tukey y verificación del umbral]

### 3.4.5. Proceso de aprendizaje automático sobre la misma base de datos

Sobre el mismo conjunto de registros, y respondiendo a la PE3, se ejecutará el siguiente flujo: separación de predictores (índices de radiofrecuencia, distancia, escenario, carga, nivel de QoS) y de variable objetivo (estado de cumplimiento del umbral y, en la vertiente de regresión, los valores de latencia y jitter); partición estratificada entre entrenamiento y prueba; preprocesamiento con imputación y escalado cuando el algoritmo lo requiera; ajuste de una línea base de regresión regularizada y de modelos de árbol y ensamble; búsqueda de hiperparámetros mediante validación cruzada; y evaluación final con las métricas definidas en el marco teórico. El detalle de este procedimiento se describe en el Capítulo IV, donde se presenta íntegramente en modo proyectado.

## 3.5. Criterio de Éxito: Umbral del 85% y Plan de Contingencia

### 3.5.1. Definición operacional del umbral

El **umbral del 85%** se establece como *criterio de éxito metodológico* y se opera en dos vertientes:

- **Vertiente de red.** La celda experimental se considera que alcanza el criterio cuando la razón de entrega de tramas (PDR) es igual o superior al 85%, con su intervalo de confianza correspondiente. La PDR se elige como métrica de referencia por ser la expresión directa de la confiabilidad entregada al usuario final y por ser una proporción directamente interpretable.
- **Vertiente de modelado.** El modelo de Machine Learning se considera que alcanza el criterio cuando su desempeño en validación cruzada —exactitud y, de manera complementaria, el puntaje *F*1— es igual o superior al 85%.

La fijación del umbral *antes* de la recolección es una decisión de diseño metodológico: elimina la tentación de redefinir el criterio con base en los resultados observados y convierte tanto el cumplimiento como el incumplimiento en resultados interpretables. En consecuencia, la investigación no se condiciona a que el 85% se alcance: se condiciona a que el 85% se *verifique con rigor* y a que, si no se alcanza, se diagnostique técnicamente la causa mediante el procedimiento que sigue.

### 3.5.2. Plan de contingencia de cinco pasos

El plan se activa automáticamente cuando (i) ninguna celda del diseño alcanza la PDR del 85%, (ii) las celdas que lo alcanzan no son reproducibles entre réplicas, o (iii) el modelo predictivo no alcanza la exactitud del 85% en validación cruzada. Sus cinco pasos son secuenciales, excluyentes en su orden y cada uno posee un criterio de cierre explícito.

**Paso 1 — Verificación del instrumental y de la trazabilidad.**
Acción: revisar la sincronización de relojes y su desfase registrado, la integridad del firmware y su versión, la configuración vigente del punto de acceso y del *broker*, la continuidad del registro en la base de datos y la correspondencia entre los tres registros (nodo, suscriptor y *broker*). Se repite una medición de referencia en un trayecto conocido y se contrasta el RSSI con el instrumento independiente.
Criterio de cierre: se confirma que el instrumento produce registros íntegros y consistentes, o se corrige la falla detectada y se reinicia la campaña desde el punto afectado.

**Paso 2 — Re-aislamiento de causas exógenas.**
Acción: verificar mediante análisis espectral o revisión de la configuración la presencia de redes vecinas, interferentes o actividad anómala no previstas; repetir los ensayos afectados en horario de menor actividad y en canal verificado; documentar las condiciones ambientales y de ocupación del escenario.
Criterio de cierre: se identifica y se acota o se documenta como condición permanente del escenario la fuente exógena de degradación.

**Paso 3 — Ampliación de la evidencia.**
Acción: aumentar el número de réplicas de las celdas infractoras, extender la duración de los ensayos, revisar con criterios predefinidos —y no *ad hoc*— la posible exclusión de valores atípicos justificados documentalmente, y evaluar la estabilidad de las estimaciones mediante el análisis de la variabilidad entre réplicas.
Criterio de cierre: se dispone de una estimación con intervalo de confianza lo bastante estrecho como para afirmar si el incumplimiento es real o producto de varianza muestral insuficiente.

**Paso 4 — Reajuste de parámetros configurables del prototipo y del protocolo.**
Acción: modificar parámetros de configuración —no de medición— con fundamento técnico: selección de canal Wi-Fi no solapado distinto, ajuste de la potencia de transmisión si el hardware lo permite, tamaño de carga útil, intervalo de *keep alive*, temporizadores de sesión, profundidad de reintentos y nivel de servicio MQTT. Se vuelve a ejecutar únicamente la submatriz de celdas afectadas.
Criterio de cierre: se identifica la configuración que alcanza el umbral y se documenta como recomendación operativa, o se demuestra que ningún ajuste de parámetros disponible permite alcanzarlo dentro de las condiciones ensayadas.

**Paso 5 — Formalización de la desviación y re-umbralización documentada.**
Acción: si los pasos 1 a 4 no conducen al cumplimiento, se emite un informe técnico de desviación que contiene: las celdas y métricas afectadas, el umbral alcanzado con su intervalo de confianza, el historial de acciones ejecutadas con su resultado, el diagnóstico técnico de la causa y la propuesta de umbral alternativo debidamente justificada. Los resultados se reportan íntegros, sin exclusión de celdas ni modificación de datos recolectados; el umbral original se conserva en la memoria del documento como referencia y el nuevo se declara como *objetivo condicional* para futuras iteraciones.
Criterio de cierre: el informe de desviación queda incorporado al capítulo de resultados y a las recomendaciones, con decisión explícita del asesor.

**Regla rectora del plan.** En ningún caso se modifica retroactivamente el umbral sobre datos ya recolectados, no se eliminan celdas del diseño sin registro documentado y no se declaran resultados selectivamente: la integridad del protocolo experimental prevalece sobre el cumplimiento del criterio.

[INSERTAR AQUÍ FLUJOGRAMA DE: Plan de contingencia de 5 pasos — condiciones de activación, acciones y criterios de cierre de cada paso]

## 3.6. Alcance de la Investigación

**Alcance por intervención.** La investigación *diseña, construye, instrumenta y valida* un prototipo de evaluación de QoS; *ejecuta* una campaña de mediciones estructurada bajo un diseño factorial 3×3×3; *analiza* los datos con métodos estadísticos y de aprendizaje automático; y *comunica* los resultados mediante tableros. No se trata de una investigación orientada a la instalación permanente de una red, sino a la validación de un método de medición y de predicción.

**Alcance tecnológico.** Se evalúa exclusivamente el enlace Wi-Fi IEEE 802.11 en la banda ISM de 2,4 GHz y el transporte MQTT sobre TCP/IP. Quedan fuera de alcance las tecnologías de área personal (IEEE 802.15.4, Bluetooth Low Energy), las bandas de 5 y 6 GHz, los mecanismos de planificación de capa física (MIMO de alto orden, modulation coding scheme adaptativo gestionado por terceros), las redes mesh de salto múltiple y los protocolos alternativos de transporte (CoAP, AMQP), cuyo estudio se postula como línea futura.

**Alcance espacial.** Se limita a interiores de una o dos plantas, con propagación intra-planta; no se evalúa penetración entre pisos ni escenarios exteriores.

**Alcance de densidad.** La densidad de nodos se mantiene constante y de valor moderado para aislar el efecto de los tres factores ensayados; el efecto de la densidad como factor adicional queda explícitamente fuera del alcance de esta iteración y se propone como extensión del diseño a un factorial de cuatro factores.

**Alcance de seguridad y privacidad.** No se evalúa el desempeño de los mecanismos de cifrado ni se incorporan ataques o condiciones adversariales; se garantiza, en cambio, que la captura de datos se limite a métricas de red y de radiofrecuencia, sin registro de contenido.

**Alcance de viabilidad económica.** Se reporta la estimación de costo por nodo y de la ausencia de infraestructura centralizada como argumento de viabilidad, sin llevar a cabo un estudio de costo-vida útil ni una comparación de mercado exhaustiva.

**Alcance temporal.** Corresponde al periodo de ejecución previsto en el cronograma del plan de tesis, organizado en las cinco fases descritas en el apartado 3.1.4.

## 3.7. Propuesta de Validación

La validación de la propuesta se estructura sobre cuatro mecanismos complementarios que garantizan la rigurosidad científica de los resultados:

1. **Validación instrumental.** Contraste del RSSI reportado por el ESP32 contra un instrumento independiente; verificación de la sincronización de relojes; medición de referencia en trayecto conocido antes y después de la campaña. Toda discrepancia superior al tolerancia declarado se corrige antes de iniciar la recolección.
2. **Validación experimental.** Replicabilidad: cada celda se ejecuta en un mínimo de tres réplicas con orden aleatorizado; los tres registros (nodo, suscriptor, *broker*) se triangulan para cada mensaje; las condiciones de ensayo se documentan de modo que una tercera parte pudiera reproducir la campaña.
3. **Validación estadística.** Verificación explícita de los supuestos del ANOVA, reporte de tamaños de efecto e intervalos de confianza, corrección por comparaciones múltiples y, para el modelado, partición entrenamiento–prueba con validación cruzada y fijación de semillas aleatorias para la reproducibilidad.
4. **Validación de utilidad.** Contrastación del instrumento frente a una línea base: el mismo enlace evaluado sin la instrumentación cruzada y las métricas que una operación convencional reportaría, de modo que se demuestre que el prototipo aporta información adicional utilizable. La capa de tableros se somete a verificación de coherencia: cada indicador visualizado debe poder rastrearse hasta la celda experimental y al registro original que lo sustenta.

Adicionalmente, se prevé una *revisión de hallazgos* con el asesor antes del procesamiento final, con el fin de confirmar que la interpretación de los resultados se mantiene dentro del marco hipotético planteado y que el plan de contingencia, en caso de activarse, se ejecuta conforme a los cinco pasos establecidos y en el orden fijado.
