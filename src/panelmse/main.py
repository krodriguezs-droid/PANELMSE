
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
from .sequential_assignment import asignar_paneles_secuencialmente
from .validators import validar_paneles, validar_posiciones
from .wall_geometry import (
    comparar_posiciones_geometricas,
    generar_posiciones_geometricas,
)

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

# ============================================================
# NUEVO BLOQUE: PROCESAMIENTO CON GEOMETRIA DEL MURO
#
# OBJETIVO:
# Integrar:
# 1. Lectura y validacion de los CSV.
# 2. Generacion geometrica de posiciones.
# 3. Comparacion geometria - CSV.
# 4. Evaluacion mediante asignacion secuencial.
# 5. Preparacion de resultados.
#
# Esta funcion conserva el flujo anterior y permite
# incorporar los nuevos parametros geometricos.
# ============================================================

def procesar_archivos_con_geometria(
    ruta_paneles,
    ruta_posiciones,
    longitud_muro_m,
    longitud_panel_m,
    altura_inicial_m,
    altura_final_m,
    paso_altura_m=0.05,
    modo_flexible=False
):

    # --------------------------------------------------------
    # BLOQUE 1: LEER LOS ARCHIVOS
    # --------------------------------------------------------

    errores_lectura = []

    try:
        filas_paneles = cargar_paneles(ruta_paneles)

    except (OSError, ValueError, csv.Error) as error:

        errores_lectura.append(
            f"No se pudo leer el archivo de paneles: {error}"
        )

    try:
        filas_posiciones = cargar_posiciones(ruta_posiciones)

    except (OSError, ValueError, csv.Error) as error:

        errores_lectura.append(
            f"No se pudo leer el archivo de posiciones: {error}"
        )

    if errores_lectura:

        return {
            "correcto": False,
            "errores": errores_lectura,
            "resultados": None
        }

    # --------------------------------------------------------
    # BLOQUE 2: VALIDAR LOS CSV
    # --------------------------------------------------------

    paneles, errores_paneles = validar_paneles(
        filas_paneles,
        Path(ruta_paneles).name
    )

    posiciones, errores_posiciones = validar_posiciones(
        filas_posiciones,
        Path(ruta_posiciones).name
    )

    errores_validacion = (
        errores_paneles + errores_posiciones
    )

    if errores_validacion:

        return {
            "correcto": False,
            "errores": errores_validacion,
            "resultados": None
        }

    # --------------------------------------------------------
    # BLOQUE 3: GENERAR LAS POSICIONES GEOMETRICAS
    # --------------------------------------------------------

    try:

        geometria = generar_posiciones_geometricas(
            longitud_muro_m,
            longitud_panel_m
        )

    except (ValueError, TypeError) as error:

        return {
            "correcto": False,
            "errores": [
                f"Error en las dimensiones del muro: {error}"
            ],
            "resultados": None
        }

    # --------------------------------------------------------
    # BLOQUE 4: COMPARAR GEOMETRIA CON EL CSV
    # --------------------------------------------------------

    comparacion = comparar_posiciones_geometricas(
        geometria,
        posiciones
    )

    # No ejecutar asignaciones si las cantidades u órdenes
    # de las posiciones no coinciden.
    if not comparacion["coincide"]:

        errores_comparacion = []

        if comparacion["ordenes_faltantes_csv"]:

            errores_comparacion.append(
                "Faltan en el CSV los órdenes: "
                + ", ".join(
                    map(
                        str,
                        comparacion["ordenes_faltantes_csv"]
                    )
                )
            )

        if comparacion["ordenes_adicionales_csv"]:

            errores_comparacion.append(
                "El CSV contiene órdenes adicionales: "
                + ", ".join(
                    map(
                        str,
                        comparacion["ordenes_adicionales_csv"]
                    )
                )
            )

        if comparacion["ordenes_duplicados_csv"]:

            errores_comparacion.append(
                "El CSV contiene órdenes repetidos: "
                + ", ".join(
                    map(
                        str,
                        comparacion["ordenes_duplicados_csv"]
                    )
                )
            )

        if comparacion["ordenes_invalidos_csv"]:

            errores_comparacion.append(
                "El CSV contiene órdenes inválidos."
            )

        errores_comparacion.append(
            "La geometría genera "
            f"{comparacion['cantidad_posiciones_geometricas']} "
            "posiciones, mientras que el CSV contiene "
            f"{comparacion['cantidad_posiciones_csv']}."
        )

        return {
            "correcto": False,
            "errores": errores_comparacion,
            "resultados": None,
            "comparacion_geometrica": comparacion,
            "geometria": geometria
        }

    # --------------------------------------------------------
    # BLOQUE 5: ASIGNACION SECUENCIAL
    # --------------------------------------------------------

    try:

        asignacion_secuencial = (
            asignar_paneles_secuencialmente(
                paneles,
                posiciones,
                altura_inicial_m,
                altura_final_m,
                paso_altura_m,
                modo_flexible
            )
        )

    except (ValueError, TypeError) as error:

        return {
            "correcto": False,
            "errores": [
                f"No fue posible realizar la asignación: {error}"
            ],
            "resultados": None
        }

    # --------------------------------------------------------
    # BLOQUE 6: PREPARAR LOS RESULTADOS
    # --------------------------------------------------------

    resultados = preparar_resultados(
        paneles,
        posiciones,
        asignacion_secuencial["asignaciones"]
    )

    # Sustituir las listas originales por las ordenadas
    # según la secuencia longitudinal del nuevo algoritmo.

    resultados["asignaciones"] = (
        asignacion_secuencial["asignaciones_detalladas"]
    )

    resultados["posiciones_pendientes"] = (
        asignacion_secuencial["posiciones_pendientes"]
    )

    resultados["paneles_sobrantes"] = (
        asignacion_secuencial["paneles_sobrantes"]
    )

    # --------------------------------------------------------
    # BLOQUE 7: ACTUALIZAR EL RESUMEN DE CANTIDADES
    # --------------------------------------------------------

    resultados["total_posiciones"] = (
        asignacion_secuencial["total_posiciones"]
    )

    resultados["total_asignadas"] = (
        asignacion_secuencial["total_asignadas"]
    )

    resultados["total_pendientes"] = (
        asignacion_secuencial["total_pendientes"]
    )

    resultados["total_paneles_sobrantes"] = (
        asignacion_secuencial["total_paneles_sobrantes"]
    )

    # --------------------------------------------------------
    # BLOQUE 8: INCORPORAR LA INFORMACION GEOMETRICA
    # --------------------------------------------------------

    resultados["geometria_muro"] = geometria

    resultados["comparacion_geometrica"] = comparacion

    resultados["cantidad_paneles_necesarios"] = (
        geometria["cantidad_paneles_necesarios"]
    )

    resultados["longitud_cubierta_m"] = (
        geometria["longitud_cubierta_m"]
    )

    resultados["espacio_sobrante_m"] = (
        geometria["espacio_sobrante_m"]
    )

    # --------------------------------------------------------
    # BLOQUE 9: INCORPORAR EL DIAGNOSTICO DEL INVENTARIO
    # --------------------------------------------------------

    resultados["diagnostico_asignacion"] = (
        asignacion_secuencial
    )

    resultados["direccion_muro"] = (
        asignacion_secuencial["direccion_muro"]
    )

    resultados["modo_altura"] = (
        asignacion_secuencial["modo_altura"]
    )

    resultados["niveles_altura_mm"] = (
        asignacion_secuencial["niveles_altura_mm"]
    )

    resultados["alcanza_altura_final"] = (
        asignacion_secuencial["alcanza_altura_final"]
    )

    resultados["advertencias"] = (
        asignacion_secuencial["advertencias"]
    )

    # --------------------------------------------------------
    # BLOQUE 10: DEVOLVER RESULTADOS
    # --------------------------------------------------------

    return {
        "correcto": True,
        "errores": [],
        "resultados": resultados
    }
