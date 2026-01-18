# LeSage - Push Gravity Visualization

Visualizaciones Manim de la teoría de gravedad de Georges-Louis Le Sage (1784).

## Concepto

Le Sage propuso que la gravedad es causada por partículas "ultramundanas" que bombardean la materia desde todas direcciones:

- **Partículas ultramundanas**: Llenan el universo, viajan en todas direcciones
- **Atraviesan casi todo**: Masa muy pequeña, muy penetrantes
- **Efecto sombra**: Dos masas se hacen sombra mutuamente
- **Desbalance de presión**: Menos impactos entre las masas → empuje neto (aparente "atracción")

### Diferencia con eCEL

| Le Sage | eCEL |
|---------|------|
| Lluvia de partículas (movimiento) | Océano estático |
| Partículas bombardean masas | Masas desplazan el medio |
| Sombra = menos impactos | Halo = eCEL acumulado |

---

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `LeSage-v1.0.0.py` | Pantalla dividida básica (eCEL vs Le Sage) |
| `LeSage-v1.0.1.py` | Lluvia continua 10 segundos |
| `LeSage-v1.0.2.py` | Lluvia rotativa (360°) + isotrópica |
| `LeSage-v1.2.2.2.py` | **ESTABLE**: Heatmap matplotlib + calentamiento por impactos |
| `LeSage-v1.0.3.py` | Configurable via YAML |
| `config_lesage.yaml` | Configuración de la lluvia |

---

## Configuración (config_lesage.yaml)

```yaml
# Velocidad de las partículas
velocidad:
  minima: 1.5          # Partículas lejanas (lentas)
  maxima: 3.0          # Partículas cercanas (rápidas)

# Cantidad de partículas
cantidad:
  por_oleada_min: 8    # Mínimo por oleada
  por_oleada_max: 15   # Máximo por oleada
  intervalo: 0.4       # Segundos entre oleadas

# Apariencia de las gotas
gotas:
  largo_min: 0.15      # Largo mínimo de la línea
  largo_max: 0.4       # Largo máximo
  grosor_min: 1        # Grosor mínimo
  grosor_max: 3        # Grosor máximo
  opacidad_min: 0.2    # Opacidad mínima (lejanas)
  opacidad_max: 0.6    # Opacidad máxima (cercanas)
  color: "#ffff00"     # Amarillo

# Duración de las fases
duracion:
  rotacion: 10         # Segundos para vuelta completa
  isotropico: 6        # Segundos lluvia isotrópica
```

### Ajustes rápidos

**Lluvia más lenta:**
```yaml
velocidad:
  minima: 1.0
  maxima: 2.0
```

**Más partículas (más densa):**
```yaml
cantidad:
  por_oleada_min: 15
  por_oleada_max: 25
```

**Gotas más largas:**
```yaml
gotas:
  largo_min: 0.3
  largo_max: 0.6
```

---

## Uso

### Renderizar (preview rápido)
```bash
manim -pql LeSage-v1.0.3.py LeSageComparacion
```

### Renderizar (alta calidad)
```bash
manim -pqh LeSage-v1.0.3.py LeSageComparacion
```

---

## Versiones

### v1.2.2.2 (2026-01-04) - ESTABLE
- Heatmap con matplotlib + calentamiento por impactos
- Configuración completa desde `config_lesage.yaml`
- Final cálido tipo “infierno líquido” (sin azules)

### v1.0.3 (2026-01-03)
- Configuración externa via `config_lesage.yaml`
- Velocidad, cantidad, apariencia ajustables sin tocar código
- Lluvia más lenta y suave (tipo lluvia real, no guerra)

### v1.0.2 (2026-01-03)
- Fase 1: Lluvia rotativa (como aguja del reloj, 360°)
- Fase 2: Lluvia isotrópica (todas direcciones a la vez)
- Demostración pedagógica del concepto

### v1.0.1 (2026-01-03)
- Lluvia continua 10 segundos
- Partículas desaparecen antes de cruzar al lado eCEL
- Líneas cortas (disparos) en lugar de puntos

### v1.0.0 (2026-01-03)
- Pantalla dividida: eCEL (izquierda) vs Le Sage (derecha)
- Base copiada de GravityeCEL-v2.1.4.py

---

## Escenas de la animación

### LeSageComparacion (v1.0.3)

1. **Título**: "eCEL vs Le Sage"
2. **Lado izquierdo**: Océano eCEL + Tierra + Halo (estático)
3. **Lado derecho**: Solo Tierra (fondo negro)
4. **Fase 1 - Rotación**: Lluvia rota 360° como aguja del reloj
5. **Fase 2 - Isotrópico**: Lluvia desde todas direcciones

---

## Próximos pasos

- [ ] Agregar efecto sombra cuando hay dos masas
- [ ] Mostrar desbalance de presión con flechas
- [ ] Visualizar el "empuje neto" resultante
- [ ] Comparar predicciones Le Sage vs Newton

---

## Referencias

1. Le Sage, G.-L. (1784). *Lucrèce Newtonien*
2. Edwards, M. R. (2002). *Pushing Gravity: New perspectives on Le Sage's theory*

---

## Contexto

Este proyecto es parte de las visualizaciones para el ensayo:

**"Energy from eCEL Deformation, Not Mass Conversion"**

Gravity Research Foundation Essay Competition 2026
