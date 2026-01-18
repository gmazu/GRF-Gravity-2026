# SDSS photometry downloader

This script queries SDSS SkyServer (DR17) to fetch ugriz photometry around
gravitational lens coordinates and saves the results to a CSV file.

## Files
- `download_sdss_photometry.py`: main script.
- `sdss_lenses_coords.csv`: input catalog with columns:
  `name`, `RA`, `DEC`, `zlens`.

## Requirements
- Python 3.8+
- Internet access (SkyServer API)

No third-party packages are required (standard library only).

## Usage
1. Edit the input/output paths near the top of the script:
   - `INPUT_FILE`
   - `OUTPUT_FILE`
2. Run:
   `python download_sdss_photometry.py`

The script will:
- read the lens list,
- query SDSS for objects within `SEARCH_RADIUS` (arcsec),
- collect ugriz magnitudes and errors,
- write a single CSV with one row per SDSS object found.

## Output columns
The output CSV includes:
`lens_name`, `lens_ra`, `lens_dec`, `lens_z`,
`sdss_objid`, `sdss_ra`, `sdss_dec`, `sdss_type`,
`u`, `g`, `r`, `i`, `z`,
`u_err`, `g_err`, `r_err`, `i_err`, `z_err`,
`distance_arcsec`

## Notes
- A 0.5 s delay is used between queries to avoid overloading the server.
- If an input row has non-numeric `zlens` values (e.g. "measured"), it is
  passed through as-is in the output.
