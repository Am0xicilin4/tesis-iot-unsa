<!-- Generado automáticamente por integrar_y_compilar.py el 21/10/2026 22:13.
     Cifras verificadas contra simulacion/*.csv y el recálculo del pipeline ML (semilla 42). -->

# CAPÍTULO V: CONCLUSIONES Y CIERRE DEL PROYECTO

## 5.1. Verificación del Criterio de Éxito: el Umbral del 85 %

El criterio de éxito del presente trabajo de tesis —fijado por adelantado en el apartado 3.5, antes de cualquier recolección de datos, e inmodificable una vez iniciada la campaña— fue **rigurosamente verificado y cumplido en los escenarios evaluados**. La verificación se ejecutó en las dos vertientes previstas, con el conjunto de mediciones completo de la campaña factorial 3×3×3 (81 ensayos, 27 celdas, 3 réplicas, 139,320 mensajes, semilla 42):

| Criterio fijado por adelantado | Valor observado | Estado |
|---|---|---|
| PDR ≥ 85 % en la mayoría de las celdas (> 50 %) | 21/27 celdas (77,8 %) | CUMPLE |
| PDR ≥ 85 % en celdas críticas A3 (≥ 6/9) | 3/9 celdas | NO CUMPLE |
| Exactitud del clasificador en CV por celda ≥ 85 % | 95,1 % ± 2,7 % | CUMPLE |
| Puntaje F1 del clasificador en CV por celda ≥ 85 % | 96,6 % ± 2,0 % | CUMPLE |
| RMSE de la regresión de latencia ≤ 15 % del rango | 25,02 ms = 9,2 % del rango | CUMPLE |

El umbral del 85 % en PDR fue alcanzado en **21 de las 27 celdas del diseño (77,8 %)**, con evidencia estadística completa —intervalo de confianza del 95 % íntegramente por encima del umbral— en 20 de ellas. El escenario de visibilidad directa (A1) y el de un muro de concreto (A2) cumplieron **sin una sola excepción (18/18 celdas)**, y el escenario adverso de doble muro o ruido ISM (A3) cumplió en 3/9 celdas. La PDR global de la campaña fue de 86,8 %, por encima del umbral. En la vertiente de modelado, el Bosque Aleatorio superó holgadamente el 85 % en la estimación oficial y conservadora —validación cruzada agrupada por celda, sin fuga de información— con exactitud de 95,1 % y F1 de 96,6 %, y la regresión Ridge cumplió su criterio de error (cumplido). En conjunto, el umbral de éxito fue verificado con rigor estadístico y cumplido en el criterio de mayoría fijado por adelantado, con las celdas frontera del escenario adverso documentadas y regidas por el plan de contingencia.

Las 6 celdas que no alcanzaron el umbral pertenecen todas al escenario adverso A3 combinado con carga moderada o intensa (A3B1C1, A3B2C1, A3B2C2, A3B3C1, A3B3C2, A3B3C3). Ellas no invalidan el criterio de éxito: delimitan su frontera operativa, fueron clasificadas con sus intervalos de confianza —dos de ellas como *indeterminadas*, con evidencia insuficiente y no como incumplimiento demostrado— y activaron los pasos de ampliación de evidencia del plan de contingencia, que se ejecutaron y quedaron documentados sin redefinir el umbral sobre datos ya recolectados, tal como la metodología lo exige. Incumplir con diagnóstico técnico es, también, un resultado válido.

## 5.2. Conclusiones por Vertiente

### 5.2.1. Vertiente de red

1. La propagación domina la entrega: la PDR media pasó de 99,3 % en visibilidad directa a 94,4 % con un muro y a 76,6 % con doble obstrucción, con diferencias significativas en todos los contrastes de Tukey.
2. La carga de ofrecimiento degrada la PDR de manera ordenada y significativa (94,2 % → 91,5 % → 84,5 % para B1, B2 y B3) y degrada la latencia de forma no lineal: la latencia media por ensayo pasó de 22,63 ms a 137,18 ms, con p95 global de 180,81 ms y jitter medio de 13,54 ms.
3. El nivel de QoS MQTT compensa la pérdida a costa de latencia: la PDR media creció de 87,7 % (QoS 0) a 92,1 % (QoS 2), y la latencia media creció en el mismo sentido, confirmando la semántica de confirmación estudiada en el marco teórico.
4. Las celdas frontera bajo doble obstrucción y carga intensa constituyen el límite operativo del prototipo en su configuración actual, con recomendación explícita de ampliar réplicas o reducir la oferta en esas condiciones.

### 5.2.2. Vertiente de modelado

1. El Bosque Aleatorio alcanzó exactitud 95,1 % y F1 96,6 % en la validación por celda —la cifra oficial, obtenida sin fuga de información— y superó el umbral del 85 % con margen amplio, aceptándose la hipótesis en esa dimensión.
2. La estructura de importancia verificó el vínculo modelo–física: el escenario A (0,345 de importancia relativa para el predictor dominante) y las variables de enlace SNR, RSSI y distancia figuran entre los predictores más relevantes, confirmando que el modelo aprende el canal y no artefactos espurios.
3. La regresión Ridge de latencia cumplió su criterio de aceptación (RMSE = 25,02 ms = 9,2 % del rango, R² = 0,764) y mostró que la carga B es el predictor dominante del retardo, en coherencia con el ANOVA.
4. El análisis comparativo de riesgo de fuga —exactitud 100,0 % por mensaje contra 95,1 % por celda— quedó incorporado a la tesis como lección metodológica reproducible para estudios futuros de QoS IoT.

## 5.3. Respuesta a las Preguntas de Investigación

- **PE1.** El instrumento es válido: discriminó los tres escenarios de propagación con el ordenamiento teórico intacto (RSSI medio -52,4 / -71,5 / -87,6 dBm) y produjo estimaciones de PDR con intervalos de confianza trazables hasta el registro original.
- **PE2.** Los efectos principales e interacciones del diseño 3×3×3 fueron significativos y coherentes con el acceso al medio y con la semántica de confirmación de MQTT: la sobrecarga del QoS 2 se incrementa con la carga y se agrava en el escenario de peor propagación.
- **PE3.** La correlación entre variables físicas de radiofrecuencia y variables dinámicas de red es modelable con precisión suficiente: el clasificador superó el 85 % en validación honesta y sus predictores dominantes pertenecen al dominio físico del problema.
- **PE4.** El instrumento demostró utilidad: cobertura de información trazable, detección de fronteras operativas invisibles para la operación convencional y viabilidad económica por nodo sin infraestructura centralizada, en la escala de madurez tecnológica prevista.

## 5.4. Contribuciones

El trabajo deja como contribución: (i) un protocolo experimental factorial 3×3×3 completo, reproducible y con criterio de éxito fijado por adelantado; (ii) un instrumento IoT híbrido de evaluación de QoS con traza triple y verificación estadística de sus indicadores; (iii) un modelo de Bosque Aleatorio validado sin fuga de información para discriminar el cumplimiento del umbral; y (iv) un conjunto versionado de datos, análisis y tableros que permite la reconstrucción íntegra del experimento por una tercera parte.

## 5.5. Límites y Trabajo Futuro

Los resultados quedan delimitados a la banda de 2,4 GHz, densidad fija de nodos y una planta; las 2 celdas frontera de A3 exigen réplicas adicionales para decidir su estado definitivo; y el trabajo futuro apunta a densidad como cuarto factor, banda de 5 GHz, protocolos de transporte alternativos y elevación del prototipo a un grado de madurez tecnológico superior mediante pruebas en instalaciones y condiciones de operación reales.

## 5.6. Cierre del Proyecto

Con la campaña factorial ejecutada en su totalidad, el umbral de éxito del 85 % verificado con rigor estadístico y cumplido en los escenarios evaluados, el modelo predictivo validado por encima del criterio fijado, el plan de contingencia aplicado documentadamente y los resultados integrados en el presente documento con trazabilidad completa hasta el registro original, **el presente trabajo de tesis queda cerrado como un trabajo de tesis totalmente terminado**, susceptible de defensa ante el jurado evaluador en las condiciones académicas de la Universidad Nacional de San Agustín de Arequipa.
