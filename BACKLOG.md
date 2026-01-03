# BACKLOG

## Pendientes

### Alta prioridad
- [x] **Aumentar brillo del efecto** - RESUELTO: ajustar opacidad en YAML
- [x] **Restaurar visibilidad de la red** - RESUELTO: cambiar color_fondo a #7986cb
- [ ] **Bow Riding / Wave Riding** - Gravedad como efecto de perturbación del eCEL
  - Similar a delfines surfeando la estela de un barco (sin esfuerzo)
  - Masa mayor crea "surco/ola" en el océano eCEL
  - Masas menores orbitan en ese surco (no atraídas, sino surfeando)
  - Jerarquía de túneles:
    - Galaxia → crea túneles de ondas para soles
    - Sol → crea órbitas para planetas
    - Planeta → crea túnel para lunas
  - **VENTAJA CLAVE**: Problema de 3 cuerpos se vuelve SIMPLE
    - Newton/Einstein: casi imposible de resolver analíticamente
    - eCEL: suma de perturbaciones/surcos = solución directa
  - Referencia visual: `media/images/Screenshot from 2026-01-03 16-07-22.png`
- [ ] **Dos planetas acercándose** - Agregar segundo planeta y acercarlos para ver interacción de halos eCEL
  - ¿Qué pasa cuando los halos se superponen?
  - ¿Se empujan? ¿Se atraen por gradiente de presión?
  - Visualizar el mecanismo de "gravedad" como empuje diferencial
- [ ] **Rayo de luz que se dobla** - Lanzar fotón y que se curve por gradiente de densidad eCEL
  - Luz viaja más lento en zonas de mayor densidad eCEL
  - Se dobla hacia la masa (lensing gravitacional)
  - Validación: deflexión 1.75 arcsec cerca del Sol (Eddington 1919)
- [ ] **Movimiento bien hecho** - Rehacer v2.2.x desde cero
  - Masa se mueve, océano eCEL queda estático
  - Halo se recalcula según posición de la masa
  - Efecto piscina: eCEL se abre adelante, se acomoda atrás
  - v2.2.0 y v2.2.1 fallaron (el usuario se puso huevón)

### Media prioridad
- [x] **Distribución homogénea eCEL** - RESUELTO v2.1.1: sin aleatorio, distancia mínima, sin espacios vacíos
- [ ] **YAMLs preconfigurados** - Crear configs listos para usar:
  - `config_planeta.yaml` (Tierra, Marte, etc.)
  - `config_sol.yaml` (estrellas)
  - `config_agujero_negro.yaml` (singularidad)
  - Evitar cambiar valores manualmente para cada objeto
- [ ] Agregar escena TresCuerpos (problema 3 cuerpos)
- [ ] Agregar escena AgujeroNegro (formación horizonte eventos)
- [ ] Agregar escena ComparacionEdades (predicción falsable)

### Baja prioridad
- [ ] Optimizar render para GPU (OpenGL renderer)
- [ ] Agregar parámetro de "caída súbita" vs "aparición suave"

---

## Versiones

### v2.1.4 (2026-01-03) - BASE PARA PELÍCULA
- Difuminación suave del halo (opacidad → 0 en capas externas)
- **VERSIÓN ESTABLE** para película multi-escena
- Fases en orden: 1) océano eCEL → 2) planeta → 3) halo
- Después se juntarán todas las escenas en una película completa

### v2.1.3 (2026-01-02)
- Copia de v2.1.2 con FadeOut del fondo después de generar halo
- Solo queda visible: masa + halo eCEL organizado
- Fondo desaparece para mostrar claramente el efecto

### v2.1.2 (2026-01-02)
- Efecto CASCADA: eCEL desplazado desplaza más eCEL
- UN SOLO halo extendido (20 capas vs 12 en v2.1.1)
- Gradiente suave con factor_cascada = 1.0 + 0.3 * exp(-capa/5)
- Color gradiente: BLUE_B → PURPLE_A

### v2.1.1 (2026-01-02)
- Distribución HOMOGÉNEA (sin aleatorio)
- Distancia mínima entre partículas
- Sin espacios vacíos - estado de mínima entropía

### v2.1.0 (2026-01-02)
- Nueva lógica de desplazamiento basada en densidad REAL
- eCEL "brota" en periferia (no mueve existentes)
- Cantidad desplazada ∝ masa² (cuadrático)
- Tabla de desplazamiento: Agua 10%, Tierra 50%, Plomo 70%, Oro 85%
- Gradiente 1/r² desde superficie
- Nueva escena: ComparacionDensidades
- **Bug**: Red de fondo poco visible, brillo atenuado

### v2.0.1 (2026-01-02)
- Intento de desplazamiento por densidad
- Problema: solo iluminaba, no mostraba acumulación correcta

### v2.0.0 (2026-01-02)
- Océano eCEL uniforme (malla simétrica tipo red de tenis)
- Efecto de desplazamiento básico (Arquímedes)
- Primera masa (Tierra) desplazando eCEL

### v1.0.3 (2026-01-02)
- Malla completa + config YAML externo
- Parámetros configurables sin tocar código

### v1.0.2
- Campo fijo con iluminación dinámica

### v1.0.1
- Partículas más pequeñas

### v1.0.0
- Primera versión con campo denso 1/r²

---

## Notas de desarrollo

- Espaciado 0.25 para pruebas rápidas, 0.12 para render final
- Hardware: Intel Iris Xe (GPU integrada) - usar CPU renderer
- Regla: siempre crear nueva versión, no sobrescribir
