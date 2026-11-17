# PANELMSE

**Asistente de asignación de paneles prefabricados MSE**

PANELMSE es una aplicación de escritorio desarrollada en Python para apoyar la asignación de paneles prefabricados a posiciones de un muro MSE, a partir de dos archivos CSV: uno con la información de los paneles y otro con las posiciones disponibles.

> **Alcance:** PANELMSE comprueba compatibilidad de familia, disponibilidad y rango de altura. Es una herramienta de apoyo a la asignación; no sustituye la revisión ni el diseño estructural del muro y no calcula estabilidad, refuerzos, anclajes u otras verificaciones estructurales.

## Funciones

- Registro del responsable, nombre del proyecto y fecha indicada por el usuario.
- Selección de los archivos CSV de paneles y posiciones.
- Lectura y validación de los datos de entrada.
- Asignación de paneles a posiciones compatibles, buscando maximizar la cantidad de posiciones cubiertas.
- Visualización de asignaciones, posiciones pendientes y paneles sobrantes.
- Exportación de resultados a CSV e informe PDF con identificación del proyecto y archivos de entrada.

## Requisitos

- Windows para utilizar la interfaz de escritorio y el instalador incluidos en el proyecto.
- Python para ejecutar el código fuente.
- Dependencias de Python indicadas en `requirements.txt`.

El ejecutable distribuido mediante el instalador se empaqueta con PyInstaller; el usuario final no necesita instalar Python para utilizar esa versión.

## Ejecutar desde el código fuente

Desde la carpeta raíz del repositorio:

```bash
python -m pip install -r requirements.txt
python -m src.panelmse.gui
```

## Archivos CSV de entrada

Los archivos de entrada utilizan separador punto y coma (`;`) y codificación UTF-8-SIG.

### `paneles.csv`

Encabezados requeridos:

```text
id_panel;altura_mm;familia;disponible
```

- `id_panel`: identificador del panel.
- `altura_mm`: altura del panel en milímetros.
- `familia`: código de familia del panel.
- `disponible`: disponibilidad (`SI` o `NO`).

### `posiciones.csv`

Encabezados requeridos:

```text
id_posicion;ubicacion;cota_apoyo_mm;altura_min_mm;altura_max_mm;familia_admitida
```

- `id_posicion`: identificador de la posición.
- `ubicacion`: descripción de la ubicación.
- `cota_apoyo_mm`: cota de apoyo en milímetros.
- `altura_min_mm` y `altura_max_mm`: intervalo permitido de altura, en milímetros.
- `familia_admitida`: familia admitida para la posición.

La altura del panel debe estar dentro del intervalo permitido, incluidos sus extremos, y la familia debe coincidir. Cada panel y cada posición pueden participar como máximo en una asignación.

## Archivos de salida

La exportación CSV produce:

- `identificacion_proyecto.csv`
- `asignaciones.csv`
- `posiciones_pendientes.csv`
- `paneles_sobrantes.csv`
- `resumen.csv`

También se puede generar un informe PDF con la identificación del proyecto, resumen, tablas y aclaración del alcance.

## Estructura del proyecto

```text
PANELMSE/
├── launcher.py
├── PANELMSE.iss
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── .gitignore
└── src/
    └── panelmse/
        ├── __init__.py
        ├── gui.py
        ├── main.py
        ├── models.py
        ├── csv_loader.py
        ├── validators.py
        ├── assignment.py
        ├── results.py
        └── assets/
            └── PANELMSE.ico
```

La estructura anterior describe los archivos principales; pueden existir otros archivos auxiliares del proyecto.

## Crear el ejecutable e instalador (Windows)

Instalar las dependencias de desarrollo:

```bash
python -m pip install -r requirements-dev.txt
```

Generar la carpeta ejecutable:

```bash
python -m PyInstaller --noconfirm --clean --onedir --windowed --name PANELMSE --icon "src\\panelmse\\assets\\PANELMSE.ico" --add-data "src\\panelmse\\assets\\PANELMSE.ico;src\\panelmse\\assets" --collect-data customtkinter --collect-all reportlab launcher.py
```

Después, abrir `PANELMSE.iss` con Inno Setup Compiler y compilarlo para producir el instalador de Windows.

## Pruebas

El proyecto cuenta con una batería manual de diez escenarios de validación que cubren el caso normal, límites de altura, familias incompatibles, disponibilidad, reasignación, datos inválidos, duplicados, encabezados faltantes y casos sin solución completa. Se recomienda repetir las pruebas al modificar la lógica o las validaciones.

## Colaboración

PANELMSE es un proyecto académico desarrollado por un equipo. Antes de subir cambios, revisa los archivos modificados, escribe un mensaje de commit descriptivo y sincroniza los cambios con el repositorio remoto.

## Datos y privacidad

No subas al repositorio archivos CSV, PDF o informes que contengan datos reales, nombres de clientes, información personal o información confidencial. Para ejemplos y pruebas compartidas, utiliza datos sintéticos.
