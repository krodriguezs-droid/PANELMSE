
# ============================================================
# PANELMSE - wall_geometry.py
# FUNCIÓN:
# Calcular cuántos paneles caben en la longitud del muro
# y cuánto espacio queda sin cubrir.
# ============================================================

from decimal import Decimal, InvalidOperation


def convertir_medida(valor, nombre):
    """
    Convierte una medida ingresada por el usuario a Decimal.
    Permite utilizar punto o coma como separador decimal.
    """

    try:
        medida = Decimal(str(valor).strip().replace(",", "."))

    except (InvalidOperation, ValueError):
        raise ValueError(
            f"La {nombre} debe ser un número válido."
        )

    if not medida.is_finite() or medida <= 0:
        raise ValueError(
            f"La {nombre} debe ser mayor que cero."
        )

    return medida


def calcular_distribucion_longitud(
    longitud_muro_m,
    longitud_panel_m
):
    """
    Calcula el número de paneles necesarios según
    la longitud total del muro.

    No se redondea hacia arriba.
    El espacio sobrante permanece sin cubrir.
    """

    longitud_muro = convertir_medida(
        longitud_muro_m,
        "longitud del muro"
    )

    longitud_panel = convertir_medida(
        longitud_panel_m,
        "longitud del panel"
    )

    # La longitud del panel debe ser menor que la del muro.
    if longitud_panel >= longitud_muro:

        raise ValueError(
            "La longitud del panel debe ser menor "
            "que la longitud total del muro."
        )

    # Calcular cuántos paneles completos caben.
    cantidad_paneles = int(
        longitud_muro // longitud_panel
    )

    # Calcular la longitud ocupada.
    longitud_cubierta = (
        cantidad_paneles * longitud_panel
    )

    # Calcular el espacio sobrante.
    espacio_sobrante = (
        longitud_muro - longitud_cubierta
    )

    return {
        "cantidad_paneles_necesarios": cantidad_paneles,
        "longitud_cubierta_m": longitud_cubierta,
        "espacio_sobrante_m": espacio_sobrante
    }

# ============================================================
# GENERAR POSICIONES GEOMETRICAS DEL MURO
#
# Funcion:
# Crear una posicion por cada panel que cabe en la longitud
# disponible.
#
# Cada posicion recibe:
# - Un orden consecutivo.
# - Una identificacion geometrica.
# - Una progresiva inicial.
# - Una progresiva final.
#
# Estas posiciones seran la referencia principal para
# compararlas posteriormente con el CSV del usuario.
# ============================================================

def generar_posiciones_geometricas(
    longitud_muro_m,
    longitud_panel_m
):
    # Calcular primero la distribucion longitudinal.
    distribucion = calcular_distribucion_longitud(
        longitud_muro_m,
        longitud_panel_m
    )

    longitud_panel = convertir_medida(
        longitud_panel_m,
        "longitud del panel"
    )

    cantidad = distribucion[
        "cantidad_paneles_necesarios"
    ]

    posiciones = []

    # Crear una posicion por cada panel que cabe.
    for orden in range(1, cantidad + 1):

        # Calcular el inicio y final de cada posicion.
        inicio = (orden - 1) * longitud_panel
        final = orden * longitud_panel

        posiciones.append({
            "orden": orden,
            "id_posicion_geometrica": f"G{orden:03d}",
            "progresiva_inicio_m": inicio,
            "progresiva_fin_m": final
        })

    return {
        "cantidad_paneles_necesarios": cantidad,
        "longitud_cubierta_m": distribucion[
            "longitud_cubierta_m"
        ],
        "espacio_sobrante_m": distribucion[
            "espacio_sobrante_m"
        ],
        "posiciones_geometricas": posiciones
    }

# ============================================================
# COMPARAR POSICIONES GEOMETRICAS CON EL CSV
#
# La geometria determina la cantidad y el orden.
# El CSV proporciona los datos particulares de cada posicion.
# ============================================================

def comparar_posiciones_geometricas(
    resultado_geometrico,
    posiciones_csv
):
    posiciones_geometricas = resultado_geometrico.get(
        "posiciones_geometricas", []
    )

    posiciones_por_orden = {}
    ordenes_duplicados = []
    ordenes_invalidos = []

    # Organizar las posiciones del CSV por su orden.
    for posicion in posiciones_csv:

        orden = getattr(posicion, "orden", None)

        if not isinstance(orden, int) or orden < 1:
            ordenes_invalidos.append(orden)
            continue

        if orden in posiciones_por_orden:
            ordenes_duplicados.append(orden)
            continue

        posiciones_por_orden[orden] = posicion

    # Obtener los órdenes generados por la geometría.
    ordenes_geometricos = {
        posicion["orden"]
        for posicion in posiciones_geometricas
    }

    ordenes_csv = set(posiciones_por_orden.keys())

    # Detectar posiciones faltantes y adicionales.
    ordenes_faltantes = sorted(
        ordenes_geometricos - ordenes_csv
    )

    ordenes_adicionales = sorted(
        ordenes_csv - ordenes_geometricos
    )

    # Relacionar cada posición geométrica con su registro CSV.
    coincidencias = []

    for posicion_geometrica in posiciones_geometricas:

        orden = posicion_geometrica["orden"]

        if orden in posiciones_por_orden:

            posicion_csv = posiciones_por_orden[orden]

            coincidencias.append({
                "orden": orden,
                "id_posicion_geometrica":
                    posicion_geometrica["id_posicion_geometrica"],
                "progresiva_inicio_m":
                    posicion_geometrica["progresiva_inicio_m"],
                "progresiva_fin_m":
                    posicion_geometrica["progresiva_fin_m"],
                "id_posicion_csv": posicion_csv.id_posicion,
                "ubicacion": posicion_csv.ubicacion,
                "cota_apoyo_mm": posicion_csv.cota_apoyo_mm,
                "altura_min_mm": posicion_csv.altura_min_mm,
                "altura_max_mm": posicion_csv.altura_max_mm,
                "familia_admitida": posicion_csv.familia_admitida
            })

    # Determinar si ambas fuentes coinciden completamente.
    coincide = (
        not ordenes_faltantes
        and not ordenes_adicionales
        and not ordenes_duplicados
        and not ordenes_invalidos
        and len(posiciones_geometricas) == len(posiciones_csv)
    )

    return {
        "coincide": coincide,
        "cantidad_posiciones_geometricas":
            len(posiciones_geometricas),
        "cantidad_posiciones_csv":
            len(posiciones_csv),
        "ordenes_faltantes_csv": ordenes_faltantes,
        "ordenes_adicionales_csv": ordenes_adicionales,
        "ordenes_duplicados_csv": sorted(set(ordenes_duplicados)),
        "ordenes_invalidos_csv": ordenes_invalidos,
        "posiciones_coincidentes": coincidencias
    }
