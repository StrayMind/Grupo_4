import subprocess
import logging
import sys
from datetime import datetime
from pathlib import Path

# Configuración del logger principal
logging.basicConfig(level=logging.INFO, format="%(asctime)s [ORQUESTADOR] %(message)s")
logger = logging.getLogger(__name__)

# Definir el orden estricto de ejecución del pipeline
# Ajusta la ruta "scripts/" si tus archivos están en otra carpeta
PIPELINE_SCRIPTS = [
    Path("scripts/limpieza_fraud_pipeline.py"),
    Path("scripts/validate_frautest.py"),
    Path("scripts/load_fraudtest_csv.py"),
    Path("scripts/train_matriculado_model.py")
]

def run_script(script_path: Path):
    """
    Ejecuta un script de Python como un subproceso.
    """
    if not script_path.exists():
        logger.error(f"No se encontró el archivo: {script_path}")
        sys.exit(1)

    logger.info(f"Iniciando la ejecución de: {script_path.name}")
    
    try:
        # Ejecutar el script. 'sys.executable' usa el mismo entorno virtual activo.
        subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            text=True,
            capture_output=False # False permite que los prints del script hijo se vean en la consola
        )
        logger.info(f"Finalizado con éxito: {script_path.name}\n{'-'*60}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error crítico al ejecutar {script_path.name}. Código de salida: {e.returncode}")
        logger.info("Deteniendo el pipeline para evitar inconsistencias en los datos.")
        sys.exit(1)

def main():
    logger.info("=== INICIANDO ORQUESTADOR DEL PIPELINE DE FRAUDE ===")
    start_time = datetime.now()

    # Ejecutar cada script en el orden definido
    for script in PIPELINE_SCRIPTS:
        run_script(script)

    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("=== PIPELINE COMPLETADO EXITOSAMENTE ===")
    logger.info(f"Tiempo total de ejecución: {duration}")

if __name__ == "__main__":
    main()