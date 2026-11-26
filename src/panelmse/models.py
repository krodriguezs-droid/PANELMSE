
# ============================================================
# PANELMSE - models.py
# FUNCIÓN DEL ARCHIVO:
# Definir las estructuras que representan los paneles
# prefabricados y las posiciones del muro MSE.
# ============================================================


# ============================================================
# IMPORTACIÓN:
# dataclass permite crear clases destinadas a almacenar datos
# de manera organizada.
# ============================================================

from dataclasses import dataclass

# ============================================================
# MODELO 1: PANEL
# FUNCIÓN:
# Representar un panel prefabricado de concreto.
#
# ATRIBUTOS:
# id_panel: identificador único del panel.
# altura_mm: altura real del panel en milímetros.
# familia: familia de compatibilidad del panel.
# disponible: indica si el panel está habilitado.
# ============================================================

@dataclass
class Panel:
    id_panel: str
    altura_mm: int
    familia: str
    disponible: bool


# ============================================================
# MODELO 2: POSICION
# FUNCIÓN:
# Representar una posición pendiente del muro MSE.
#
# ATRIBUTOS:
# id_posicion: identificador único de la posición.
# ubicacion: descripción de su ubicación en el muro.
# cota_apoyo_mm: cota de apoyo en milímetros.
# altura_min_mm: altura mínima permitida.
# altura_max_mm: altura máxima permitida.
# familia_admitida: familia compatible con la posición.
# orden: posición consecutiva que ocupa en el muro,
# comenzando desde 1.
# ============================================================

@dataclass
class Posicion:
    id_posicion: str
    ubicacion: str
    cota_apoyo_mm: int
    altura_min_mm: int
    altura_max_mm: int
    familia_admitida: str
    orden: int = 0
