
# ============================================================
# PANELMSE - assignment.py
# FUNCIÓN DEL ARCHIVO:
# Asignar paneles prefabricados a posiciones compatibles
# procurando cubrir la mayor cantidad posible de posiciones.
# ============================================================


# ============================================================
# BLOQUE 1: IMPORTACIONES
# FUNCIÓN:
# Importar los modelos Panel y Posicion que representan
# los elementos que participarán en la asignación.
# ============================================================

from .models import Panel, Posicion

# ============================================================
# BLOQUE 2: COMPROBAR COMPATIBILIDAD
# FUNCIÓN:
# Determinar si un panel puede ocupar una posición.
#
# CONDICIONES:
# 1. El panel debe estar disponible.
# 2. Su familia debe coincidir con la familia admitida.
# 3. Su altura debe estar dentro del intervalo permitido.
#
# Los límites de altura son inclusivos.
# ============================================================

def es_compatible(panel: Panel, posicion: Posicion) -> bool:

    # Comprobar disponibilidad.
    if not panel.disponible:
        return False

    # Comprobar compatibilidad de familias.
    if panel.familia != posicion.familia_admitida:
        return False

    # Comprobar que la altura esté dentro del intervalo.
    return posicion.altura_min_mm <= panel.altura_mm <= posicion.altura_max_mm


# ============================================================
# BLOQUE 3: CONSTRUIR LAS RELACIONES DE COMPATIBILIDAD
# FUNCIÓN:
# Ordenar paneles y posiciones por identificador.
# Identificar qué paneles pueden ocupar cada posición.
#
# RESULTADO:
# Un diccionario donde cada posición tiene una lista
# de paneles compatibles.
# ============================================================

def construir_compatibilidades(
    paneles: list[Panel],
    posiciones: list[Posicion]
) -> dict[str, list[Panel]]:

    # Ordenar los paneles por identificador.
    paneles_ordenados = sorted(
        [p for p in paneles if p.disponible],
        key=lambda panel: panel.id_panel
    )

    # Ordenar las posiciones por identificador.
    posiciones_ordenadas = sorted(
        posiciones,
        key=lambda posicion: posicion.id_posicion
    )

    # Diccionario que almacenará las compatibilidades.
    compatibilidades = {}

    # Revisar cada posición.
    for posicion in posiciones_ordenadas:

        # Lista de paneles que pueden ocupar esta posición.
        paneles_compatibles = []

        # Revisar los paneles disponibles.
        for panel in paneles_ordenados:

            if es_compatible(panel, posicion):
                paneles_compatibles.append(panel)

        # Guardar los paneles compatibles con la posición.
        compatibilidades[posicion.id_posicion] = paneles_compatibles

    return compatibilidades


# ============================================================
# BLOQUE 4: ALGORITMO DE REUBICACIÓN
# FUNCIÓN:
# Intentar asignar un panel a una posición.
#
# Si el panel ya está ocupado por otra posición, intenta
# encontrar otro panel para la posición que lo ocupa.
#
# Esto permite reorganizar asignaciones anteriores
# para conseguir cubrir más posiciones.
# ============================================================

def intentar_asignar(
    posicion: Posicion,
    compatibilidades: dict[str, list[Panel]],
    asignacion_por_panel: dict[str, Posicion],
    paneles_visitados: set[str]
) -> bool:

    # Revisar los paneles compatibles en orden de identificador.
    for panel in compatibilidades[posicion.id_posicion]:

        # Evitar revisar dos veces el mismo panel en esta búsqueda.
        if panel.id_panel in paneles_visitados:
            continue

        paneles_visitados.add(panel.id_panel)

        # Averiguar si el panel ya está asignado.
        posicion_anterior = asignacion_por_panel.get(
            panel.id_panel
        )

        # Si el panel está libre, se puede asignar directamente.
        # Si está ocupado, intentar reubicar la asignación anterior.
        if (
            posicion_anterior is None
            or intentar_asignar(
                posicion_anterior,
                compatibilidades,
                asignacion_por_panel,
                paneles_visitados
            )
        ):

            # Registrar la nueva asignación.
            asignacion_por_panel[panel.id_panel] = posicion

            return True

    # No fue posible encontrar un panel para esta posición.
    return False


# ============================================================
# BLOQUE 5: FUNCIÓN PRINCIPAL DE ASIGNACIÓN
# FUNCIÓN:
# Coordinar el proceso completo de asignación.
#
# ENTRADAS:
# Lista de paneles validados.
# Lista de posiciones validadas.
#
# RESULTADO:
# Diccionario con el identificador de cada posición
# y el objeto Panel que se le asignó.
# ============================================================

def asignar_paneles(
    paneles: list[Panel],
    posiciones: list[Posicion]
) -> dict[str, Panel]:

    # Ordenar las posiciones por identificador.
    posiciones_ordenadas = sorted(
        posiciones,
        key=lambda posicion: posicion.id_posicion
    )

    # Construir las relaciones de compatibilidad.
    compatibilidades = construir_compatibilidades(
        paneles,
        posiciones_ordenadas
    )

    # Diccionario que registra qué posición ocupa cada panel.
    asignacion_por_panel = {}

    # Intentar asignar un panel a cada posición.
    for posicion in posiciones_ordenadas:

        # Cada búsqueda comienza con un conjunto vacío.
        # Este conjunto evita ciclos durante la reubicación.
        paneles_visitados = set()

        intentar_asignar(
            posicion,
            compatibilidades,
            asignacion_por_panel,
            paneles_visitados
        )

    # Crear un diccionario para consultar los paneles por ID.
    paneles_por_id = {
        panel.id_panel: panel
        for panel in paneles
    }

    # Convertir el resultado a posición -> panel.
    asignaciones_por_posicion = {}

    for id_panel, posicion in asignacion_por_panel.items():

        asignaciones_por_posicion[posicion.id_posicion] = (
            paneles_por_id[id_panel]
        )

    # Devolver las asignaciones ordenadas por identificador.
    return dict(sorted(asignaciones_por_posicion.items()))
