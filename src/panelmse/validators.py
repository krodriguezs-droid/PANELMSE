
# ============================================================
# PANELMSE - validators.py
# FUNCIÓN DEL ARCHIVO:
# Validar los datos de los CSV, normalizar la información
# y convertir los registros en objetos Panel y Posicion.
# ============================================================


# ============================================================
# BLOQUE 1: IMPORTACIONES
# FUNCIÓN:
# Importar los modelos que representan los paneles
# y las posiciones del muro MSE.
# ============================================================

from .models import Panel, Posicion

# ============================================================
# BLOQUE 2: DEFINICIÓN DE COLUMNAS
# FUNCIÓN:
# Establecer las columnas obligatorias de cada archivo CSV.
# ============================================================

COLUMNAS_PANELES = {
    "id_panel",
    "altura_mm",
    "familia",
    "disponible"

}

COLUMNAS_POSICIONES = {    
    "orden",
    "id_posicion",
    "ubicacion",
    "cota_apoyo_mm",
    "altura_min_mm",
    "altura_max_mm",
    "familia_admitida"
}


# ============================================================
# BLOQUE 3: LIMPIEZA DE TEXTO
# FUNCIÓN:
# Eliminar espacios al principio y al final de un texto.
# Si el valor está vacío o es None, devolver texto vacío.
# ============================================================

def limpiar_texto(valor: str | None) -> str:

    if valor is None:
        return ""

    return str(valor).strip()


# ============================================================
# BLOQUE 4: NORMALIZACIÓN DE IDENTIFICADORES
# FUNCIÓN:
# Eliminar espacios externos y convertir identificadores
# a mayúsculas para evitar diferencias al compararlos.
# ============================================================

def normalizar_identificador(valor: str | None) -> str:

    return limpiar_texto(valor).upper()


# ============================================================
# BLOQUE 5: NORMALIZACIÓN DE FAMILIAS
# FUNCIÓN:
# Eliminar espacios externos y convertir los códigos
# de familia a mayúsculas.
# ============================================================

def normalizar_familia(valor: str | None) -> str:

    return limpiar_texto(valor).upper()


# ============================================================
# BLOQUE 6: VALIDACIÓN DE ENCABEZADOS
# FUNCIÓN:
# Comprobar que un CSV contenga exactamente las columnas
# establecidas para su tipo de archivo.
# ============================================================

def validar_encabezados(
    filas: list[dict[str, str | None]],
    columnas_esperadas: set[str],
    nombre_archivo: str
) -> list[str]:

    errores = []

    # Comprobar que existan registros para verificar.
    if not filas:
        return [
            f"{nombre_archivo}: el archivo no contiene registros."
        ]

    # Obtener los encabezados del primer registro.
    columnas_encontradas = set(filas[0].keys())

    # Detectar columnas faltantes.
    faltantes = columnas_esperadas - columnas_encontradas

    if faltantes:
        errores.append(
            f"{nombre_archivo}: faltan las columnas: "
            f"{', '.join(sorted(faltantes))}."
        )

    # Detectar columnas adicionales.
    adicionales = columnas_encontradas - columnas_esperadas

    if adicionales:
        errores.append(
            f"{nombre_archivo}: existen columnas no permitidas: "
            f"{', '.join(sorted(adicionales))}."
        )

    return errores


# ============================================================
# BLOQUE 7: CONVERSIÓN DE VALORES ENTEROS
# FUNCIÓN:
# Convertir un dato de texto a número entero.
# Informar si está vacío, mal formado o es negativo
# cuando el campo no permite valores negativos.
# ============================================================

def convertir_entero(
    valor: str | None,
    nombre_campo: str,
    nombre_archivo: str,
    numero_fila: int,
    errores: list[str],
    permitir_negativo: bool = False
) -> int | None:

    texto = limpiar_texto(valor)

    # Detectar valores vacíos.
    if not texto:
        errores.append(
            f"{nombre_archivo}, fila {numero_fila}: "
            f"el campo '{nombre_campo}' está vacío."
        )
        return None

    # Intentar convertir el texto en número entero.
    try:
        numero = int(texto)

    except ValueError:
        errores.append(
            f"{nombre_archivo}, fila {numero_fila}: "
            f"el campo '{nombre_campo}' debe ser un número entero."
        )
        return None

    # Detectar valores negativos cuando no están permitidos.
    if not permitir_negativo and numero < 0:
        errores.append(
            f"{nombre_archivo}, fila {numero_fila}: "
            f"el campo '{nombre_campo}' no puede ser negativo."
        )
        return None

    return numero


# ============================================================
# BLOQUE 8: VALIDACIÓN DE PANELES
# FUNCIÓN:
# Revisar los registros del archivo de paneles.
# Normalizar identificadores y familias.
# Convertir cada registro válido en un objeto Panel.
#
# RESULTADO:
# Devuelve una lista de paneles válidos y una lista de errores.
# ============================================================

def validar_paneles(
    filas: list[dict[str, str | None]],
    nombre_archivo: str = "paneles.csv"
) -> tuple[list[Panel], list[str]]:

    paneles = []
    errores_totales = []
    ids_vistos = set()

    # Comprobar los encabezados.
    errores_encabezados = validar_encabezados(
        filas,
        COLUMNAS_PANELES,
        nombre_archivo
    )

    if errores_encabezados:
        return [], errores_encabezados

    # Recorrer los registros. La primera fila de datos es la 2.
    for numero_fila, fila in enumerate(filas, start=2):

        errores_fila = []

        # Normalizar el identificador.
        id_panel = normalizar_identificador(
            fila.get("id_panel")
        )

        # Comprobar que el identificador no esté vacío.
        if not id_panel:
            errores_fila.append(
                f"{nombre_archivo}, fila {numero_fila}: "
                "el identificador del panel está vacío."
            )

        # Detectar identificadores repetidos.
        elif id_panel in ids_vistos:
            errores_fila.append(
                f"{nombre_archivo}, fila {numero_fila}: "
                f"el identificador '{id_panel}' está repetido."
            )

        else:
            ids_vistos.add(id_panel)

        # Convertir la altura a número entero.
        altura = convertir_entero(
            fila.get("altura_mm"),
            "altura_mm",
            nombre_archivo,
            numero_fila,
            errores_fila
        )

        # Normalizar la familia.
        familia = normalizar_familia(
            fila.get("familia")
        )

        if not familia:
            errores_fila.append(
                f"{nombre_archivo}, fila {numero_fila}: "
                "la familia del panel está vacía."
            )

        # Validar disponibilidad.
        disponibilidad = normalizar_identificador(
            fila.get("disponible")
        )

        if disponibilidad not in {"SI", "NO"}:
            errores_fila.append(
                f"{nombre_archivo}, fila {numero_fila}: "
                "la disponibilidad debe ser SI o NO."
            )

        # Crear el objeto únicamente si la fila es válida.
        if not errores_fila:

            panel = Panel(
                id_panel=id_panel,
                altura_mm=altura,
                familia=familia,
                disponible=(disponibilidad == "SI")
            )

            paneles.append(panel)

        # Acumular los errores encontrados.
        errores_totales.extend(errores_fila)

    return paneles, errores_totales



# ============================================================
# BLOQUE 9: VALIDACIÓN DE POSICIONES
#
# Comprueba los datos de cada posición y su orden dentro
# del muro.
#
# REGLAS NUEVAS:
# - El orden debe comenzar en 1.
# - No se permiten órdenes negativos ni iguales a cero.
# - No se permiten órdenes repetidos.
# - La secuencia debe ser consecutiva.
# - Las posiciones se devuelven ordenadas por su número.
# ============================================================

def validar_posiciones(
    filas: list[dict[str, str | None]],
    nombre_archivo: str = "posiciones.csv"
) -> tuple[list[Posicion], list[str]]:

    posiciones = []
    errores_totales = []

    ids_vistos = set()
    ordenes_vistos = set()

    ordenes_validos = True

    # Comprobar los encabezados.
    errores_encabezados = validar_encabezados(
        filas,
        COLUMNAS_POSICIONES,
        nombre_archivo
    )

    if errores_encabezados:
        return [], errores_encabezados

    # Recorrer los registros.
    for numero_fila, fila in enumerate(filas, start=2):

        errores_fila = []

        # ----------------------------------------------------
        # VALIDAR ORDEN
        # ----------------------------------------------------

        orden = convertir_entero(
            fila.get("orden"),
            "orden",
            nombre_archivo,
            numero_fila,
            errores_fila
        )

        if orden is None:

            ordenes_validos = False

        elif orden < 1:

            errores_fila.append(
                f"{nombre_archivo}, fila {numero_fila}: "
                "el orden debe ser mayor o igual a 1."
            )

            ordenes_validos = False

        elif orden in ordenes_vistos:

            errores_fila.append(
                f"{nombre_archivo}, fila {numero_fila}: "
                f"el orden '{orden}' está repetido."
            )

            ordenes_validos = False

        else:

            ordenes_vistos.add(orden)

        # ----------------------------------------------------
        # VALIDAR IDENTIFICADOR
        # ----------------------------------------------------

        id_posicion = normalizar_identificador(
            fila.get("id_posicion")
        )

        if not id_posicion:

            errores_fila.append(
                f"{nombre_archivo}, fila {numero_fila}: "
                "el identificador de la posición está vacío."
            )

        elif id_posicion in ids_vistos:

            errores_fila.append(
                f"{nombre_archivo}, fila {numero_fila}: "
                f"el identificador '{id_posicion}' está repetido."
            )

        else:

            ids_vistos.add(id_posicion)

        # ----------------------------------------------------
        # VALIDAR UBICACIÓN
        # ----------------------------------------------------

        ubicacion = limpiar_texto(
            fila.get("ubicacion")
        )

        if not ubicacion:

            errores_fila.append(
                f"{nombre_archivo}, fila {numero_fila}: "
                "la ubicación está vacía."
            )

        # ----------------------------------------------------
        # VALIDAR COTA DE APOYO
        # ----------------------------------------------------

        cota_apoyo = convertir_entero(
            fila.get("cota_apoyo_mm"),
            "cota_apoyo_mm",
            nombre_archivo,
            numero_fila,
            errores_fila,
            permitir_negativo=True
        )

        # ----------------------------------------------------
        # VALIDAR ALTURA MÍNIMA
        # ----------------------------------------------------

        altura_min = convertir_entero(
            fila.get("altura_min_mm"),
            "altura_min_mm",
            nombre_archivo,
            numero_fila,
            errores_fila
        )

        # ----------------------------------------------------
        # VALIDAR ALTURA MÁXIMA
        # ----------------------------------------------------

        altura_max = convertir_entero(
            fila.get("altura_max_mm"),
            "altura_max_mm",
            nombre_archivo,
            numero_fila,
            errores_fila
        )

        # Comprobar que el intervalo no esté invertido.
        if (
            altura_min is not None
            and altura_max is not None
            and altura_min > altura_max
        ):

            errores_fila.append(
                f"{nombre_archivo}, fila {numero_fila}: "
                "la altura mínima es mayor que la altura máxima."
            )

        # ----------------------------------------------------
        # VALIDAR FAMILIA
        # ----------------------------------------------------

        familia = normalizar_familia(
            fila.get("familia_admitida")
        )

        if not familia:

            errores_fila.append(
                f"{nombre_archivo}, fila {numero_fila}: "
                "la familia admitida está vacía."
            )

        # ----------------------------------------------------
        # CREAR OBJETO POSICIÓN
        # ----------------------------------------------------

        if not errores_fila:

            posicion = Posicion(
                id_posicion=id_posicion,
                ubicacion=ubicacion,
                cota_apoyo_mm=cota_apoyo,
                altura_min_mm=altura_min,
                altura_max_mm=altura_max,
                familia_admitida=familia,
                orden=orden
            )

            posiciones.append(posicion)

        errores_totales.extend(errores_fila)

    # --------------------------------------------------------
    # COMPROBAR QUE LA SECUENCIA SEA CONSECUTIVA
    # --------------------------------------------------------

    if ordenes_validos:

        ordenes_esperados = set(
            range(1, len(filas) + 1)
        )

        ordenes_faltantes = (
            ordenes_esperados - ordenes_vistos
        )

        ordenes_fuera_rango = (
            ordenes_vistos - ordenes_esperados
        )

        if ordenes_faltantes or ordenes_fuera_rango:

            detalles = []

            if ordenes_faltantes:

                detalles.append(
                    "faltan los órdenes: "
                    + ", ".join(
                        map(str, sorted(ordenes_faltantes))
                    )
                )

            if ordenes_fuera_rango:

                detalles.append(
                    "están fuera de la secuencia esperada: "
                    + ", ".join(
                        map(str, sorted(ordenes_fuera_rango))
                    )
                )

            errores_totales.append(
                f"{nombre_archivo}: la columna 'orden' "
                "debe ser consecutiva desde 1. "
                + "; ".join(detalles)
                + "."
            )

    # --------------------------------------------------------
    # ORDENAR POSICIONES
    # --------------------------------------------------------

    posiciones.sort(
        key=lambda posicion: posicion.orden
    )

    return posiciones, errores_totales

