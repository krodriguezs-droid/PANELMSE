# PANELMSE

**Asistente de asignación de paneles prefabricados MSE**

PANELMSE es una aplicación de escritorio desarrollada en Python para apoyar la asignación de paneles prefabricados a posiciones de un muro MSE, a partir de dos archivos CSV: uno con la información de los paneles y otro con las posiciones disponibles.

> **Alcance:** PANELMSE comprueba compatibilidad de familia, disponibilidad y rango de altura. Es una herramienta de apoyo a la asignación; no sustituye la revisión ni el diseño estructural del muro y no calcula estabilidad, refuerzos, anclajes u otras verificaciones estructurales.

## Funciones

- Registro del responsable, nombre tanto de proyecto y fecha indicada por el usuario.
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

#EXPERIENCIA

Durante el desarrollo del proyecto PANELMSE tuvimos la oportunidad de llevar un problema relacionado con la ingeniería civil a una solución práctica mediante programación en Python. El problema consistía en asignar paneles prefabricados de un muro MSE a las posiciones que podían recibirlos, procurando cubrir la mayor cantidad de posiciones posible sin utilizar paneles incompatibles ni modificar las condiciones de diseño. Al principio, el reto no era solamente escribir código: primero debíamos comprender el problema, definir qué información necesitaba el programa y establecer reglas que pudieran comprobarse con ejemplos.

Para empezar, decidimos trabajar con dos archivos CSV, uno de paneles y otro de posiciones, con las alturas y cotas en milímetros, y fijamos reglas claras: límites inclusivos, un panel por posición y exclusión de paneles no disponibles o de familia incompatible. Al estudiar la asignación comprendimos que escoger el primer panel compatible no siempre da el mejor resultado, así que implementamos una estrategia que reorganiza asignaciones previas para cubrir más posiciones. Fue un aprendizaje entender que el orden de las decisiones cambia el resultado y que el algoritmo debe responder a las reglas del problema.

Usamos ChatGPT como apoyo para proponer código, generar ejemplos y revisar errores, pero aprendimos que sus respuestas no se aceptan sin más: había que leerlas, ejecutarlas y comparar los resultados con casos que pudiéramos comprobar manualmente. Dividir el trabajo en componentes (lectura de archivos, validaciones, algoritmo, resultados e interfaz) nos ayudó a corregir partes sin rehacer todo. Al integrar surgieron ajustes inesperados, como la forma de ejecutar la aplicación por las importaciones entre módulos, el icono de la ventana y la unificación del nombre del lanzador, lo que nos mostró que un programa puede funcionar por partes y aun así necesitar revisión al entregarse.

La interfaz, hecha con CustomTkinter, permite cargar los archivos, ejecutar el cálculo y ver asignaciones, posiciones pendientes y paneles sobrantes. También se agregó la exportación a CSV y un informe PDF, y se preparó la distribución con PyInstaller, un instalador y un repositorio en GitHub. Para confiar en los resultados realizamos diez casos de prueba, que incluyeron valores en los límites, familias incompatibles, datos inválidos y casos sin solución completa; según nuestras pruebas, todos se ejecutaron satisfactoriamente.

Un aprendizaje clave fue reconocer el alcance real de PANELMSE: organiza asignaciones según altura, familia y disponibilidad, pero no hace el diseño estructural del muro ni reemplaza las verificaciones del profesional responsable. En conclusión, el proyecto nos enseñó a convertir una necesidad de obra en un procedimiento informático (definir datos, programar, probar y presentar resultados) y a usar la inteligencia artificial como apoyo, manteniendo la responsabilidad de entender y comprobar el código.
