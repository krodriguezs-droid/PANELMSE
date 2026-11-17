# ============================================================
# PANELMSE - LANZADOR DE LA APLICACIÓN
# Punto de entrada para crear el ejecutable.
# ============================================================

# Importar la clase principal de la interfaz.
from src.panelmse.gui import PanelMSEApp


def main():

    # Crear la ventana principal.
    aplicacion = PanelMSEApp()

    # Mantener activa la interfaz.
    aplicacion.mainloop()


# Ejecutar la aplicación.
if __name__ == "__main__":
    main()