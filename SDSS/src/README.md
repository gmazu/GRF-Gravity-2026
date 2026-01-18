# Descargador de fotometria SDSS

Este script consulta SDSS SkyServer (DR17) para obtener fotometria ugriz
alrededor de coordenadas de lentes gravitacionales y guarda los resultados
en un CSV.

## Archivos
- `download_sdss_photometry.py`: script principal.
- `sdss_lenses_coords.csv`: catalogo de entrada con columnas:
  `name`, `RA`, `DEC`, `zlens`.

## Requisitos
- Python 3.8+
- Acceso a internet (API de SkyServer)

No requiere paquetes externos (solo librerias standard).

## Ejecucion
1. Edita las rutas de entrada/salida al inicio del script:
   - `INPUT_FILE`
   - `OUTPUT_FILE`
2. Ejecuta:
   `python download_sdss_photometry.py`

Opcionalmente, limita la cantidad de lentes con:
`python download_sdss_photometry.py --limit 10`

O procesa solo una fila (posicion 1-based):
`python download_sdss_photometry.py --row 5`

El script:
- lee la lista de lentes,
- consulta SDSS para objetos dentro de `SEARCH_RADIUS` (arcsec),
- guarda magnitudes ugriz y errores,
- escribe un CSV con una fila por objeto SDSS encontrado.

## Columnas de salida
El CSV de salida incluye:
`lens_name`, `lens_ra`, `lens_dec`, `lens_z`,
`sdss_objid`, `sdss_ra`, `sdss_dec`, `sdss_type`,
`u`, `g`, `r`, `i`, `z`,
`u_err`, `g_err`, `r_err`, `i_err`, `z_err`,
`distance_arcsec`

## Notas
- Se espera 0.5 s entre queries para no sobrecargar el servidor.
- Si una fila tiene `zlens` no numerico (ej. "measured"), se guarda tal cual.
