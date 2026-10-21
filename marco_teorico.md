# CAPÍTULO II: MARCO TEÓRICO Y CONCEPTUAL

El presente capítulo sustenta teóricamente la investigación. Se inicia con los antecedentes de trabajos previos relacionados (2.1); continúa con el desarrollo profundo de la base teórica que sustenta cada una de las preguntas de investigación —calidad de servicio, Wi-Fi IEEE 802.11, propagación en interiores, MQTT y Machine Learning— (2.2); procede al estado del arte organizado por enfoques y cierra con el párrafo de vacío que delimita la contribución pretendida (2.3); explicita el marco conceptual o glosario rector (2.4) y finaliza con la normatividad estrictamente pertinente al objeto de estudio (2.5).

## 2.1. Antecedentes de la Investigación

Los antecedentes se presentan diferenciados por enfoque, con el propósito de mostrar el estado real del avance sobre el problema principal y la distancia que separa a los trabajos existentes de la propuesta formulada en este documento.

### 2.1.1. Antecedentes sobre caracterización y modelado de la propagación en interiores

Chrysikos, Georgopoulos y Kotsopoulos (2009) realizaron una validación específica del sitio del modelo de pérdida de la Unión Internacional de Telecomunicaciones (ITU) a 2,4 GHz, a partir de mediciones adquiridas en un entorno de oficina inalámbrica (*WLAN*). Los autores lograron un ajuste numérico del modelo ITU de carácter general al sitio particular, obteniendo valores de los parámetros del modelo correspondientes a esa banda de frecuencia, con el propósito de mejorar la precisión del presupuesto de enlace en redes inalámbricas locales. Su aporte evidencia que los modelos de referencia públicos requieren recalibración local para ser utilizados como herramienta de diseño.

Solahuddin y Mardeni (2011) desarrollaron un modelo empírico de pérdida para redes IEEE 802.11n a 2,4 GHz en un edificio académico, comparando el desempeño de los modelos de doble pendiente, segmentado, de sombreado log-normal, ITU-R P.1238-1, Motley-Keenan ajustado y COST 231 de múltiples paredes. Concluyeron que el modelo segmentado ofrecía la mejor estimación de señal y lo tomaron como referencia para una optimización posterior. Mardeni y Solahuddin (2012) continuaron ese trabajo, reportando que el modelo mejorado reducía el error medio de predicción respecto del modelo original y que la validación en un edificio de oficinas distinto mantenía la precisión obtenida.

Kaddouri, El Hajj, Zaharia y El Zein (2018) efectuaron mediciones extensas de pérdida de trayecto en una oficina de planta abierta a 2,4 GHz y 5,8 GHz, cubriendo combinaciones de posición y altura transmisor–receptor en visibilidad directa y sin visibilidad directa, y realizaron una segunda campaña para cuantificar el efecto de la movilidad de las personas. Reportaron que la presencia de las personas incrementa la pérdida media del trayecto y que los exponentes de pérdida obtenidos difieren según la configuración de medición, además de contrastar sus resultados con los valores de la recomendación ITU-R P.1238.

Rath, Timmadasari, Panigrahi y Simha (2017) propusieron un modelo estadístico de pérdida en interiores para operaciones regulares de Wi-Fi en la banda de 2,4 a 2,5 GHz, validado mediante campañas de medición en oficinas con distintas condiciones (espacio ocupado, oficina abierta, pasillo, comedor y locales de varios pisos). Compararon su modelo con el de ITU-R y con el de distancia logarítmica, reportando mejor ajuste de su propuesta a los datos experimentales y destacando que los exponentes de pérdida varían de forma significativa entre pasillos y espacios abiertos debido a la multipropagación y a las reflexiones.

[INSERTAR AQUÍ TABLA: Cuadro comparativo de antecedentes de propagación en interiores — autores, banda, modelo evaluado y hallazgo clave]

### 2.1.2. Antecedentes sobre medición experimental del desempeño Wi-Fi y del QoS de protocolos de aplicación

Dianu, Riihijärvi y Petrova (2014) presentaron un estudio basado en mediciones del desempeño del estándar Wi-Fi IEEE 802.11ac en un entorno interior típico de oficina. Observaron que las mejoras de desempeño respecto de 802.11n son sensibles a las condiciones del canal —con caída rápida de las tasas de datos al aumentar la distancia— y que, mientras la interferencia de canal adyacente proveniente de equipos legados tiene un impacto severo, el mecanismo de acceso al medio permite compartir el canal de manera efectiva cuando la interferencia es de canal coexistente.

Fiehe, Riihijärvi y Mähönen (2010) llevaron a cabo campañas de medición extensas de IEEE 802.11n en entornos de oficina controlados e interferidos. Reportaron que el rendimiento teórico no se alcanza en la práctica, que 802.11n tolera de manera razonable la interferencia proveniente de otras tecnologías de la banda ISM de 2,4 GHz, pero que interferentes estrechos de potencia suficiente y equipos legados en la misma región de espectro degradan de manera notable el desempeño.

Miaoudakis, Stratakis, Antonidakis, Zaharopoulos y Stojanovic (2009) evaluaron mediante mediciones reales la coexistencia de redes inalámbricas locales y de área personal en una oficina típica, considerando interferencia 802.11–802.11 en canales solapados y no solapados y la interferencia Bluetooth sobre 802.11. Reportaron degradaciones importantes de rendimiento y aumentos de la latencia de ida y vuelta cuando los canales se solapan, y degradación residual aun en canales no solapados.

van Bloem, Schiphorst, Kluwer y Slump (2012) desarrollaron una herramienta de medición de la influencia de distintas fuentes de interferencia sobre enlaces de comunicación IEEE 802.11, analizando la capa física y la capa de enlace para evaluar el impacto conjunto sobre la calidad de servicio. Sus resultados mostraron que ciertos interferentes producen degradación severa del QoS del Wi-Fi, y que el análisis a nivel de tramas permite identificar el mecanismo de interferencia con mayor detalle que las herramientas tradicionales centradas únicamente en rendimiento y tasa de error de paquetes.

Parastar y Wang (2020) estudiaron experimentalmente la calidad de servicio en redes IEEE 802.11, poniendo énfasis en el mecanismo de acceso mejorado EDCA propuesto por IEEE 802.11e y en la influencia de sus parámetros (AIFS y TXOP) sobre el retardo, empleando para ello una plataforma real con redes definidas por software, en contraposición a los estudios mayoritariamente basados en simulación.

En el plano de los protocolos de aplicación, Hijazi, Habaebi, Al-Haddad y Mohammed Zyoud realizaron una prueba de estrés de un servidor MQTT en una infraestructura de red privada de IoT, analizando retardo, jitter, pérdida de paquetes y rendimiento en escenarios de tiempo real y no tiempo real para los tres niveles de servicio MQTT. Reportaron que el retardo crece de forma marcada con la carga, que el nivel QoS 0 presenta los menores retardos por ausencia de confirmaciones y que los niveles QoS 1 y QoS 2 intercambian sobrecarga de control por mayor confiabilidad de entrega.

Akbar, Amron, Mulya y Hanifah (2017) revisaron la implementación del protocolo MQTT para la comunicación en redes de sensores inalámbricas, midiendo el proceso de descubrimiento de puerta de enlace, la pérdida de paquetes en QoS 0, la duplicación de datos y los reintentos en QoS 1 y 2, y el tiempo de ida y vuelta en los niveles confirmados, concluyendo que el nivel de servicio elegido determina explícitamente el compromiso entre velocidad y confiabilidad de la entrega.

Nikfarjam Nashtifani (2026) midió experimentalmente la latencia en sistemas IoT de pequeña escala construidos con nodos ESP32 que publican por MQTT sobre Wi-Fi en interiores, sincronizando los relojes mediante NTP para obtener retardos de ida y vuelta de un solo sentido y de ida y vuelta, en distintas distancias de comunicación y en los niveles de QoS 0 y 1. Concluyó que las condiciones de la red Wi-Fi y la arquitectura de comunicación influyen en la latencia en mayor medida que las limitaciones de proceso del microcontrolador, y que el nivel QoS 1 incrementa el retardo y el jitter respecto de QoS 0.

Chen y Kunz, por su parte, compararon experimentalmente protocolos de IoT bajo una red inalámbrica de acceso con restricciones de ancho de banda, retardo y pérdida, evidenciando que el comportamiento de MQTT ante la pérdida de paquetes y la reducción de capacidad del enlace lo distancia del desempeño de alternativas orientadas a la mensajería de baja latencia.

[INSERTAR AQUÍ TABLA: Cuadro comparativo de antecedentes de medición Wi-Fi y QoS MQTT — autores, protocolo, métricas y hallazgo]

### 2.1.3. Antecedentes sobre Machine Learning aplicado a la predicción de QoS y al estado de los enlaces

Pawar, Jadhav, Lokhande, Raskar y Patil (2023) evaluaron los parámetros de calidad de servicio de la comunicación MQTT en aplicaciones de IoT mediante una red neuronal profunda, con el propósito de anticipar el comportamiento del enlace a partir de series de indicadores de red.

Hameed (2023) planteó un marco de modelado de tráfico y predicción de QoS mediante técnicas de aprendizaje profundo avanzado, formulando la predicción de indicadores como problema de pronóstico de series temporales univariadas y multivariadas y validando la propuesta con datos de tráfico de aplicaciones IoT reales sobre acceso IEEE 802.15.4.

Çoğay, Akkoç y Seçinti (2024) propusieron un marco de enrutamiento dinámico multiproto asistido por Machine Learning en el que un clasificador de paquetes basado en métodos de ensamble selecciona las rutas de acuerdo con la carga y el estado de los enlaces, evaluando la clasificación con métricas F1 y el enrutamiento en el simulador NS-3 mediante razones de entrega de paquetes y rendimiento.

Ávalos-Arce, Pérez-Díaz, Del-Valle-Soto y Briseño (2024) investigaron las limitaciones de los modelos de predicción del estado de paquetes en redes inalámbricas IEEE 802.15.4 sometidas a distintas interferencias, entrenando varios clasificadores supervisados con características extraídas de la captura de tramas. Reportaron que los atributos de fortaleza de red y de tamaño de paquete resultan predictores dominantes y que los métodos de ensamble (refuerzo de gradiente y bosques aleatorios) obtienen el mejor desempeño frente a métodos lineales y basados en vectores de soporte.

Yazici y Güreş (2024) predijeron indicadores de QoS —razón de entrega de paquetes y rendimiento— en escenarios inalámbricos empleando múltiples métodos de Machine Learning con un esquema de validación cruzada anidada que evita la fuga de información entre la selección de parámetros y la evaluación; encontraron que los métodos de ensamble, y en particular los bosques aleatorios, ofrecen el mejor compromiso de error y coeficiente de determinación.

Becvar, Plachy, Mach, Nikolov y Gesbert (2024) abordaron la predicción de la calidad de canal con Machine Learning, desde el concepto hasta la validación experimental, en un trabajo que subraya la brecha entre el desempeño reportado en condiciones controladas y el alcanzado en condiciones operativas reales.

Benadji, Zitoune y Vèque (2023) propusieron la predicción de la razón de pérdida de paquetes como indicador de congestión en redes IoT mediante modelos de aprendizaje profundo y ventanas deslizantes sobre series temporales, con el fin de sustituir la reacción tardía a la congestión por una anticipación basada en datos.

[INSERTAR AQUÍ TABLA: Cuadro comparativo de antecedentes de Machine Learning para predicción de QoS — autores, método, predictores y métricas]

### 2.1.4. Antecedentes sobre monitoreo, visualización y tableros de indicadores

Ehrlich, Neumann, Biendarra y Jasperneite (2019) abordaron el monitoreo de la calidad de servicio en redes de comunicación industriales híbridas, analizando los métodos disponibles de extracción de información del tráfico y su aprovechamiento por los sistemas de gestión de red, en un contexto donde la visibilidad del estado de la red es condición para la toma de decisiones de configuración.

Calderon, del Campo, Saavedra y Santamaría (2023) implementaron y evaluaron el desempeño de una plataforma IoT modular de arquitectura distribuida que combina herramientas de la familia Elastic con Apache Kafka, incluyendo un marco de monitoreo basado en agentes que supervisa la plataforma con arreglo a métricas definidas y la complementa con interfaces de visualización para facilitar el despliegue, la gestión y el mantenimiento.

Praja, Tahir, Cahyani, Zahroeva, Anam y Prameswari (2025) desarrollaron un sistema de monitoreo y registro del tráfico Wi-Fi de aulas universitarias mediante captura de paquetes con Wireshark y su visualización interactiva en Power BI, identificando patrones de uso, tráfico dominante y anomalías potenciales a partir de los datos capturados.

### 2.1.5. Síntesis de los antecedentes

Los antecedentes descritos cubren, de manera conjunta, los cuatro frentes que la investigación moviliza: la caracterización física del canal, la medición experimental del desempeño Wi-Fi y de los protocolos de aplicación, la predicción del comportamiento del enlace mediante aprendizaje automático y la visualización de indicadores para la toma de decisiones. Sin embargo, cada conjunto de trabajos desarrolla su aporte de manera aislada respecto de los otros: los trabajos de propagación entregan modelos de atenuación sin vincularlos con métricas de QoS de aplicación; los de medición de protocolos entregan métricas sin modelar su dependencia de las variables físicas; los de Machine Learning predicen indicadores sin instrumentar de forma simultánea el plano físico con hardware de bajo costo; y los de visualización presentan tableros sin corresponder a modelos predictivos validados experimentalmente.

[INSERTAR AQUÍ TABLA: Matriz de vacío de investigación — cobertura de los cuatro frentes en la literatura frente a la propuesta]

## 2.2. Marco Teórico

### 2.2.1. Calidad de Servicio (QoS)

La Recomendación ITU-T E.800 define la calidad de servicio como el *conjunto de efectos de un servicio que condicionan la satisfacción del usuario del mismo*. La definición, deliberadamente amplia, tiene una consecuencia práctica decisiva para la ingeniería: para que la QoS sea gestionable debe traducirse en *indicadores medibles* (KPI) relacionados con la percepción del usuario o con el cumplimiento de acuerdos de nivel de servicio. De esta manera, la QoS opera en tres planos diferenciados: el plano del usuario (percepción subjetiva), el plano del servicio (parámetros contractuales) y el plano de la red (magnitudes técnicas observables en los equipos). La investigación se sitúa en el tercer plano, como fuente de evidencia que sustenta los dos anteriores.

Las magnitudes técnicas empleadas en este trabajo se definen con precisión operacional:

- **Latencia extremo a extremo (*end-to-end delay*).** Tiempo transcurrido entre la emisión de un mensaje por el nodo publicador y su recepción efectiva por el suscriptor, incluyendo el tiempo de acceso al medio Wi-Fi, la cola de espera en el *broker* y el procesamiento de los extremos. La Recomendación ITU-T G.114 establece que un retardo de ida de hasta 150 ms es prácticamente imperceptible para la mayoría de los usuarios en aplicaciones interactivas, mientras que por encima de 400 ms resulta generalmente inaceptable; este rango se utiliza en la investigación como referencia interpretativa, no como umbral de éxito.
- **Jitter o variación del retardo.** Dispersión estadística de los retardos de entrega consecutivos, típicamente expresada como la desviación típica de la serie de retardos o como la diferencia de retardo de paquetes (IPDV, definido en la RFC 3393). Un jitter elevado degrada las aplicaciones basadas en flujo continuo aun cuando la latencia media sea aceptable.
- **Razón de entrega de tramas (PDR, *Packet Delivery Ratio*).** Cociente entre el número de mensajes recibidos correctamente y el número de mensajes publicados, expresado en porcentaje. Es el indicador binario de confiabilidad de extremo a extremo y el natural para expresar el umbral del 85% adoptado en la investigación.
- **Pérdida de paquetes.** Complemento probabilístico de la PDR, asociada a colisiones en el medio, a desbordamiento de colas, a degradación del enlace físico y a desconexiones temporales.
- **Buen uso (*goodput*).** Cantidad de carga útil entregada por unidad de tiempo, excluyendo las cabeceras, las confirmaciones y los mensajes retransmitidos; permite distinguir el rendimiento aparente del rendimiento efectivamente aprovechable por la aplicación.
- **Índices de radiofrecuencia.** RSSI (*Received Signal Strength Indicator*), SNR (*Signal-to-Noise Ratio*), nivel de ruido de fondo y, cuando el controlador lo expone, la tasa de error estimada. Constituyen la familia de *variables físicas* del modelo de correlación.

Conviene subrayar que la QoS es una propiedad *emergente* del sistema completo: no se explica por la calidad del punto de acceso, ni por el ancho de banda contratado, ni por el protocolo de aplicación considerados aisladamente, sino por la interacción entre el canal de propagación, el mecanismo de acceso al medio y la semántica de confirmación del protocolo de transporte de mensajes. Esta característica justifica formalmente el enfoque transversal de la investigación.

[INSERTAR AQUÍ TABLA: Definición operacional de las métricas de QoS empleadas — latencia, jitter, PDR, pérdida y buen uso, con unidad y referencia normativa]

### 2.2.2. Wi-Fi IEEE 802.11: acceso al medio y parámetros de operación

La familia de estándares IEEE 802.11 define las capas física y de enlace para redes inalámbricas locales (WLAN). En la banda ISM de 2,4 GHz operan las variantes 802.11b, 802.11g y 802.11n, esta última con modulaciones OFDM, canales de 20 y 40 MHz y opciones de espacial *Multiple-Input Multiple-Output*; las variantes 802.11ac y 802.11ax operan predominantemente en la banda de 5 GHz y, en el caso de 802.11ax, también en 6 GHz. Los canales de 20 MHz en 2,4 GHz se solapan entre sí, de modo que únicamente tres canales son mutuamente no solapados (típicamente los canales 1, 6 y 11), condición que constituye una restricción de diseño de primer orden en instalaciones con múltiples puntos de acceso y con presencia de redes vecinas.

En la capa de enlace, el mecanismo básico de acceso distribuido (DCF, *Distributed Coordination Function*) implementa un procedimiento de acceso al medio por detección de portadora con evitación de colisiones (CSMA/CA). Antes de transmitir, la estación verifica que el medio esté inactivo durante un intervalo de escucha extendida; si el medio está ocupado o si se produce una colisión, difiere la transmisión mediante un *retroceso exponencial binario*: la estación selecciona aleatoriamente un entero dentro de una ventana de contienda cuyo tamaño se duplica hasta alcanzar un límite máximo, y vuelve a intentar el acceso. Este mecanismo se modela analíticamente mediante cadenas de Markov de dos dimensiones, en la formulación clásica de Bianchi (2000), que permite derivar expresiones de la probabilidad de transmisión condicionada, la probabilidad de colisión y la tasa de éxito de tramas en función de los parámetros de la ventana de contienda y del número de estaciones activas.

Tres consecuencias de este diseño son directamente relevantes para la investigación:

1. **Sensibilidad a la densidad y a la carga.** A medida que el número de emisores activos o la tasa de ofrecimiento aumentan, la probabilidad de colisión crece de manera no lineal y la ventana de contienda se expande, elevando la latencia y reduciendo el buen uso. La congestión, por tanto, no es únicamente un fenómeno de red, sino un fenómeno del propio mecanismo de acceso.
2. **Sensibilidad a la calidad del canal.** Los mecanismos de sondeo de portadora, la selección de la tasa de modulación y codificación y las retransmisiones enlace a enlace reaccionan al RSSI y al SNR; una degradación física se traduce en aumento de la tasa de error, mayor número de reintentos y, en consecuencia, mayor jitter y menor PDR. Es aquí donde las variables físicas y las variables de red se acoplan.
3. **Sobrecarga y asimetría de interferencias.** La banda de 2,4 GHz es compartida con Bluetooth, Zigbee, cámaras inalámbricas, enlaces de audio y video y equipos vecinos no coordinados. Las interferencias de canal adyacente suelen ser más dañinas que las de canal coexistente, por cuanto el mecanismo de acceso puede coordinarse únicamente con las estaciones que perciben el mismo canal.

Para dar respuesta a las aplicaciones con requerimientos diferenciados, IEEE 802.11e introdujo el mecanismo EDCA (*Enhanced Distributed Channel Access*), comercializado como WMM, que sustituye una única cola de contienda por cuatro categorías de acceso con parámetros de escucha, ventana de retroceso y duración de transmisión diferenciados, permitiendo priorizar el tráfico de voz, vídeo, *best effort* y de fondo. EDCA no garantiza QoS, sino que la *diferencia*: la garantía efectiva sigue dependiendo del canal y de la carga, lo que mantiene vigente la necesidad de medición experimental.

[INSERTAR AQUÍ FLUJOGRAMA DE: Mecanismo DCF/CSMA/CA con retroceso exponencial binario y su interacción con la calidad del canal (cross-layer)]

### 2.2.3. Propagación en interiores

El canal inalámbrico interior se caracteriza por tres fenómenos dominantes: la *pérdida de trayecto* asociada a la expansión de la onda, la *atenuación por obstáculos* —muros, tabiques, mobiliario, conductos y cuerpos humanos— y el *desvanecimiento por multipropagación*, causado por la interferencia entre las múltiples copias de la señal que llegan al receptor por reflexión, difracción y dispersión. Cuando el receptor recibe una componente dominante acompañada de un conjunto de componentes dispersas, el desvanecimiento se describe con distribución Rician parametrizada por el factor K; en ausencia de componente dominante, corresponde a la distribución de Rayleigh; la familia Nakagami-*m* generaliza ambos casos. Sobre la envolvente de potencia media se superpone el *desvanecimiento por sombra*, de distribución log-normal, que captura la variación lenta de la atenuación por el desplazamiento respecto de los obstáculos.

El modelo de pérdida de trayecto de distancia logarítmica constituye la herramienta de trabajo por excelencia de la investigación:

PL(d) = PL(d₀) + 10 · n · log₁₀(d / d₀) + X<sub>σ</sub>

donde PL(d) es la pérdida de trayecto en decibelios a la distancia d, d₀ es una distancia de referencia, n es el exponente de pérdida de trayecto y X<sub>σ</sub> es una variable aleatoria gaussiana de desviación típica σ que representa el desvanecimiento por sombra. La Recomendación ITU-R P.1238 proporciona una formulación específica para interiores de la forma L = 20 log₁₀(f) + N log₁₀(d) + L<sub>f</sub>(n) − 28 dB, donde f es la frecuencia en megahercios, d la separación en metros, N el coeficiente de pérdida de distancia y L<sub>f</sub>(n) la pérdida por penetración de plantas, con valores tabulados de N para contextos residenciales, de oficina y comercial. Los modelos de múltiples paredes, en la línea de Motley-Keenan, añaden un término sumatorio que contabiliza el número y el tipo de materiales atraviesados por el trayecto.

Dos cuestiones de ingeniería condicionan el aprovechamiento de estos modelos en la investigación:

- **Calibración local.** Los coeficientes N, σ y las pérdidas por material son específicos del edificio y de la banda. Los antecedentes revisados coinciden en que el modelo general debe ajustarse a las mediciones del sitio antes de emplearse como herramienta de predicción, y que el ajuste reduce el error de predicción de forma apreciable.
- **Adecuación al instrumento.** El prototipo basado en ESP32 no dispone de instrumentación de canal complejo; expone fundamentalmente el RSSI del controlador Wi-Fi, a partir del cual es posible estimar el nivel de potencia recibida y el ruido de fondo. Por ello, la caracterización se plantea en términos de magnitudes *observables* con el hardware disponible, y la fidelidad del modelo se evalúa por su capacidad de reproducir la tendencia y la dispersión de esas observaciones, no por su capacidad de reconstruir el campo electromagnético completo.

La multipropagación posee además una consecuencia no lineal que justifica el enfoque de aprendizaje automático: el RSSI no disminuye monotónicamente con la distancia en escenarios cerrados, ya que las interferencias constructivas y destructivas producen máximos y mínimos locales. Un modelo lineal simple captura la tendencia global, pero no el comportamiento local que condiciona la calidad del enlace a distancias cortas.

[INSERTAR AQUÍ TABLA: Cuadro comparativo de modelos de propagación en interiores — ITU-R P.1238 vs Motley-Keenan vs log-distance vs modelos estocásticos (Rayleigh, Rician, Nakagami-m)]

### 2.2.4. MQTT y la arquitectura de transporte de mensajes IoT

MQTT (*Message Queuing Telemetry Transport*) es un protocolo de mensajería ligero basado en el paradigma publicación–suscripción, definido como estándar por OASIS (versión 3.1.1 en 2014 y versión 5.0 en 2019) y concebido para entornos de recursos limitados y enlaces de baja fiabilidad. Su arquitectura se organiza en tres entidades: el *cliente publicador*, que envía mensajes a un *tema* (*topic*) jerárquico; el *cliente suscriptor*, que se suscribe a temas de interés; y el *broker* (servidor de mensajería), que mantiene las sesiones, enruta los mensajes y gestiona las confirmaciones. La separación entre publicadores y suscriptores elimina la necesidad de que los extremos se conozcan mutuamente, lo que simplifica el despliegue de nodos IoT y habilita la incorporación de nuevos consumidores de datos —como la base de datos de la investigación y la capa de tableros— sin modificar la configuración de los emisores.

El protocolo define tres niveles de servicio que constituyen el eje de la variable experimental "nivel de QoS":

- **QoS 0 (al menos una vez, *at most once*).** Entrega sin confirmación: el mensaje se envía una sola vez y no se retransmite. Es el nivel más rápido y de menor sobrecarga, pero no garantiza la recepción ni la no duplicación.
- **QoS 1 (al menos una vez).** Entrega con confirmación de recibido (PUBACK): el emisor retransmite hasta recibir la confirmación, lo que garantiza la entrega al menos una vez, a costa de mayor latencia, mayor consumo de ancho de banda y posibilidad de duplicados.
- **QoS 2 (exactamente una vez).** Ciclo completo de cuatro mensajes (PUBREC/PUBREL/PUBCOMP) que evita la duplicación mediante control explícito de identificadores de paquete. Es el nivel con mayor sobrecarga de control y el mayor tiempo de entrega.

A los niveles de servicio se suman parámetros de sesión con impacto directo en las métricas: el intervalo de *keep alive* (que determina la detección de desconexión), el indicador de sesión limpia (que decide la recuperación de mensajes pendientes), el tiempo de caducidad de sesión, el tamaño máximo de carga útil y el uso de marcas de retención (*retain*) y de mensajes de último valor conocido (*last will*). La versión 5.0 añade *reason codes*, *acknowledgements* diferidos y propiedades de mensaje que permiten afinar el control de flujo y la depuración, características que se consideran en la elección del *broker*.

La elección de MQTT como protocolo de la investigación obedece a tres razones de ingeniería: es el protocolo de facto del IoT sobre IP, dispone de implementaciones de *broker* ligeras y de código abierto utilizables en una estación de adquisición local, y expone de forma explícita y configurable el compromiso entre confiabilidad y sobrecaba, lo que lo convierte en un factor experimental manipulable directamente. Sobre Wi-Fi, MQTT opera sobre TCP, de modo que la latencia extremo a extremo acumula el tiempo de acceso al medio inalámbrico, la ventana de contienda, las retransmisiones TCP y el ciclo de confirmación MQTT: el valor medido es, por construcción, una magnitud *transversal* que integra la pila completa.

El ESP32 constituye la plataforma de nodo elegida por su integración nativa de interfaz Wi-Fi IEEE 802.11 b/g/n y Bluetooth, su capacidad de operar como estación y como punto de acceso, su costo reducido, la disponibilidad de bibliotecas MQTT maduras y su perfil de consumo compatible con alimentación por bus o por batería de mediana duración. El prototipo emplea el ESP32 tanto como nodo publicador como instrumentador de los índices de radiofrecuencia, aprovechando la interfaz de estado del controlador Wi-Fi para obtener RSSI y nivel de ruido en cada publicación.

[INSERTAR AQUÍ FLUJOGRAMA DE: Modelo Publish-Subscribe de MQTT con flujos de confirmación de los niveles QoS 0, 1 y 2]

### 2.2.5. Machine Learning aplicado a la evaluación de redes

El aprendizaje automático comprende los métodos que permiten a un sistema mejorar su desempeño a partir de la experiencia, en oposición a la programación explícita de reglas. La investigación se circunscribe al *aprendizaje supervisado*, en el que se dispone de un conjunto de datos de entrada **X** (predictores) y de una variable objetivo **y** (respuesta) y se busca la función f : **X** → **y** que generalice a datos no observados. En el problema planteado se formulan dos tareas complementarias:

- **Clasificación.** La variable objetivo es discreta: por ejemplo, si la combinación experimental cumple o no cumple el umbral del 85% en la métrica de referencia (PDR), o el estado de QoS codificado como adecuado / degradado / crítico.
- **Regresión.** La variable objetivo es continua: la predicción de la latencia, del jitter o del buen uso a partir de los índices de radiofrecuencia y de las condiciones de operación.

Las familias de algoritmos consideradas se seleccionan por su idoneidad con conjuntos de datos tabulares de tamaño moderado y por su interpretabilidad:

- **Regresión lineal con regularización (Ridge y Lasso).** Proporcionan una línea base de referencia, cuantifican la asociación lineal entre cada predictor y la respuesta y, mediante la penalización, permiten reducir la varianza de las estimaciones e identificar predictores poco informativos.
- **Árbol de decisión.** Modelan relaciones no lineales e interacciones por particiones sucesivas del espacio de predictores; su lectura es directa, pero presentan varianza alta y tendencia al sobreajuste cuando se profundiza el árbol.
- **Bosques aleatorios y otros ensambles (*gradient boosting*).** Combina múltiples árboles entrenados sobre muestras y subconjuntos de atributos, reduciendo la varianza sin incrementar proporcionalmente el sesgo; se reportan ampliamente como los de mejor desempeño en problemas de predicción de estado de enlaces e indicadores de red.
- **Métodos lineales logísticos para clasificación.** Actúan como modelo de referencia interpretable ante problemas binarios.

La evaluación de los modelos se guía por principios que la investigación adopta de forma explícita:

1. **Separación entre entrenamiento y prueba.** Los datos se particionan, con estratificación cuando las clases están desequilibradas, de modo que la evaluación final se realice sobre observaciones no vistas durante el ajuste.
2. **Validación cruzada en *k* pliegues.** Permite estimar la varianza del desempeño y detectar inestabilidad del modelo; en problemas con búsqueda de hiperparámetros se prefiere el esquema anidado, que evita la *fuga* de información entre la selección de configuraciones y la evaluación.
3. **Métricas acordes al desbalance de clases.** Además de la exactitud, se emplean precisión, sensibilidad, especificidad, *F*1 y el área bajo la curva ROC; para la regresión, el error absoluto medio, la raíz del error cuadrático medio y el coeficiente de determinación.
4. **Interpretabilidad.** El análisis de importancia de atributos y las correlaciones parciales se emplean para traducir el modelo al lenguaje físico de la ingeniería: si el RSSI, la carga de tráfico y el nivel de QoS no aparecen entre los predictores dominantes, el modelo será cuestionado aun con métricas elevadas.
5. **Reproducibilidad.** La fijación de semillas aleatorias, la versionación del conjunto de datos y la conservación del *pipeline* completo de preprocesamiento y modelado forman parte del protocolo experimental.

La biblioteca Scikit-learn (Pedregosa y otros, 2011) se elige como entorno de implementación por su madurez, su disponibilidad de código abierto, su coherencia de API entre preprocesamiento, selección de modelos y métricas, y su compatibilidad con el ecosistema de análisis de datos empleado en la investigación.

[INSERTAR AQUÍ FLUJOGRAMA DE: Pipeline de evaluación de modelos de Machine Learning — partición, validación cruzada en k pliegues, métricas e interpretabilidad]

## 2.3. Estado del Arte

El estado del arte se organiza por enfoques, de modo que cada frente de trabajo aparezca con su alcance real, sus resultados consolidados y sus límites.

### Enfoque 1: Modelado y calibración de la propagación en interiores

Las campañas de medición realizadas en oficinas, edificios académicos y locales comerciales a 2,4 GHz han consolidado un conjunto de conocimientos estables: el exponente de pérdida de trayecto varía significativamente entre espacios abiertos, pasillos y ambientes con tabiquería; la presencia de personas incrementa de forma medible la atenuación media; los coeficientes de las recomendaciones generales deben ajustarse al sitio para reducir el error de predicción; y los modelos de múltiples paredes superan a los modelos de distancia simple cuando el trayecto atraviesa obstáculos identificables (Chrysikos y otros, 2009; Solahuddin y Mardeni, 2011; Mardeni y Solahuddin, 2012; Kaddouri y otros, 2018; Rath y otros, 2017). Este enfoque alcanza, por tanto, un grado de madurez alto en lo que respecta a la *estimación de atenuación*. Su límite reside en que las variables resultantes rara vez se vinculan de manera simultánea con indicadores de QoS de aplicación medidos en el mismo experimento.

### Enfoque 2: Medición experimental del desempeño Wi-Fi y de los protocolos de aplicación

Las mediciones de campo sobre IEEE 802.11n y 802.11ac en oficinas han demostrado que las tasas teóricas no se alcanzan en la práctica, que el rendimiento decae con la distancia y que las interferencias de canal adyacente degradan severamente el enlace (Fiehe y otros, 2010; Dianu y otros, 2014; Miaoudakis y otros, 2009; van Bloem y otros, 2012). En paralelo, los estudios experimentales de EDCA han mostrado la influencia medible de sus parámetros sobre el retardo en plataformas reales (Parastar y Wang, 2020). Sobre la capa de aplicación, las pruebas de estrés y los bancos de ensayo con MQTT han establecido el ordenamiento cualitativo de sus niveles de servicio en términos de retardo, jitter, pérdida y sobrecarga, tanto en redes de sensores como sobre Wi-Fi con nodos ESP32 (Hijazi y otros; Akbar y otros, 2017; Nikfarjam Nashtifani, 2026; Chen y Kunz). Este enfoque entrega, así, la *línea base métrica* de la investigación: sabe cómo se comporta el protocolo aisladamente. Su límite es que las mediciones se reportan como funciones de una variable a la vez —distancia, carga o nivel de QoS— y no como un diseño factorial que permita estimar interacciones, ni acompañadas de un modelo de predicción.

### Enfoque 3: Predicción y clasificación del estado del enlace mediante Machine Learning

La tercera línea concentra los avances más recientes. Se han aplicado redes neuronales profundas a la evaluación de parámetros QoS de MQTT (Pawar y otros, 2023), modelos de series temporales y *transformers* a la predicción de indicadores de red (Hameed, 2023), métodos de ensamble a la clasificación de paquetes y al enrutamiento asistido por aprendizaje (Çoğay y otros, 2024; Ávalos-Arce y otros, 2024; Yazici y Güreş, 2024) y aprendizaje profundo a la anticipación de congestión (Benadji y otros, 2023). Los trabajos coinciden en tres hallazgos transferibles: los métodos de ensamble superan consistentemente a los métodos lineales en tareas de predicción de indicadores; la selección rigurosa de hiperparámetros con validación cruzada anidada mejora la robustez de las estimaciones; y atributos asociados a la fortaleza de enlace y a la configuración de transmisión figuran entre los predictores dominantes. El enfoque de predicción de calidad de canal con validación experimental confirma además que existe una brecha entre el desempeño obtenido en condiciones de laboratorio y el operativo (Becvar y otros, 2024). Su límite es que, en la gran mayoría de los casos, los predictores provienen de simuladores, de rastreadores de paquetes o de registros de una sola capa, y no de un instrumento propio que registre simultáneamente radiofrecuencia y aplicación en un diseño experimental controlado.

### Enfoque 4: Monitoreo, visualización y gestión de la calidad de servicio

El cuarto frente comprende los trabajos que trasladan las mediciones a la operación. Se han propuesto marcos de monitoreo de plataformas IoT con arquitecturas de streaming y visualización integrada (Calderon y otros, 2023), marcos de monitoreo de QoS en redes industriales híbridas orientados a alimentar a los sistemas de gestión (Ehrlich y otros, 2019) y, en una vertiente de menor complejidad pero alta aplicabilidad, sistemas de captura de tráfico Wi-Fi con visualización interactiva en Power BI para el análisis de uso y detección de anomalías en instalaciones educativas (Praja y otros, 2025). Este enfoque aporta el mecanismo de *traducción* entre el resultado analítico y la decisión, pero habitualmente se limita a visualizar datos ya procesados, sin corresponder a un modelo predictivo validado ni a un criterio de éxito formalizado.

### Párrafo de vacío

Del recorrido precedente se desprende que la literatura disponible ofrece, de manera separada, (i) modelos de propagación en interiores calibrables pero desconectados de las métricas de calidad de servicio; (ii) mediciones experimentales del comportamiento Wi-Fi y de los niveles de servicio MQTT que carecen de un diseño factorial capaz de estimar las interacciones entre propagación, carga y confiabilidad del protocolo; (iii) modelos de Machine Learning que predicen indicadores de red sobre datos de una sola capa o provenientes de simulación, sin instrumentación propia que registre simultáneamente las variables físicas y las variables dinámicas; y (iv) tableros de visualización que comunican descriptores de la red sin sustento en un modelo predictivo ni en un criterio de éxito formal. En consecuencia, **existe un vacío de investigación en la integración experimental de los cuatro frentes: no se dispone, hasta donde alcanza la revisión efectuada, de un prototipo IoT híbrido de bajo costo que, mediante una única campaña de mediciones estructurada en un diseño factorial 3×3×3, registre de forma sincronizada las variables físicas de radiofrecuencia y las variables dinámicas de red; correlacione ambas familias mediante modelos de aprendizaje automático validados; verifique un criterio de éxito explícito del 85% con un plan de contingencia predefinido; y comunique el resultado en tableros de decisión.** La presente investigación se sitúa exactamente en ese punto de intersección.

**NOTA:** Si bien los trabajos descritos en los cuatro enfoques constituyen precedentes legítimos de las técnicas empleadas, la propuesta se diferencia de ellos de manera sustancial. Frente a los estudios de propagación (Enfoque 1), no se limita a estimar atenuación, sino que utiliza la caracterización del canal como fuente de predictores de una variable de QoS. Frente a las mediciones de protocolo (Enfoque 2), no evalúa un factor aislado, sino que emplea un diseño factorial completo 3×3×3 que permite estimar efectos principales e interacciones entre escenario de propagación, carga de tráfico y nivel de servicio MQTT. Frente a los trabajos de Machine Learning (Enfoque 3), no consume datos de simuladores ni de una sola capa, sino que construye su propio instrumento de adquisición sincronizada y somete el modelo a un criterio de éxito del 85% regido por un plan de contingencia de cinco pasos. Frente a los trabajos de visualización (Enfoque 4), no presenta tableros descriptivos, sino una capa de indicadores alimentada por resultados estadísticos y predictivos previamente validados. En suma, lo que se propone hacer no es la repetición de alguno de los enfoques previos, sino su integración en un único protocolo experimental reproducible.

[INSERTAR AQUÍ FLUJOGRAMA DE: Modelo de pila de protocolos y la interacción cross-layer entre Wi-Fi IEEE 802.11 y MQTT]

## 2.4. Marco Conceptual

**Calidad de Servicio (QoS).** Conjunto de efectos de un servicio que condicionan la satisfacción del usuario (ITU-T E.800); en este trabajo, su expresión operacional corresponde al conjunto de métricas de latencia, jitter, PDR, pérdida y buen uso.

**Latencia extremo a extremo.** Tiempo transcurrido desde la emisión de un mensaje por el nodo publicador hasta su recepción efectiva por el suscriptor, incluyendo acceso al medio, cola en el *broker* y procesamiento de extremos.

**Jitter.** Variación de los retardos de entrega consecutivos; se expresa como desviación típica de la serie de retardos o como diferencia de retardo de paquetes.

**Razón de entrega de tramas (PDR).** Porcentaje de mensajes recibidos correctamente respecto del total de mensajes publicados; métrica de referencia para el umbral del 85%.

**Buen uso (*goodput*).** Carga útil entregada por unidad de tiempo, excluidas cabeceras, confirmaciones y retransmisiones.

**Banda ISM.** Bandas de radio Industrial, Científica y Médica, de uso libre sin licencia, en las que operan Wi-Fi, Bluetooth y Zigbee bajo la condición de no causar interferencias perjudiciales.

**Wi-Fi / IEEE 802.11.** Familia de estándares de las capas física y de enlace para redes inalámbricas locales; en este trabajo, la variante operativa en 2,4 GHz sobre la que se transmiten las publicaciones MQTT.

**DCF y CSMA/CA.** Función de coordinación distribuida y método de acceso al medio por detección de portadora con evitación de colisiones, base del mecanismo de acceso de IEEE 802.11.

**Retroceso exponencial binario.** Procedimiento de diferimiento aleatorio de la transmisión mediante una ventana de contienda que se duplica tras cada colisión, hasta un límite máximo.

**EDCA / WMM.** Mecanismo de acceso mejorado definido por IEEE 802.11e que diferencia cuatro categorías de tráfico con parámetros de contienda distintos; prioriza, pero no garantiza, calidad de servicio.

**Nodo no visible (*hidden node*).** Situación topológica en la que dos estaciones no perciben entre sí pero transmiten hacia el mismo punto de acceso, provocando colisiones no detectables por el sondeo de portadora.

**Multipropagación.** Llegada al receptor de múltiples copias de la señal por reflexión, difracción y dispersión, origen del desvanecimiento selectivo.

**Desvanecimiento por sombra.** Variación lenta de la potencia recibida debida a obstáculos entre transmisor y receptor; modelada como variable aleatoria gaussiana en decibelios.

**Exponente de pérdida de trayecto.** Parámetro n que cuantifica la rapidez con que la potencia decrece con la distancia en el modelo de pérdida logarítmica; en interiores su valor depende del material y de la geometría del sitio.

**RSSI.** Indicador de intensidad de señal recibida expuesto por el controlador Wi-Fi; predictor físico principal del prototipo.

**SNR.** Relación señal-ruido en el receptor; condiciona la tasa de error alcanzable y, por tanto, la selección de modulación y la necesidad de reintentos.

**MQTT.** Protocolo de mensajería ligero basado en publicación–suscripción, definido por OASIS, empleado para transportar las mediciones de los nodos hasta el *broker*.

**Tema (*topic*).** Cadena jerárquica a la que se publican o de la que se suscriben los mensajes en MQTT; estructura lógica que organiza los flujos de datos del prototipo.

**Nivel de QoS MQTT.** Grado de confiabilidad acordado entre cliente y *broker*: QoS 0 sin confirmación, QoS 1 con confirmación y QoS 2 con ciclo completo de cuatro manos.

***Broker* MQTT.** Servidor que mantiene las sesiones, enruta los mensajes entre publicadores y suscriptores y gestiona las confirmaciones.

**ESP32.** Microcontrolador de bajo costo con interfaz Wi-Fi IEEE 802.11 y Bluetooth integrado; plataforma del nodo instrumentador del prototipo.

**Prototipo IoT híbrido.** Conjunto hardware–software que integra nodos ESP32, infraestructura Wi-Fi, *broker* MQTT, base de datos y capa de análisis para la adquisición conjunta de variables físicas y de red.

**Aprendizaje supervisado.** Paradigma de Machine Learning en el que un modelo se ajusta a un conjunto de datos etiquetado para predecir una variable objetivo.

**Clasificador / regresor.** Modelo que predice una categoría discreta / una magnitud continua.

**Bosque aleatorio (*random forest*).** Método de ensamble que combina múltiples árboles de decisión entrenados sobre muestras y subconjuntos aleatorios de atributos.

**Validación cruzada en *k* pliegues.** Procedimiento de evaluación en el que el conjunto de datos se divide en *k* partes y el modelo se entrena y evalúa en rotación, estimando la capacidad de generalización.

**Exactitud, sensibilidad, precisión y *F*1.** Métricas de desempeño de un clasificador; *F*1 es la media armónica entre precisión y sensibilidad, recomendable ante clases desequilibradas.

**Diseño factorial experimental.** Plan de experimentación en el que se manipulan simultáneamente varios factores con sus respectivos niveles, permitiendo estimar efectos principales e interacciones.

**Efecto principal e interacción.** Influencia promedio de un factor sobre la respuesta; influencia conjunta de dos o más factores que no resulta de la suma de sus efectos individuales.

**Umbral del 85%.** Criterio de éxito metodológico operacionalizado: el porcentaje mínimo de cumplimiento que debe alcanzar la métrica de referencia (PDR) y la exactitud del modelo predictivo para considerar verificada la hipótesis de trabajo.

**Plan de contingencia de cinco pasos.** Procedimiento predefinido de respuesta ante resultados que no alcanzan el umbral del 85%, con pasos de verificación instrumental, re-aislamiento de causas, ampliación de evidencia, reajuste de parámetros y documentación formal de la desviación.

**Power BI.** Plataforma de inteligencia de negocio para la modelación de datos, el cálculo de medidas y la construcción de tableros interactivos con indicadores de desempeño.

**KPI y tablero.** Indicador clave de desempeño y superficie visual que lo comunica con tendencias, metas y estados de cumplimiento.

## 2.5. Normatividad y Legislación

La normatividad aplicable se limita a los documentos estrictamente pertinentes con el objeto de estudio:

**Estándares IEEE 802.11.** El estándar IEEE 802.11 y sus modificaciones (802.11n, 802.11e/EDCA, 802.11ac, 802.11ax) definen las reglas de convivencia del enlace utilizado por el prototipo: modulaciones, canales, mecanismos de acceso al medio y parámetros de contienda. Su cumplimiento es condición de que las mediciones sean comparables con las de terceros.

**Estándar OASIS MQTT.** La especificación MQTT Version 5.0 y su predecesora 3.1.1, publicadas por el consorcio OASIS, definen la semántica de los niveles de servicio, los flujos de confirmación y los parámetros de sesión cuyo efecto se mide experimentalmente.

**Recomendaciones ITU-T.** La Recomendación E.800 aporta la definición normativa de calidad de servicio; la Recomendación G.114 fija las referencias de tolerancia al retardo de ida; la serie Y.1540 establece clases de desempeño de transferencia de paquetes IP que se toman como marco interpretativo de los resultados.

**Recomendaciones ITU-R.** La Recomendación ITU-R P.1238 proporciona los modelos y parámetros de propagación en interiores empleados como línea base de comparación del modelo calibrado en el escenario de medición.

**Reglamento de Radiocomunicaciones de la Unión Internacional de Telecomunicaciones.** El Reglamento establece el régimen de las bandas ISM, de uso libre y sin licencia, bajo la condición de no causar interferencias perjudiciales a otros servicios; esta condición delimita el marco de operación del prototipo y de los equipos vecinos con los que coexiste.

**Marco de protección de datos personales.** La normativa nacional de protección de datos personales resulta pertinente en tanto la investigación opera con registros de tráfico y de estado de enlace. El protocolo experimental contempla explícitamente la recolección exclusiva de métricas de red y de radiofrecuencia, sin captura de contenido de las comunicaciones ni de datos personales de los usuarios, condición que se verifica durante la etapa de instrumentación y se declara en el informe final.

**Aspectos de seguridad.** Si bien la seguridad del transporte no constituye una variable de la investigación, la utilización de canales cifrados y de credenciales de acceso al *broker* se rige por las prácticas recomendadas en las propias especificaciones de OASIS MQTT y por la configuración segura del punto de acceso inalámbrico, con el propósito de que el tráfico experimental no introduzca sesgos ni vulnerabilidades en la red de la institución anfitriona.
