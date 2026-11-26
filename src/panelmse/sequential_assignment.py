
# ============================================================
# PANELMSE - sequential_assignment.py
#
# OBJETIVO:
# Asignar paneles respetando el orden longitudinal del muro
# y la progresion de alturas.
#
# REGLAS:
# - Cada panel se utiliza una sola vez.
# - Se respeta la disponibilidad y la familia.
# - Se respetan los intervalos de las posiciones.
# - Se respeta la progresion ascendente, descendente o plana.
# - Se permite el modo estricto y flexible.
# - No se permiten huecos entre posiciones asignadas.
#
# El algoritmo busca la mayor cantidad de posiciones
# consecutivas que puedan cubrirse.
# ============================================================

from functools import cache

from .assignment import es_compatible
from .height_progression import convertir_altura_mm, generar_niveles_altura

# ============================================================
# BLOQUE 1: COMPROBAR TRANSICION ENTRE DOS ALTURAS
# ============================================================

def transicion_valida(
    altura_anterior,
    altura_actual,
    direccion,
    salto_maximo
):

    diferencia = altura_actual - altura_anterior

    # Muro ascendente.
    if direccion == 1:
        return 0 <= diferencia <= salto_maximo

    # Muro descendente.
    if direccion == -1:
        return -salto_maximo <= diferencia <= 0

    # Planicie.
    return diferencia == 0


# ============================================================
# BLOQUE 2: ASIGNACION SECUENCIAL PRINCIPAL
# ============================================================

def asignar_paneles_secuencialmente(
    paneles,
    posiciones,
    altura_inicial_m,
    altura_final_m,
    paso_altura_m=0.05,
    modo_flexible=False
):

    # --------------------------------------------------------
    # A. VALIDAR LAS ALTURAS DEL MURO
    # --------------------------------------------------------

    altura_inicial = convertir_altura_mm(
        altura_inicial_m,
        "altura inicial"
    )

    altura_final = convertir_altura_mm(
        altura_final_m,
        "altura final"
    )

    paso_altura = convertir_altura_mm(
        paso_altura_m,
        "paso de altura"
    )

    niveles = generar_niveles_altura(
        altura_inicial_m,
        altura_final_m,
        paso_altura_m
    )

    niveles_permitidos = set(niveles)

    # --------------------------------------------------------
    # B. DETERMINAR LA DIRECCION DEL MURO
    # --------------------------------------------------------

    if altura_final > altura_inicial:
        direccion = 1
        nombre_direccion = "ascendente"

    elif altura_final < altura_inicial:
        direccion = -1
        nombre_direccion = "descendente"

    else:
        direccion = 0
        nombre_direccion = "planicie"

    # --------------------------------------------------------
    # C. DETERMINAR EL SALTO MAXIMO
    # --------------------------------------------------------

    multiplicador = 2 if modo_flexible else 1

    salto_maximo = paso_altura * multiplicador

    # --------------------------------------------------------
    # D. VALIDAR Y ORDENAR LAS POSICIONES
    # --------------------------------------------------------

    if not posiciones:
        raise ValueError(
            "No hay posiciones para realizar la asignacion."
        )

    if any(
        not isinstance(getattr(posicion, "orden", None), int)
        for posicion in posiciones
    ):
        raise ValueError(
            "Todas las posiciones deben tener un orden entero."
        )

    posiciones_ordenadas = sorted(
        posiciones,
        key=lambda posicion: posicion.orden
    )

    ordenes = [
        posicion.orden
        for posicion in posiciones_ordenadas
    ]

    ordenes_esperados = list(
        range(1, len(posiciones_ordenadas) + 1)
    )

    if ordenes != ordenes_esperados:

        raise ValueError(
            "Las posiciones deben tener órdenes consecutivos "
            "desde 1, sin repetidos."
        )

    # --------------------------------------------------------
    # E. ORDENAR LOS PANELES
    # --------------------------------------------------------

    paneles_ordenados = sorted(
        paneles,
        key=lambda panel: panel.id_panel
    )


    # --------------------------------------------------------
    # F. CONSTRUIR CANDIDATOS Y DIAGNOSTICAR EL INVENTARIO
    # --------------------------------------------------------

    candidatos_por_posicion = []
    ids_candidatos_por_posicion = []
    rechazos_por_posicion = []

    for indice, posicion in enumerate(posiciones_ordenadas):

        candidatos = []

        rechazados = {
            "no_disponible": [],
            "familia_incompatible": [],
            "fuera_intervalo_altura": [],
            "no_cumple_paso_altura": [],
            "no_cumple_altura_inicial": []
        }

        for indice_panel, panel in enumerate(paneles_ordenados):

            motivo = None

            # 1. Comprobar disponibilidad.
            if not panel.disponible:

                motivo = "no_disponible"

            # 2. Comprobar familia.
            elif panel.familia != posicion.familia_admitida:

                motivo = "familia_incompatible"

            # 3. Comprobar intervalo de altura.
            elif not (
                posicion.altura_min_mm
                <= panel.altura_mm
                <= posicion.altura_max_mm
            ):

                motivo = "fuera_intervalo_altura"

            # 4. Comprobar niveles permitidos.
            elif panel.altura_mm not in niveles_permitidos:

                motivo = "no_cumple_paso_altura"

            # 5. Comprobar altura inicial.
            elif (
                indice == 0
                and panel.altura_mm != altura_inicial
            ):

                motivo = "no_cumple_altura_inicial"

            # Si cumple todas las condiciones es candidato.
            if motivo is None:

                candidatos.append(indice_panel)

            else:

                rechazados[motivo].append(
                    panel.id_panel
                )

        # Priorizar paneles que avancen hacia la altura final.
        if direccion == 1:

            candidatos.sort(
                key=lambda i: (
                    -paneles_ordenados[i].altura_mm,
                    paneles_ordenados[i].id_panel
                )
            )

        elif direccion == -1:

            candidatos.sort(
                key=lambda i: (
                    paneles_ordenados[i].altura_mm,
                    paneles_ordenados[i].id_panel
                )
            )

        else:

            candidatos.sort(
                key=lambda i: paneles_ordenados[i].id_panel
            )

        candidatos_por_posicion.append(candidatos)

        ids_candidatos_por_posicion.append({
            "orden": posicion.orden,
            "id_posicion": posicion.id_posicion,
            "cantidad_candidatos": len(candidatos),
            "ids_paneles_candidatos": [
                paneles_ordenados[i].id_panel
                for i in candidatos
            ]
        })

        rechazos_por_posicion.append({
            "orden": posicion.orden,
            "id_posicion": posicion.id_posicion,
            "motivos": rechazados
        })


    # --------------------------------------------------------
    # G. BUSCAR LA MEJOR SECUENCIA DE ASIGNACIONES
    # --------------------------------------------------------

    @cache
    def buscar(
        indice_posicion,
        altura_anterior,
        usados_mask
    ):

        # Si se recorrieron todas las posiciones,
        # se encontró el final de la secuencia.
        if indice_posicion >= len(posiciones_ordenadas):
            return ()

        mejor_camino = ()
        mejor_puntuacion = (-1, -1, -1)

        # Revisar los candidatos de la posicion actual.
        for indice_panel in candidatos_por_posicion[
            indice_posicion
        ]:

            bit = 1 << indice_panel

            # Evitar utilizar un panel más de una vez.
            if usados_mask & bit:
                continue

            panel = paneles_ordenados[indice_panel]
            altura = panel.altura_mm

            # Comprobar la progresion desde la segunda posicion.
            if altura_anterior is not None and not transicion_valida(
            altura_anterior,
            altura,
            direccion,
            salto_maximo
                ):
             continue

            # Buscar la mejor continuacion con este panel.
            sufijo = buscar(
                indice_posicion + 1,
                altura,
                usados_mask | bit
            )

            camino = (indice_panel,) + sufijo

            ultima_altura = paneles_ordenados[
                camino[-1]
            ].altura_mm

            cantidad = len(camino)

            completo = (
                cantidad == len(posiciones_ordenadas)
            )

            alcanza_final = (
                completo
                and ultima_altura == altura_final
            )

            # En caso de empate, favorecer la progresion
            # que mas se acerque a la altura final.
            avance = (
                (ultima_altura - altura_inicial) * direccion
                if direccion != 0
                else 0
            )

            puntuacion = (
                cantidad,
                int(alcanza_final),
                avance
            )

            if puntuacion > mejor_puntuacion:

                mejor_camino = camino
                mejor_puntuacion = puntuacion

        return mejor_camino

    camino = buscar(0, None, 0)

    # --------------------------------------------------------
    # H. CONSTRUIR LAS ASIGNACIONES
    # --------------------------------------------------------

    asignaciones = {}
    detalles = []
    ids_utilizados = set()

    cantidad_asignada = len(camino)

    for indice_posicion, indice_panel in enumerate(camino):

        posicion = posiciones_ordenadas[indice_posicion]
        panel = paneles_ordenados[indice_panel]

        asignaciones[posicion.id_posicion] = panel

        ids_utilizados.add(panel.id_panel)

        detalles.append({
            "orden": posicion.orden,
            "id_posicion": posicion.id_posicion,
            "ubicacion": posicion.ubicacion,
            "id_panel": panel.id_panel,
            "altura_panel_mm": panel.altura_mm,
            "cota_apoyo_mm": posicion.cota_apoyo_mm,
            "cota_superior_mm": (
                posicion.cota_apoyo_mm + panel.altura_mm
            )
        })

    # --------------------------------------------------------
    # I. IDENTIFICAR PENDIENTES Y SOBRANTES
    # --------------------------------------------------------

    posiciones_pendientes = (
        posiciones_ordenadas[cantidad_asignada:]
    )

    paneles_disponibles = [
        panel
        for panel in paneles_ordenados
        if panel.disponible
    ]

    paneles_no_disponibles = [
        panel
        for panel in paneles_ordenados
        if not panel.disponible
    ]

    paneles_sobrantes = [
        panel
        for panel in paneles_disponibles
        if panel.id_panel not in ids_utilizados
    ]

    # --------------------------------------------------------
    # J. COMPROBAR SI SE CUBRIO EL MURO COMPLETO
    # --------------------------------------------------------

    ultima_altura = (
        paneles_ordenados[camino[-1]].altura_mm
        if camino
        else None
    )

    todas_cubiertas = (
        cantidad_asignada == len(posiciones_ordenadas)
    )

    alcanza_final = (
        todas_cubiertas
        and ultima_altura == altura_final
    )

    # --------------------------------------------------------
    # K. PREPARAR ADVERTENCIAS
    # --------------------------------------------------------

    advertencias = []

    if posiciones_pendientes:

        siguiente = posiciones_pendientes[0]

        advertencias.append(
            f"No fue posible asignar un panel a la posicion "
            f"de orden {siguiente.orden}. Las posiciones "
            "siguientes quedan pendientes para no romper "
            "la secuencia del muro."
        )

    if todas_cubiertas and not alcanza_final:

        advertencias.append(
            "Todas las posiciones tienen panel, pero la "
            "ultima altura asignada no alcanza la altura "
            "final solicitada. Revise el inventario y "
            "el perfil de alturas."
        )

    if not camino:

        advertencias.append(
            "No existe un panel disponible y compatible "
            "para iniciar en la altura inicial."
        )

    # --------------------------------------------------------
    # L. DEVOLVER RESULTADOS
    # --------------------------------------------------------

    ids_candidatos = {
        paneles_ordenados[i].id_panel
        for candidatos in candidatos_por_posicion
        for i in candidatos
    }
# --------------------------------------------------------
# IDENTIFICAR PANELES SIN NINGUNA POSICION COMPATIBLE
# --------------------------------------------------------

    paneles_sin_posicion_compatible = [
        panel
        for panel in paneles_ordenados
        if panel.id_panel not in ids_candidatos
    ]

    paneles_disponibles_sin_candidato = [
        panel
        for panel in paneles_sin_posicion_compatible
        if panel.disponible
    ]

    ids_paneles_candidatos = sorted(ids_candidatos)

    ids_paneles_sin_posicion = [
       panel.id_panel
    for panel in paneles_sin_posicion_compatible
    ]

    return {
        "direccion_muro": nombre_direccion,
        "modo_altura": (
            "flexible" if modo_flexible else "estricto"
        ),
        "paso_altura_mm": paso_altura,
        "salto_maximo_mm": salto_maximo,
        "niveles_altura_mm": niveles,

        "candidatos_por_posicion": ids_candidatos_por_posicion,
        "rechazos_por_posicion": rechazos_por_posicion,

        "ids_paneles_candidatos": ids_paneles_candidatos,

        "ids_paneles_sin_posicion_compatible": (
        ids_paneles_sin_posicion
        ),

       "total_paneles_disponibles_sin_candidato": (
        len(paneles_disponibles_sin_candidato)
        ),

        "paneles_disponibles_sin_candidato": (
        paneles_disponibles_sin_candidato
        ),

        "total_paneles_inventario": len(paneles_ordenados),
        "total_paneles_disponibles": len(paneles_disponibles),
        "total_paneles_candidatos": len(ids_candidatos),
        "total_paneles_asignados": cantidad_asignada,
        "total_paneles_sobrantes": len(paneles_sobrantes),

        "total_posiciones": len(posiciones_ordenadas),
        "total_asignadas": cantidad_asignada,
        "total_pendientes": len(posiciones_pendientes),

        "asignaciones": asignaciones,
        "asignaciones_detalladas": detalles,
        "posiciones_pendientes": posiciones_pendientes,
        "paneles_sobrantes": paneles_sobrantes,
        "paneles_no_disponibles": paneles_no_disponibles,

        "ultima_altura_mm": ultima_altura,
        "todas_posiciones_cubiertas": todas_cubiertas,
        "alcanza_altura_final": alcanza_final,
        "progresion_valida": True,

        "advertencias": advertencias
    }
