# GRF-Gravity-2026

Visualizaciones Manim del modelo de gravedad eCEL (Push Gravity via Pressure Gradients).

## Concepto

El modelo eCEL propone que la gravedad no es una fuerza de atraccion sino el resultado de gradientes de presion en un "oceano" de campo eCEL:

- Mayor densidad de eCEL cerca de la materia
- La densidad disminuye con 1/r² (inverso del cuadrado de la distancia)
- Los cuerpos son empujados hacia zonas de menor densidad (entre masas)

## Archivos

| Archivo | Descripcion |
|---------|-------------|
| `manim.py` | Version original (estilo Einstein - curvatura) |
| `GravityeCEL-v1.0.0.py` | Primera version con campo denso 1/r² |
| `GravityeCEL-v1.0.1.py` | Particulas mas pequenas |
| `GravityeCEL-v1.0.2.py` | Campo fijo con iluminacion dinamica |
| `GravityeCEL-v1.0.3.py` | Malla completa + config YAML externo |
| `config_ecel.yaml` | Configuracion de intensidad, malla y animacion |

## Uso

```bash
# Renderizar animacion (calidad baja, preview)
manim -pql GravityeCEL-v1.0.3.py OceanGravity

# Renderizar alta calidad
manim -pqh GravityeCEL-v1.0.3.py OceanGravity
```

## Configuracion

Editar `config_ecel.yaml` para ajustar sin tocar el codigo:

```yaml
intensidad:
  multiplicador: 0.75      # Factor de brillo
  opacidad_minima: 0.08    # Opacidad del fondo
  opacidad_maxima: 0.95    # Opacidad maxima cerca del nucleo

malla:
  espaciado: 0.12          # Distancia entre particulas
  radio_particula: 0.012   # Tamano de cada particula

animacion:
  duracion_movimiento: 4   # Segundos de animacion
  desplazamiento: 1.5      # Distancia que se mueven los nucleos
```

## Requisitos

- Python 3.8+
- Manim
- PyYAML

```bash
pip install manim pyyaml
```
