import requests
from pathlib import Path
import time

# Crear carpeta para PDFs
output_dir = Path("GRF_Abstracts_1960-2025")
output_dir.mkdir(exist_ok=True)

# URL base
base_url = "https://www.gravityresearchfoundation.org"

# Lista de años (1960-2025)
years = range(1960, 2026)

# Patrones de nombres de archivo
patterns = [
    "/s/{year}-GRF-Abstracts.pdf",      # 2021-2025
    "/s/{year}-abstracts.pdf",          # 2020
    "/s/{year}abstracts.pdf"            # 1960-2019
]

# Contador
downloaded = 0
failed = []

print(f"🚀 Descargando abstracts GRF 1960-2025...\n")

for year in years:
    success = False
    
    # Probar cada patrón
    for pattern in patterns:
        pdf_path = pattern.format(year=year)
        pdf_url = base_url + pdf_path
        filename = f"{year}_GRF_Abstracts.pdf"
        filepath = output_dir / filename
        
        try:
            print(f"📥 Intentando {year}... ", end="")
            response = requests.get(pdf_url, timeout=10)
            
            if response.status_code == 200 and response.headers.get('Content-Type') == 'application/pdf':
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                file_size = filepath.stat().st_size / 1024  # KB
                print(f"✅ Descargado ({file_size:.1f} KB)")
                downloaded += 1
                success = True
                time.sleep(0.5)  # Pausa cortés
                break
                
        except Exception as e:
            continue
    
    if not success:
        print(f"❌ No encontrado")
        failed.append(year)

# Resumen
print(f"\n{'='*50}")
print(f"✅ Descargados: {downloaded} PDFs")
print(f"❌ Fallidos: {len(failed)}")
if failed:
    print(f"   Años faltantes: {failed}")
print(f"📁 Guardados en: {output_dir.absolute()}")
print(f"{'='*50}")
