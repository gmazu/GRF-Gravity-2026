# CONTEXT

Reglas para desarrollo con asistente IA (Claude).

## Reglas generales

- **Pedir VB (visto bueno) antes de hacer cambios** en archivos existentes
- No asumir que un cambio es deseado, siempre confirmar primero
- Proponer el cambio, esperar aprobacion, luego ejecutar

## Versionamiento

- **Siempre crear nueva version** al hacer cambios (v2.0.1, v2.0.2, etc.)
- **NO sobrescribir** la version actual a menos que se indique explicitamente
- **Mejor tener mas versiones que menos** - facilita volver atras si algo falla
- Formato: `NombreProyecto-vX.Y.Z.py`
  - X = version mayor (cambios grandes de arquitectura)
  - Y = version menor (nuevas funcionalidades)
  - Z = parche (correcciones, ajustes pequenos)

## Comportamiento esperado (eCEL)

- El campo eCEL se comporta como un liquido (efecto Arquimedes)
- Las masas desplazan el eCEL de su volumen
- El eCEL desplazado se acumula en la periferia
- La densidad decae con 1/r² (inverso del cuadrado de la distancia)
- Parametros configurables via `config_ecel.yaml` sin tocar codigo

## Estructura de archivos

- `CONTEXT.md` - Este archivo (reglas para IA)
- `README.md` - Documentacion del proyecto
- `config_*.yaml` - Configuracion sin tocar codigo
- `*-vX.Y.Z.py` - Scripts versionados
