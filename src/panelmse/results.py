
# ============================================================
# PANELMSE - results.py
# FUNCIÓN DEL ARCHIVO:
# Organizar los resultados de la asignación de paneles.
#
# RESULTADOS:
# 1. Tabla de posiciones y paneles asignados.
# 2. Cota superior resultante.
# 3. Posiciones pendientes.
# 4. Paneles sobrantes.
# ============================================================


# ============================================================
# BLOQUE 1: IMPORTACIONES
# FUNCIÓN:
# Importar los modelos Panel y Posicion para trabajar
# con la información de los elementos del muro.
# ============================================================

from .models import Panel, Posicion

# ============================================================
# BLOQUE 2: PREPARAR LOS RESULTADOS
# FUNCIÓN:
# Recibir los paneles, las posiciones y las asignaciones.
# Organizar la información y calcular las cotas superiores.
#
# ENTRADAS:
# paneles: lista de paneles registrados.
# posiciones: lista de posiciones registradas.
# asignaciones: diccionario posición -> panel.
#
# RESULTADO:
# Diccionario con asignaciones, pendientes, sobrantes
# y cantidades totales.
# ============================================================

def preparar_resultados(
    paneles: list[Panel],
    posiciones: list[Posicion],
    asignaciones: dict[str, Panel]
) -> dict:

    # --------------------------------------------------------
    # A. IDENTIFICAR LOS PANELES UTILIZADOS
    # FUNCIÓN:
    # Crear un conjunto con los identificadores de los paneles
    # que ya fueron asignados.
    # --------------------------------------------------------

    paneles_utilizados = {
        panel.id_panel
        for panel in asignaciones.values()
    }

    # --------------------------------------------------------
    # B. IDENTIFICAR LAS POSICIONES CUBIERTAS
    # FUNCIÓN:
    # Registrar cuáles posiciones recibieron un panel.
    # --------------------------------------------------------

    posiciones_cubiertas = set(asignaciones.keys())

    # --------------------------------------------------------
    # C. CONSTRUIR LA TABLA DE ASIGNACIONES
    # FUNCIÓN:
    # Recorrer las posiciones en orden de identificador
    # y preparar la información de cada asignación.
    # --------------------------------------------------------

    tabla_asignaciones = []

    posiciones_ordenadas = sorted(
        posiciones,
        key=lambda posicion: posicion.id_posicion
    )

    for posicion in posiciones_ordenadas:

        # Buscar el panel asignado a esta posición.
        panel = asignaciones.get(posicion.id_posicion)

        # Si no existe un panel asignado, continuar.
        if panel is None:
            continue

        # Calcular la cota superior resultante.
        cota_superior = (
            posicion.cota_apoyo_mm + panel.altura_mm
        )

        # Agregar los datos a la tabla.
        tabla_asignaciones.append({

            "id_posicion": posicion.id_posicion,

            "ubicacion": posicion.ubicacion,

            "id_panel": panel.id_panel,

            "altura_panel_mm": panel.altura_mm,

            "cota_apoyo_mm": posicion.cota_apoyo_mm,

            "cota_superior_mm": cota_superior

        })

    # --------------------------------------------------------
    # D. IDENTIFICAR LAS POSICIONES PENDIENTES
    # FUNCIÓN:
    # Encontrar las posiciones que no recibieron ningún panel.
    # --------------------------------------------------------

    posiciones_pendientes = [

        posicion

        for posicion in posiciones_ordenadas

        if posicion.id_posicion not in posiciones_cubiertas

    ]

    # --------------------------------------------------------
    # E. IDENTIFICAR LOS PANELES SOBRANTES
    # FUNCIÓN:
    # Encontrar los paneles disponibles que no fueron usados.
    #
    # Los paneles NO habilitados no se consideran sobrantes,
    # porque están excluidos del proceso de asignación.
    # --------------------------------------------------------

    paneles_sobrantes = sorted(

        [

            panel

            for panel in paneles

            if (
                panel.disponible
                and panel.id_panel not in paneles_utilizados
            )

        ],

        key=lambda panel: panel.id_panel

    )

    # --------------------------------------------------------
    # F. ORGANIZAR EL RESUMEN
    # FUNCIÓN:
    # Contabilizar las asignaciones, posiciones pendientes
    # y paneles sobrantes.
    # --------------------------------------------------------

    resultados = {

        "asignaciones": tabla_asignaciones,

        "posiciones_pendientes": posiciones_pendientes,

        "paneles_sobrantes": paneles_sobrantes,

        "total_posiciones": len(posiciones),

        "total_asignadas": len(tabla_asignaciones),

        "total_pendientes": len(posiciones_pendientes),

        "total_paneles_sobrantes": len(paneles_sobrantes)

    }

    # Devolver todos los resultados organizados.
    return resultados
