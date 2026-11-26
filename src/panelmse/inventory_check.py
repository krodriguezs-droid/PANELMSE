
# ============================================================
# PANELMSE - inventory_check.py
#
# OBJETIVO:
# Comprobar que los paneles del inventario pueden utilizarse
# en las posiciones del muro.
#
# CONDICIONES:
# 1. Panel disponible.
# 2. Familia compatible.
# 3. Altura dentro del intervalo de la posicion.
# 4. Altura perteneciente a los niveles del muro.
#
# IMPORTANTE:
# Este modulo identifica candidatos.
# Todavia no realiza la asignacion definitiva ni comprueba
# la progresion entre paneles consecutivos.
# ============================================================

from .height_progression import generar_niveles_altura


# ============================================================
# EVALUAR INVENTARIO POR POSICION
# ============================================================

def evaluar_inventario_por_posicion(
    paneles,
    posiciones,
    altura_inicial_m,
    altura_final_m,
    paso_altura_m=0.05
):
    # Generar los niveles permitidos para el muro.
    niveles_altura = generar_niveles_altura(
        altura_inicial_m,
        altura_final_m,
        paso_altura_m
    )

    niveles_permitidos = set(niveles_altura)

    # Ordenar las posiciones longitudinalmente.
    posiciones_ordenadas = sorted(
        posiciones,
        key=lambda posicion: posicion.orden
    )

    # Ordenar los paneles por identificador.
    paneles_ordenados = sorted(
        paneles,
        key=lambda panel: panel.id_panel
    )

    # Almacenar candidatos y rechazos.
    candidatos_por_posicion = []
    paneles_aptos_por_id = {}

    # Motivos de rechazo.
    motivos = (
        "no_disponible",
        "familia_incompatible",
        "fuera_intervalo_altura",
        "no_cumple_paso_altura"
    )

    # --------------------------------------------------------
    # REVISAR CADA POSICION
    # --------------------------------------------------------

    for posicion in posiciones_ordenadas:

        candidatos = []

        rechazados = {
            motivo: []
            for motivo in motivos
        }

        # Revisar cada panel disponible en el inventario.
        for panel in paneles_ordenados:

            motivo_rechazo = None

            # 1. Comprobar disponibilidad.
            if not panel.disponible:

                motivo_rechazo = "no_disponible"

            # 2. Comprobar familia.
            elif panel.familia != posicion.familia_admitida:

                motivo_rechazo = "familia_incompatible"

            # 3. Comprobar intervalo de altura.
            elif not (
                posicion.altura_min_mm
                <= panel.altura_mm
                <= posicion.altura_max_mm
            ):

                motivo_rechazo = "fuera_intervalo_altura"

            # 4. Comprobar nivel de altura del muro.
            elif panel.altura_mm not in niveles_permitidos:

                motivo_rechazo = "no_cumple_paso_altura"

            # Si cumple todas las condiciones, es candidato.
            if motivo_rechazo is None:

                candidatos.append(panel)

                paneles_aptos_por_id[panel.id_panel] = panel

            else:

                rechazados[motivo_rechazo].append(
                    panel.id_panel
                )

        candidatos_por_posicion.append({
            "orden": posicion.orden,
            "id_posicion": posicion.id_posicion,
            "ubicacion": posicion.ubicacion,
            "cantidad_candidatos": len(candidatos),
            "paneles_candidatos": candidatos,
            "ids_paneles_candidatos": [
                panel.id_panel for panel in candidatos
            ],
            "rechazados": rechazados
        })

    # --------------------------------------------------------
    # IDENTIFICAR LOS PANELES SIN NINGUNA POSICION COMPATIBLE
    # --------------------------------------------------------

    ids_aptos = set(paneles_aptos_por_id)

    paneles_sin_posicion = [
        panel
        for panel in paneles_ordenados
        if panel.id_panel not in ids_aptos
    ]

    # --------------------------------------------------------
    # DEVOLVER RESULTADOS
    # --------------------------------------------------------

    return {
        "niveles_altura_mm": niveles_altura,

        "total_paneles_inventario": len(paneles),

        "total_paneles_disponibles": sum(
            1 for panel in paneles if panel.disponible
        ),

        "total_paneles_aptos": len(paneles_aptos_por_id),

        "paneles_aptos": list(
            paneles_aptos_por_id.values()
        ),

        "paneles_sin_posicion_compatible":
            paneles_sin_posicion,

        "total_posiciones": len(posiciones_ordenadas),

        "posiciones_sin_candidatos": [
            resultado["orden"]
            for resultado in candidatos_por_posicion
            if resultado["cantidad_candidatos"] == 0
        ],

        "candidatos_por_posicion": candidatos_por_posicion
    }
