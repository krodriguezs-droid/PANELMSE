
# ============================================================
# PANELMSE - main.py
# FUNCIÓN DEL ARCHIVO:
# Coordinar el funcionamiento de todos los módulos.
#
# FLUJO:
# 1. Leer los archivos CSV.
# 2. Validar los registros.
# 3. Ejecutar las asignaciones.
# 4. Preparar los resultados.
#
# Si existen errores de lectura o validación, se bloquea
# el cálculo y se devuelven los mensajes correspondientes.
# ============================================================


# ============================================================
# BLOQUE 1: IMPORTACIONES
# FUNCIÓN:
# Importar las funciones de los módulos que conforman
# el funcionamiento principal de PANELMSE.
# ============================================================

import csv
from pathlib import Path

from .assignment import asignar_paneles
from .csv_loader import cargar_paneles, cargar_posiciones
from .results import preparar_resultados
from .validators import validar_paneles, validar_posiciones

# ============================================================
# BLOQUE 2: FUNCIÓN PRINCIPAL
# FUNCIÓN:
# Recibir las rutas de los dos CSV y coordinar
# el procesamiento de la información.
#
# ENTRADAS:
# ruta_paneles: ubicación del CSV de paneles.
# ruta_posiciones: ubicación del CSV de posiciones.
#
# RESULTADO:
# Un diccionario con el estado del procesamiento,
# los posibles errores y los resultados obtenidos.
# ============================================================

def procesar_archivos(
    ruta_paneles: str | Path,
    ruta_posiciones: str | Path
) -> dict:

    # ========================================================
    # BLOQUE 2.1: LECTURA DE LOS ARCHIVOS
    # FUNCIÓN:
    # Leer los CSV utilizando las funciones de csv_loader.py.
    # Registrar los errores de lectura sin ejecutar cálculos.
    # ========================================================

    errores_lectura = []

    filas_paneles = None
    filas_posiciones = None

    # Intentar leer el archivo de paneles.
    try:

        filas_paneles = cargar_paneles(ruta_paneles)

    except (OSError, ValueError, csv.Error) as error:

        errores_lectura.append(
            f"No se pudo leer el archivo de paneles: {error}"
        )

    # Intentar leer el archivo de posiciones.
    try:

        filas_posiciones = cargar_posiciones(ruta_posiciones)

    except (OSError, ValueError, csv.Error) as error:

        errores_lectura.append(
            f"No se pudo leer el archivo de posiciones: {error}"
        )

    # Si existe algún error de lectura, detener el proceso.
    if errores_lectura:

        return {
            "correcto": False,
            "errores": errores_lectura,
            "resultados": None
        }


    # ========================================================
    # BLOQUE 2.2: VALIDACIÓN DE LOS DATOS
    # FUNCIÓN:
    # Comprobar los registros de ambos archivos mediante
    # las funciones de validators.py.
    #
    # Si existe cualquier error, no se ejecuta la asignación.
    # ========================================================

    paneles, errores_paneles = validar_paneles(
        filas_paneles,
        Path(ruta_paneles).name
    )

    posiciones, errores_posiciones = validar_posiciones(
        filas_posiciones,
        Path(ruta_posiciones).name
    )

    # Reunir los errores de ambos archivos.
    errores_validacion = (
        errores_paneles + errores_posiciones
    )

    # Bloquear el cálculo si hay datos inválidos.
    if errores_validacion:

        return {
            "correcto": False,
            "errores": errores_validacion,
            "resultados": None
        }


    # ========================================================
    # BLOQUE 2.3: ASIGNACIÓN DE PANELES
    # FUNCIÓN:
    # Ejecutar el algoritmo de emparejamiento máximo
    # definido en assignment.py.
    #
    # El objetivo es cubrir la mayor cantidad posible
    # de posiciones respetando las restricciones.
    # ========================================================

    asignaciones = asignar_paneles(
        paneles,
        posiciones
    )


    # ========================================================
    # BLOQUE 2.4: PREPARACIÓN DE RESULTADOS
    # FUNCIÓN:
    # Organizar las asignaciones, calcular las cotas
    # superiores e identificar pendientes y sobrantes.
    # ========================================================

    resultados = preparar_resultados(
        paneles,
        posiciones,
        asignaciones
    )


    # ========================================================
    # BLOQUE 2.5: DEVOLVER RESULTADOS
    # FUNCIÓN:
    # Entregar el resultado completo a quien haya llamado
    # esta función, por ejemplo, la futura interfaz gráfica.
    #
    # "correcto" indica que la lectura, validación y cálculo
    # se completaron sin errores, aunque existan posiciones
    # pendientes.
    # ========================================================

    return {
        "correcto": True,
        "errores": [],
        "resultados": resultados
    }
