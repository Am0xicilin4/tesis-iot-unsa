import os

# Cambiar la ruta absoluta del contenedor por la ruta local actual
ruta = "./"

with open(ruta + "introduccion.md", "a", encoding="utf-8") as f:
    f.write("\n\n[INSERTAR AQUÍ FLUJOGRAMA DE: Arquitectura general del sistema IoT híbrido...]")
# (y así sucesivamente con los demás archivos)