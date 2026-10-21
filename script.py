import os

ruta = "/root/tesis/"

with open(ruta + "introduccion.md", "a", encoding="utf-8") as f:
    f.write("\n\n[INSERTAR AQUÍ FLUJOGRAMA DE: Arquitectura general del sistema IoT híbrido, mostrando la relación entre los nodos ESP32, el canal Wi-Fi, el broker MQTT y la capa de análisis]\n")
    f.write("[INSERTAR AQUÍ TABLA: Matriz de consistencia de la investigación, relacionando problema, objetivos, hipótesis y variables]\n")

with open(ruta + "marco_teorico.md", "a", encoding="utf-8") as f:
    f.write("\n\n[INSERTAR AQUÍ FLUJOGRAMA DE: Modelo de pila de protocolos y la interacción cross-layer entre Wi-Fi IEEE 802.11 y MQTT]\n")
    f.write("[INSERTAR AQUÍ TABLA: Cuadro comparativo de modelos de propagación en interiores (ITU-R P.1238 vs Motley-Keenan)]\n")

with open(ruta + "metodologia.md", "a", encoding="utf-8") as f:
    f.write("\n\n[INSERTAR AQUÍ FLUJOGRAMA DE: Diagrama de bloques del diseño experimental factorial 3x3x3 y el flujo del plan de contingencia de 5 pasos]\n")
    f.write("[INSERTAR AQUÍ TABLA: Especificación técnica y costos de los componentes del prototipo físico ESP32]\n")

with open(ruta + "analisis_proyectado.md", "a", encoding="utf-8") as f:
    f.write("\n\n[INSERTAR AQUÍ FLUJOGRAMA DE: Pipeline de Machine Learning con Scikit-learn, desde la limpieza de datos hasta la validación cruzada y evaluación de métricas]\n")
    f.write("[INSERTAR AQUÍ TABLA: Modelo estrella y esquema de relaciones para los tableros de control en Power BI]\n")

print("¡Marcadores estructurados inyectados exitosamente en todos los capítulos!")
