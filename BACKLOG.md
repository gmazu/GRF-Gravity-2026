# BACKLOG

## Pendientes

### Alta prioridad
- [x] **Aumentar brillo del efecto** - RESUELTO: ajustar opacidad en YAML
- [x] **Restaurar visibilidad de la red** - RESUELTO: cambiar color_fondo a #7986cb

### Media prioridad
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
