
# ============================================================
# PANELMSE - csv_loader.py
# FUNCIÓN DEL ARCHIVO:
# Leer los archivos CSV de paneles y posiciones.
# ============================================================


# ============================================================
# BLOQUE 1: IMPORTACIONES
# FUNCIÓN:
# Importar las herramientas necesarias para trabajar
# con archivos CSV y rutas del computador.
# ============================================================

import csv
from pathlib import Path

# ============================================================
# BLOQUE 2: FUNCIÓN GENERAL PARA LEER CSV
# FUNCIÓN:
# Abrir un archivo CSV, leer sus encabezados y recuperar
# sus registros como diccionarios.
#
# CONFIGURACIÓN:
# - Separador: punto y coma (;).
# - Codificación: UTF-8 con o sin BOM.
# ============================================================

def leer_csv(ruta: str | Path) -> list[dict[str, str | None]]:

    # Convertir la ruta recibida en un objeto Path.
    ruta_archivo = Path(ruta)

    # Comprobar que el archivo exista.
    if not ruta_archivo.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {ruta_archivo}"
        )

    # Comprobar que la ruta corresponda a un archivo.
    if not ruta_archivo.is_file():
        raise ValueError(
            f"La ruta indicada no corresponde a un archivo: {ruta_archivo}"
        )

    # Abrir el archivo para su lectura.
    with ruta_archivo.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as archivo:

        # Leer el CSV utilizando punto y coma como separador.
        lector = csv.DictReader(archivo, delimiter=";")

        # Comprobar que existan encabezados.
        if lector.fieldnames is None or not lector.fieldnames:
            raise ValueError(
                f"El archivo {ruta_archivo.name} no contiene encabezados."
            )

        # Comprobar que no existan encabezados vacíos.
        if any(not encabezado.strip() for encabezado in lector.fieldnames):
            raise ValueError(
                f"El archivo {ruta_archivo.name} contiene encabezados vacíos."
            )

        # Comprobar que no existan encabezados repetidos.
        if len(lector.fieldnames) != len(set(lector.fieldnames)):
            raise ValueError(
                f"El archivo {ruta_archivo.name} contiene encabezados repetidos."
            )

        # Crear una lista para almacenar los registros.
        filas = []

        # Recorrer los registros del archivo.
        for numero_fila, fila in enumerate(lector, start=2):

            # Detectar si una fila tiene más campos que encabezados.
            if None in fila:
                raise ValueError(
                    f"El archivo {ruta_archivo.name} tiene campos adicionales "
                    f"en la fila {numero_fila}."
                )

            # Guardar la fila leída.
            filas.append(fila)

    # Comprobar que el archivo tenga registros.
    if not filas:
        raise ValueError(
            f"El archivo {ruta_archivo.name} no contiene registros."
        )

    # Devolver todos los registros leídos.
    return filas


# ============================================================
# BLOQUE 3: CARGAR PANELES
# FUNCIÓN:
# Leer el archivo CSV que contiene los paneles prefabricados.
# ============================================================

def cargar_paneles(ruta: str | Path) -> list[dict[str, str | None]]:

    return leer_csv(ruta)


# ============================================================
# BLOQUE 4: CARGAR POSICIONES
# FUNCIÓN:
# Leer el archivo CSV que contiene las posiciones del muro.
# ============================================================

def cargar_posiciones(ruta: str | Path) -> list[dict[str, str | None]]:

    return leer_csv(ruta)
