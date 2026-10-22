# ANEXOS

Los anexos que siguen recogen los tres instrumentos que el capítulo III remite a este nivel: el croquis del escenario experimental con sus criterios fotográficos (apartado 3.1.2), la lista de materiales y su presupuesto (apartado 3.1.3) y el formato del cuaderno de campo (apartado 3.4). Su propósito es permitir la reconstrucción íntegra del experimento por un tercero sin acceso al escenario físico.

## Anexo A. Croquis del escenario experimental y criterios fotográficos

Croquis de planta de referencia. Las distancias consignadas son de referencia; la distancia vigente de cada ensayo se mide con cinta métrica, se asienta en el cuaderno de campo y se carga en `geometría.csv` con la identificación `AᵢBⱼCₖ`.

```
   ┌──────────────────────────────────────────────────────────┐
   │  HABITACIÓN 1 (recinto emisor)     │  HABITACIÓN 2        │
   │                                    │                      │
   │   [AP]@            ◄── 3 m ──►    │        [S]●           │  A1: N1 y S en
   │                          [N1]●     │   (misma/hab. contigua│  el mismo recinto
   │                                    │    con puerta abierta)│  o puerta abierta
   ├────────────────────────────────────┼──────────────────────┤
   │            MURO DE CONCRETO 1      │                      │
   ├────────────────────────────────────┼──────────────────────┤
   │  HABITACIÓN 3                      │  HABITACIÓN 4        │
   │                                    │                      │
   │   [N2]●             ◄── 3 m ──►    │        [S]●          │  A2: exactamente
   │                                    │      (1 muro)        │  UN muro interpuesto
   ├────────────────────────────────────┤                      │
   │            MURO DE CONCRETO 2      │                      │
   ├────────────────────────────────────┴──────────────────────┤
   │  ÁREA 5 (extremo opuesto / semiabierta)                   │
   │            [N3]●        ◄── ≈8 m ──►       [S]●          │  A3: DOS muros
   │                                                            │  (o ruido ISM alto)
   └────────────────────────────────────────────────────────────┘

   [N1|N2|N3]● = nodo emisor    [S]● = suscriptor    @ = punto de acceso (AP)
   El AP, la PC de adquisición y el router NO se desplazan durante toda la campaña.
```

**Tabla A.1. Levantamiento geométrico (llenar en campo antes de la campaña):**

| Punto de emplazamiento | Codificación fija | Distancia desde referencia (m) | Observación |
|---|---|---|---|
| Punto de acceso Wi-Fi | AP | ______ | No se desplaza; altura ______ m |
| Nodo emisor 1 | N1 | ______ | Habitación 1 |
| Nodo emisor 2 | N2 | ______ | Habitación 3 |
| Nodo emisor 3 | N3 | ______ | Área 5 |
| Suscriptor, nivel A1 | S-A1 | ______ | Misma habitación o puerta abierta; muros = 0 |
| Suscriptor, nivel A2 | S-A2 | ______ | Un muro interpuesto; distancia comparable a A1 |
| Suscriptor, nivel A3 | S-A3 | ______ | Dos muros o zona de ruido ISM elevado |
| PC de adquisición (broker) | PC | ______ | Enlace cableado al router; no se desplaza |

**Tabla A.2. Registro fotográfico por nivel de propagación:**

| Leyenda | Contenido de la fotografía | Uso en el documento |
|---|---|---|
| A-1 | Emisor y suscriptor en el nivel A1, con el recinto y la puerta en el estado ensayado | Evidencia de visibilidad directa |
| A-2 | Emisor y suscriptor en el nivel A2, con el muro interpuesto visible en el encuadre | Evidencia de un solo muro |
| A-3 | Emisor y suscriptor en el nivel A3, con los dos muros o la fuente de ruido circundante | Evidencia de doble muro o interferencia |
| R-1 | Panel del router: canal, SSID, ancho de banda y potencia | Evidencia de canal fijo (apartado 3.1.5) |
| N-1 | Banner de consola de los cuatro nodos: IP, canal, RSSI y marca NTP | Evidencia de sincronización ≤ ±10 ms |

Las fotografías se archivan con la leyenda de la primera columna, se insertan en la versión impresa del documento y conservan la fecha y hora de captura en los metadatos.

## Anexo B. Lista de materiales y presupuesto de referencia

**Tabla B.1. Lista de materiales del prototipo (4 nodos):**

| # | Componente | Cant. | Especificación / nota | Costo unit. (S/) | Total (S/) |
|---|---|---|---|---|---|
| 1 | Placa ESP32 NodeMCU DevKit V1 | 4 | Chip ESP-WROOM-32, USB mini-B, regulador 3,3 V integrado; 3 nodos emisores (N1–N3) + 1 suscriptor (S) | ______ | ______ |
| 2 | Sensor DHT22 (AM2302) | 4 | Temperatura y humedad como covariable ambiental de control | ______ | ______ |
| 3 | Resistencia 10 kΩ | 4 | *Pull-up* del data del DHT22 | ______ | ______ |
| 4 | Cable USB mini-B | 4 | Alimentación y programación, ≥ 1 A por puerto | ______ | ______ |
| 5 | Hub USB o fuente(s) 5 V dedicada(s) | 2–4 | Evitar hubs de baja capacidad; pico del ESP32 ≈ 500 mA | ______ | ______ |
| 6 | Router Wi-Fi doméstico | 1 | 2,4 GHz, IEEE 802.11 b/g/n, canal fijo y ancho de 20 MHz | ______ | ______ |
| 7 | PC estación de adquisición | 1 | Ejecuta broker Mosquitto, NTP local y colector; enlace cableado | ______ | ______ |
| 8 | Cable Ethernet Cat5e/Cat6 | 1 | Enlace PC–router | ______ | ______ |
| 9 | Cinta métrica, cinta adhesiva, croquis impresos | — | Fijación de posiciones sin desplazamientos intra-ensayo | ______ | ______ |
| | | | **TOTAL** | | ______ |

Los costos se asientan al momento de la adquisición real, con fecha y comprobante de pago archivados en el cuaderno de campo; la columna se deja en blanco a propósito para no consignar precios no verificables.

## Anexo C. Formato del cuaderno de campo

### C.1. Condiciones fijas de la campaña (se verifican una vez por sesión de medición)

| Verificación | Criterio | Valor observado | Fecha/hora | Firma |
|---|---|---|---|---|
| Canal Wi-Fi fijo | 1, 6 u 11; ancho 20 MHz; WAN caída | ______ | ______ | ______ |
| Sincronización NTP | Desfase ≤ ±10 ms en N1, N2, N3 y S | ______ | ______ | ______ |
| Broker Mosquitto | Servicio activo, log con milisegundos | ______ | ______ | ______ |
| Ambiente conforme | Puertas, ocupación y aparatos según apartado 3.1.2 | ______ | ______ | ______ |
| Firmware vigente | Versión idéntica en las cuatro placas | ______ | ______ | ______ |

### C.2. Registro individual de ensayo (una fila por cada uno de los 81 ensayos)

| Campo | Valor |
|---|---|
| Orden en `secuencia_81.csv` (1–81) | ______ |
| Identificador de ensayo (`AᵢBⱼCₖ_rℓ`) | ______ |
| Celda / réplica | ______ |
| Nivel de QoS MQTT (C1/C2/C3 = 0/1/2) | ______ |
| Intervalo de oferta B (5000 / 1000 / 250 ms) | ______ |
| Nivel de escenario y variante empleada (A1/A2/A3; si A3, doble muro o ruido ISM) | ______ |
| Distancia medida emisor–suscriptor (m) | ______ |
| Hora de inicio (NTP, ms) | ______ |
| Hora de fin (NTP, ms) | ______ |
| Duración efectiva (s; exigida 600) | ______ |
| Desfase NTP verificado al inicio y al fin (ms) | ______ |
| Condición ambiental (puertas, ocupación, electrodomésticos) | ______ |
| Versión del firmware en los nodos | ______ |
| Versión de Mosquitto y configuración vigente del router (canal, potencia, SSID, seguridad) | ______ |
| Mensajes esperados / observados (%) | ______ / ______ |
| Incidencias operativas (con hora) | ______ |
| Decisión: completa / anulada (motivo y fecha de reejecución) | ______ |

### C.3. Registros triangulados conservados por ensayo

| Registro | Contenido mínimo | Soporte |
|---|---|---|
| Nodo emisor | Marca de tiempo de emisión, RSSI, SNR, nivel de ruido y contador de secuencia | `mensajes.db` / `mensajes.csv` |
| Nodo suscriptor | Marca de tiempo de recepción, contador de secuencia y verificación de unicidad | `tesis/suscriptor/registros` y copia serie |
| Broker Mosquitto | Sesión, suscripción, mensaje recibido y confirmación de entrega según el QoS ensayado | `log_type information` de Mosquitto |

La etiqueta única de cada mensaje es `AᵢBⱼCₖ_rℓ` + identificador de secuencia. Los ensayos anulados se reejecutan íntegros en su totalidad; ningún registro se edita ni se elimina retroactivamente.
