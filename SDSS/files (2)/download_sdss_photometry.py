#!/usr/bin/env python3
"""
Script para descargar fotometría ugriz de SDSS para lentes gravitacionales
Proyecto: GRF-RGB / ThöEv-RθB
Objetivo: Buscar cromaticidad en lensing gravitacional (arcoíris gravitacionales)

Uso:
    python download_sdss_photometry.py

El script:
1. Lee las coordenadas de los 700 lentes SDSS
2. Hace queries al servidor SkyServer de SDSS
3. Descarga fotometría ugriz para cada lente
4. Guarda todo en un CSV para análisis
"""

import csv
import time
import urllib.request
import urllib.parse
import json

# Configuración
INPUT_FILE = '/home/claude/sdss_lenses_coords.csv'
OUTPUT_FILE = '/home/claude/sdss_lenses_photometry.csv'
SEARCH_RADIUS = 5  # arcsec - radio de búsqueda alrededor de cada lente

# URL del servidor SDSS SkyServer
SDSS_URL = "https://skyserver.sdss.org/dr17/SkyServerWS/SearchTools/RadialSearch"

def query_sdss_photometry(ra, dec, radius_arcsec=5):
    """
    Consulta al servidor SDSS para obtener fotometría ugriz
    cerca de una coordenada dada.
    """
    params = {
        'ra': ra,
        'dec': dec,
        'radius': radius_arcsec / 60.0,  # convertir a arcmin
        'format': 'json'
    }
    
    url = SDSS_URL + '?' + urllib.parse.urlencode(params)
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"  Error en query: {e}")
        return None

def main():
    print("=" * 60)
    print("DESCARGA DE FOTOMETRÍA SDSS PARA LENTES GRAVITACIONALES")
    print("Proyecto: GRF-RGB / ThöEv-RθB")
    print("=" * 60)
    print()
    
    # Leer coordenadas de lentes
    lenses = []
    with open(INPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lenses.append(row)
    
    print(f"Lentes a procesar: {len(lenses)}")
    print(f"Radio de búsqueda: {SEARCH_RADIUS} arcsec")
    print()
    
    # Preparar archivo de salida
    output_columns = [
        'lens_name', 'lens_ra', 'lens_dec', 'lens_z',
        'sdss_objid', 'sdss_ra', 'sdss_dec', 'sdss_type',
        'u', 'g', 'r', 'i', 'z',
        'u_err', 'g_err', 'r_err', 'i_err', 'z_err',
        'distance_arcsec'
    ]
    
    results = []
    errors = []
    
    print("Iniciando descarga...")
    print("-" * 60)
    
    for i, lens in enumerate(lenses):
        name = lens['name']
        ra = float(lens['RA'])
        dec = float(lens['DEC'])
        zlens = lens['zlens']
        
        print(f"[{i+1}/{len(lenses)}] {name} (RA={ra:.4f}, DEC={dec:.4f})")
        
        # Query SDSS
        data = query_sdss_photometry(ra, dec, SEARCH_RADIUS)
        
        if data and len(data) > 0:
            # Puede haber múltiples objetos cerca - guardar todos
            for obj in data:
                try:
                    result = {
                        'lens_name': name,
                        'lens_ra': ra,
                        'lens_dec': dec,
                        'lens_z': zlens,
                        'sdss_objid': obj.get('objid', ''),
                        'sdss_ra': obj.get('ra', ''),
                        'sdss_dec': obj.get('dec', ''),
                        'sdss_type': obj.get('type', ''),
                        'u': obj.get('u', ''),
                        'g': obj.get('g', ''),
                        'r': obj.get('r', ''),
                        'i': obj.get('i', ''),
                        'z': obj.get('z', ''),
                        'u_err': obj.get('err_u', ''),
                        'g_err': obj.get('err_g', ''),
                        'r_err': obj.get('err_r', ''),
                        'i_err': obj.get('err_i', ''),
                        'z_err': obj.get('err_z', ''),
                        'distance_arcsec': obj.get('distance', '') 
                    }
                    results.append(result)
                except Exception as e:
                    print(f"  Error procesando objeto: {e}")
            
            print(f"  -> {len(data)} objetos encontrados")
        else:
            print(f"  -> Sin datos")
            errors.append(name)
        
        # Pausa para no sobrecargar el servidor
        time.sleep(0.5)
        
        # Guardar progreso cada 50 lentes
        if (i + 1) % 50 == 0:
            print()
            print(f"Progreso: {i+1}/{len(lenses)} ({100*(i+1)/len(lenses):.1f}%)")
            print(f"Objetos encontrados: {len(results)}")
            print()
    
    print("-" * 60)
    print()
    
    # Guardar resultados
    print(f"Guardando resultados en {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(results)
    
    print()
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Lentes procesados: {len(lenses)}")
    print(f"Objetos SDSS encontrados: {len(results)}")
    print(f"Lentes sin datos: {len(errors)}")
    print(f"Archivo de salida: {OUTPUT_FILE}")
    print()
    
    if errors:
        print(f"Lentes sin datos SDSS ({len(errors)}):")
        for e in errors[:10]:
            print(f"  - {e}")
        if len(errors) > 10:
            print(f"  ... y {len(errors)-10} más")
    
    print()
    print("Listo para análisis de cromaticidad!")
    print("Siguiente paso: comparar magnitudes u vs z para cada lente")

if __name__ == '__main__':
    main()
