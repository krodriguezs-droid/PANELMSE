
# ============================================================
# PANELMSE - STAGE 07
# BLOQUE 1: IMPORTAR LA BIBLIOTECA DE INTERFAZ
# ============================================================

# Permite manejar las rutas y los nombres de los archivos.
import calendar
import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

# Permite abrir ventanas para seleccionar archivos y mostrar mensajes.
from tkinter import filedialog, messagebox, ttk

# Evita que caracteres especiales del usuario se interpreten como etiquetas.
from xml.sax.saxutils import escape

# Biblioteca para construir la interfaz gráfica.
import customtkinter as ctk

# Biblioteca para generar documentos PDF.
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

# Configuración de páginas y orientación del documento.
from reportlab.lib.pagesizes import A4, landscape

# Estilos de títulos y textos.
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

# Componentes para construir el documento y sus tablas.
from reportlab.platypus import (
    LayoutError,
    LongTable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Importamos la función principal de procesamiento.
from .main import procesar_archivos, procesar_archivos_con_geometria
from .wall_geometry import calcular_distribucion_longitud

# ============================================================
# BLOQUE 2: DEFINIR LA VENTANA PRINCIPAL
# Esta clase representa la ventana de nuestra aplicación.
# ============================================================

class PanelMSEApp(ctk.CTk):

    def __init__(self):

        # Inicializamos la ventana de CustomTkinter.
        super().__init__()

        # ====================================================
        # GUARDAR LAS RUTAS DE LOS ARCHIVOS
        # ====================================================

        self.ruta_paneles = None
        self.ruta_posiciones = None
        self.resultados_actuales = None
        # ============================================================
        # INFORMACIÓN DEL PROYECTO
        # Se completa antes de seleccionar los archivos CSV.
        # ============================================================

        self.datos_proyecto = None
        self.datos_geometria = None
        # ============================================================
        # DATOS DEL SELECTOR DE FECHA
        # ============================================================

        self.fecha_seleccionada = None
        self.calendario_ventana = None
        self.calendario_anio = None
        self.calendario_mes = None

        # Continúa aquí el resto de la configuración...

        # ----------------------------------------------------
        # CONFIGURACIÓN GENERAL DE LA VENTANA
        # ----------------------------------------------------

        self.title("PANELMSE - Asignación de paneles MSE")
        # Aplicar el icono personalizado después de iniciar la ventana.
        self.after(350, self.aplicar_icono_ventana)
        # Tamaño inicial de la ventana.
        self.geometry("1100x720")

        # Tamaño mínimo permitido.
        self.minsize(900, 600)

        # Color de fondo general.
        self.configure(fg_color="#F1F3F6")

        # Permitimos que la columna principal se expanda.
        self.grid_columnconfigure(0, weight=1)

        # Permitimos que el espacio central crezca.
        self.grid_rowconfigure(1, weight=1)


        # ====================================================
        # BLOQUE 3: CREAR EL ENCABEZADO
        # Aquí aparecerán el nombre y el propósito del programa.
        # ====================================================

        self.header = ctk.CTkFrame(
            self,
            fg_color="#192B40",
            corner_radius=0
        )

        self.header.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        self.header.grid_columnconfigure(0, weight=1)

        # Nombre principal de la aplicación.
        self.title_label = ctk.CTkLabel(
            self.header,
            text="PANELMSE",
            font=("Arial", 30, "bold"),
            text_color="#FFFFFF"
        )

        self.title_label.grid(
            row=0,
            column=0,
            padx=30,
            pady=(22, 4),
            sticky="w"
        )

        # Descripción de la aplicación.
        self.subtitle_label = ctk.CTkLabel(
            self.header,
            text="Asistente de asignación de paneles prefabricados MSE",
            font=("Arial", 14),
            text_color="#DCE4ED"
        )

        self.subtitle_label.grid(
            row=1,
            column=0,
            padx=32,
            pady=(0, 22),
            sticky="w"
        )


        # ====================================================
        # BLOQUE 4: CREAR EL ÁREA CENTRAL DE TRABAJO
        # Este espacio contendrá los controles y resultados.
        # ====================================================

        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="#F1F3F6",
            corner_radius=0
        )

        self.main_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=25,
            pady=25
        )

        self.main_frame.grid_columnconfigure(0, weight=1)
        # Permitir que el área central ocupe el espacio disponible.
        self.main_frame.grid_rowconfigure(0, weight=1)

       
        # ============================================================
        # TARJETA CENTRAL CON DESPLAZAMIENTO VERTICAL
        # Permite acceder a todos los elementos de la interfaz.
        # ============================================================

        self.work_card = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color="#DCE2EA",
            scrollbar_button_color="#AAB6C5",
            scrollbar_button_hover_color="#7D8DA2"
        )

        self.work_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=5,
            pady=5
        )
        # Permitir que los elementos internos ocupen el ancho disponible.
        self.work_card.grid_columnconfigure(0, weight=1)

        # Título del área de trabajo.
        self.work_title = ctk.CTkLabel(
            self.work_card,
            text="Área de trabajo",
            font=("Arial", 22, "bold"),
            text_color="#192B40"
        )

        self.work_title.grid(
            row=0,
            column=0,
            padx=25,
            pady=(30, 10),
            sticky="w"
        )

        # Mensaje provisional mientras construimos la interfaz.
        self.work_description = ctk.CTkLabel(
            self.work_card,
            text=(
                "Registre la información del proyecto y seleccione los archivos "
                "CSV para realizar la asignación de paneles prefabricados MSE."
            ),
            font=("Arial", 14),
            text_color="#647386",
            wraplength=800,
            justify="left"
        )

        self.work_description.grid(
            row=1,
            column=0,
            padx=25,
            pady=10,
            sticky="w"
        )
        # ============================================================
        # BLOQUE: REGISTRO DEL PROYECTO
        # El usuario identifica el proyecto antes de cargar los CSV.
        # ============================================================

        self.project_section = ctk.CTkFrame(
            self.work_card,
            fg_color="#F3F5F8",
            corner_radius=12
        )

        self.project_section.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=25,
            pady=15
        )

        self.project_section.grid_columnconfigure(1, weight=1)

        # ------------------------------------------------------------
        # TÍTULO DEL REGISTRO
        # ------------------------------------------------------------

        self.project_title = ctk.CTkLabel(
            self.project_section,
            text="IDENTIFICACIÓN DEL PROYECTO",
            font=("Arial", 17, "bold"),
            text_color="#192B40"
        )

        self.project_title.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=20,
            pady=(18, 15),
            sticky="w"
        )

        # ------------------------------------------------------------
        # NOMBRE DEL RESPONSABLE
        # ------------------------------------------------------------

        self.responsable_label = ctk.CTkLabel(
            self.project_section,
            text="Nombre del responsable:",
            font=("Arial", 13, "bold"),
            text_color="#192B40"
        )

        self.responsable_label.grid(
            row=1,
            column=0,
            padx=20,
            pady=10,
            sticky="w"
        )

        self.responsable_entry = ctk.CTkEntry(
            self.project_section,
            height=35,
            validate="key",
            validatecommand=(
                self.register(self.validar_nombre),
                "%P"
            )
        )

        self.responsable_entry.grid(
            row=1,
            column=1,
            padx=20,
            pady=10,
            sticky="ew"
        )

        # ------------------------------------------------------------
        # NOMBRE DEL PROYECTO
        # ------------------------------------------------------------

        self.nombre_proyecto_label = ctk.CTkLabel(
            self.project_section,
            text="Nombre del proyecto:",
            font=("Arial", 13, "bold"),
            text_color="#192B40"
        )

        self.nombre_proyecto_label.grid(
            row=2,
            column=0,
            padx=20,
            pady=10,
            sticky="w"
        )

        self.nombre_proyecto_entry = ctk.CTkEntry(
            self.project_section,
            placeholder_text="Escribe el nombre del proyecto",
            height=35
        )

        self.nombre_proyecto_entry.grid(
            row=2,
            column=1,
            padx=20,
            pady=10,
            sticky="ew"
        )

        # ------------------------------------------------------------
        # FECHA DEL PROYECTO
        # ------------------------------------------------------------

        self.fecha_proyecto_label = ctk.CTkLabel(
            self.project_section,
            text="Fecha del proyecto:",
            font=("Arial", 13, "bold"),
            text_color="#192B40"
        )

        self.fecha_proyecto_label.grid(
            row=3,
            column=0,
            padx=20,
            pady=10,
            sticky="w"
        )

        # ------------------------------------------------------------
        # SELECTOR DE FECHA DEL PROYECTO
        # ------------------------------------------------------------

        self.fecha_frame = ctk.CTkFrame(
        self.project_section,
        fg_color="transparent"
        )
 
        self.fecha_frame.grid(
        row=3,
        column=1,
        padx=20,
        pady=10,
        sticky="w"
        )

        # Campo donde se mostrará la fecha seleccionada.
        self.fecha_entry = ctk.CTkEntry(
        self.fecha_frame,
        width=150,
        height=35,
        placeholder_text="Selecciona una fecha"
        )

        self.fecha_entry.grid(
        row=0,
        column=0,
        padx=(0, 8)
        )

        self.fecha_entry.configure(state="disabled")

        # Botón para abrir el calendario.
        self.fecha_calendario_button = ctk.CTkButton(
        self.fecha_frame,
        text="Seleccionar fecha",
        width=145,
        height=35,
        fg_color="#192B40",
        hover_color="#263E59",
        text_color="#FFFFFF",
        command=self.abrir_calendario
        )

        self.fecha_calendario_button.grid(
        row=0,
        column=1
        )

        # ============================================================
        # BLOQUE: DIMENSIONES Y CONFIGURACION DEL MURO
        # ============================================================

        self.geometry_frame = ctk.CTkFrame(
            self.project_section,
            fg_color="#E9EEF3",
            corner_radius=10
        )

        self.geometry_frame.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=20,
            pady=(12, 8),
            sticky="ew"
        )

        # Configurar las columnas internas.
        for columna in range(4):
            self.geometry_frame.grid_columnconfigure(
                columna,
                weight=1 if columna in (1, 3) else 0
            )

        # ------------------------------------------------------------
        # TITULO
        # ------------------------------------------------------------

        self.geometry_title = ctk.CTkLabel(
            self.geometry_frame,
            text="DIMENSIONES Y PERFIL DEL MURO",
            font=("Arial", 15, "bold"),
            text_color="#192B40"
        )

        self.geometry_title.grid(
            row=0,
            column=0,
            columnspan=4,
            padx=15,
            pady=(12, 10),
            sticky="w"
        )

        # ------------------------------------------------------------
        # LONGITUD TOTAL DEL MURO
        # ------------------------------------------------------------

        ctk.CTkLabel(
            self.geometry_frame,
            text="Longitud total del muro (m):",
            font=("Arial", 12, "bold"),
            text_color="#192B40"
        ).grid(
            row=1,
            column=0,
            padx=12,
            pady=8,
            sticky="w"
        )

        self.longitud_muro_entry = ctk.CTkEntry(
            self.geometry_frame,
            height=34,
            width=140,
            placeholder_text="Ej. 12.60"
        )

        self.longitud_muro_entry.grid(
            row=1,
            column=1,
            padx=10,
            pady=8,
            sticky="ew"
        )

        # ------------------------------------------------------------
        # LONGITUD DEL PANEL
        # ------------------------------------------------------------

        ctk.CTkLabel(
            self.geometry_frame,
            text="Longitud de cada panel (m):",
            font=("Arial", 12, "bold"),
            text_color="#192B40"
        ).grid(
            row=1,
            column=2,
            padx=12,
            pady=8,
            sticky="w"
        )

        self.longitud_panel_entry = ctk.CTkEntry(
            self.geometry_frame,
            height=34,
            width=140,
            placeholder_text="Ej. 1.25"
        )

        self.longitud_panel_entry.grid(
            row=1,
            column=3,
            padx=10,
            pady=8,
            sticky="ew"
        )

        # ------------------------------------------------------------
        # ALTURA INICIAL
        # ------------------------------------------------------------

        ctk.CTkLabel(
            self.geometry_frame,
            text="Altura inicial (m):",
            font=("Arial", 12, "bold"),
            text_color="#192B40"
        ).grid(
            row=2,
            column=0,
            padx=12,
            pady=8,
            sticky="w"
        )

        self.altura_inicial_entry = ctk.CTkEntry(
            self.geometry_frame,
            height=34,
            placeholder_text="Ej. 1.25"
        )

        self.altura_inicial_entry.grid(
            row=2,
            column=1,
            padx=10,
            pady=8,
            sticky="ew"
        )

        # ------------------------------------------------------------
        # ALTURA FINAL
        # ------------------------------------------------------------

        ctk.CTkLabel(
            self.geometry_frame,
            text="Altura final (m):",
            font=("Arial", 12, "bold"),
            text_color="#192B40"
        ).grid(
            row=2,
            column=2,
            padx=12,
            pady=8,
            sticky="w"
        )

        self.altura_final_entry = ctk.CTkEntry(
            self.geometry_frame,
            height=34,
            placeholder_text="Ej. 1.35"
        )

        self.altura_final_entry.grid(
            row=2,
            column=3,
            padx=10,
            pady=8,
            sticky="ew"
        )

        # ------------------------------------------------------------
        # PASO DE ALTURA
        # ------------------------------------------------------------

        ctk.CTkLabel(
            self.geometry_frame,
            text="Paso de altura (m):",
            font=("Arial", 12, "bold"),
            text_color="#192B40"
        ).grid(
            row=3,
            column=0,
            padx=12,
            pady=8,
            sticky="w"
        )

        self.paso_altura_entry = ctk.CTkEntry(
            self.geometry_frame,
            height=34
        )

        self.paso_altura_entry.grid(
            row=3,
            column=1,
            padx=10,
            pady=8,
            sticky="ew"
        )

        self.paso_altura_entry.insert(0, "0.05")

        # ------------------------------------------------------------
        # MODO DE PROGRESION
        # ------------------------------------------------------------

        ctk.CTkLabel(
            self.geometry_frame,
            text="Modo de progresión:",
            font=("Arial", 12, "bold"),
            text_color="#192B40"
        ).grid(
            row=3,
            column=2,
            padx=12,
            pady=8,
            sticky="w"
        )

        self.modo_altura_segmented = ctk.CTkSegmentedButton(
            self.geometry_frame,
            values=["Estricto", "Flexible"],
            selected_color="#192B40",
            selected_hover_color="#263E59"
        )

        self.modo_altura_segmented.grid(
            row=3,
            column=3,
            padx=10,
            pady=8,
            sticky="ew"
        )

        self.modo_altura_segmented.set("Estricto")

        # Texto explicativo.
        self.geometry_description = ctk.CTkLabel(
            self.geometry_frame,
            text=(
                "Estricto: salto máximo de un paso. "
                "Flexible: salto máximo de dos pasos."
            ),
            font=("Arial", 11),
            text_color="#647386"
        )

        self.geometry_description.grid(
            row=4,
            column=0,
            columnspan=4,
            padx=12,
            pady=(5, 12),
            sticky="w"
        )
        # ------------------------------------------------------------
        # RESUMEN DE PANELES NECESARIOS
        # ------------------------------------------------------------

        self.paneles_necesarios_label = ctk.CTkLabel(
        self.geometry_frame,
        text="Paneles necesarios: pendiente de cálculo",
        font=("Arial", 13, "bold"),
        text_color="#192B40"
        )
 
        self.paneles_necesarios_label.grid(
        row=5,
        column=0,
        columnspan=4,
        padx=12,
        pady=(5, 14),
        sticky="w"
        )
        # ------------------------------------------------------------
        # BOTÓN PARA CONFIRMAR EL REGISTRO
        # ------------------------------------------------------------

        self.project_button = ctk.CTkButton(
            self.project_section,
            text="Confirmar datos del proyecto",
            width=240,
            height=38,
            fg_color="#192B40",
            hover_color="#263E59",
            text_color="#FFFFFF",
            font=("Arial", 13, "bold"),
            command=self.registrar_proyecto
        )

        self.project_button.grid(
            row=5,
            column=0,
            padx=20,
            pady=(12, 18),
            sticky="w"
        )

        # ------------------------------------------------------------
        # ESTADO DEL REGISTRO
        # ------------------------------------------------------------

        self.project_status_label = ctk.CTkLabel(
            self.project_section,
            text="Estado: Registro pendiente",
            font=("Arial", 12),
            text_color="#647386",
            wraplength=350,
            justify="left"
        )

        self.project_status_label.grid(
            row=5,
            column=1,
            padx=20,
            pady=(12, 18),
            sticky="w"
        )
        # ============================================================
        # BLOQUE: PANEL DE ARCHIVOS DE ENTRADA
        # Aquí el usuario seleccionará los dos archivos CSV.
        # ============================================================

        self.file_section = ctk.CTkFrame(
            self.work_card,
            fg_color="#F3F5F8",
            corner_radius=12
        )

        self.file_section.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=25,
            pady=20
        )

        # Permitimos que la columna de los nombres se expanda.
        self.file_section.grid_columnconfigure(1, weight=1)


        # ------------------------------------------------------------
        # TÍTULO DEL PANEL
        # ------------------------------------------------------------

        self.file_title = ctk.CTkLabel(
            self.file_section,
            text="ARCHIVOS DE ENTRADA",
            font=("Arial", 17, "bold"),
            text_color="#192B40"
        )

        self.file_title.grid(
            row=0,
           column=0,
           columnspan=3,
           padx=20,
           pady=(20, 15),
           sticky="w"
        )


        # ------------------------------------------------------------
        # FILA 1: ARCHIVO DE PANELES
        # ------------------------------------------------------------

        self.paneles_label = ctk.CTkLabel(
            self.file_section,
            text="Archivo de paneles:",
            font=("Arial", 14, "bold"),
            text_color="#192B40"
        )

        self.paneles_label.grid(
            row=1,
            column=0,
            padx=20,
            pady=12,
            sticky="w"
        )

        self.paneles_button = ctk.CTkButton(
            self.file_section,
            text="Seleccionar CSV",
            width=150,
            fg_color="#D6A23A",
            hover_color="#B8862B",
            text_color="#192B40",
            state="disabled",
            command=self.seleccionar_paneles
        )

        self.paneles_button.grid(
            row=1,
            column=1,
            padx=15,
            pady=12,
            sticky="w"
        )

        self.paneles_file_label = ctk.CTkLabel(
            self.file_section,
            text="No seleccionado",
            font=("Arial", 12),
            text_color="#647386"
        )

        self.paneles_file_label.grid(
            row=1,
            column=2,
            padx=15,
            pady=12,
            sticky="w"
        )


        # ------------------------------------------------------------
        # FILA 2: ARCHIVO DE POSICIONES
        # ------------------------------------------------------------

        self.posiciones_label = ctk.CTkLabel(
            self.file_section,
            text="Archivo de posiciones:",
            font=("Arial", 14, "bold"),
            text_color="#192B40"
        )

        self.posiciones_label.grid(
            row=2,
            column=0,
            padx=20,
            pady=(10, 20),
            sticky="w"
        )

        self.posiciones_button = ctk.CTkButton(
            self.file_section,
            text="Seleccionar CSV",
            width=150,
            fg_color="#D6A23A",
            hover_color="#B8862B",
            text_color="#192B40",
            state="disabled",
            command=self.seleccionar_posiciones
        )

        self.posiciones_button.grid(
            row=2,
            column=1,
            padx=15,
            pady=(10, 20),
            sticky="w"
        )

        self.posiciones_file_label = ctk.CTkLabel(
            self.file_section,
            text="No seleccionado",
            font=("Arial", 12),
            text_color="#647386"
        )

        self.posiciones_file_label.grid(
            row=2,
            column=2,
            padx=15,
            pady=(10, 20),
            sticky="w"
        )
        # ============================================================
        # BLOQUE: BOTÓN PARA CALCULAR LA ASIGNACIÓN
        # Ejecuta el procesamiento de los archivos seleccionados.
        # ============================================================

        self.calculate_button = ctk.CTkButton(
            self.work_card,
            text="Calcular asignación",
            width=220,
            height=40,
            fg_color="#192B40",
            hover_color="#263E59",
            text_color="#FFFFFF",
            font=("Arial", 14, "bold"),
            state="disabled",
            command=self.calcular_asignacion
        )

        self.calculate_button.grid(
            row=4,
            column=0,
            padx=25,
            pady=(5, 25),
            sticky="w"
        )
        # ============================================================
        # BLOQUE: RESUMEN DE RESULTADOS
        # Muestra las cantidades generales del procesamiento.
        # ============================================================

        self.summary_frame = ctk.CTkFrame(
            self.work_card,
            fg_color="#F3F5F8",
            corner_radius=10
        )

        self.summary_frame.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=25,
            pady=10
        )

        # Configurar cuatro columnas para el resumen.
                # Configurar las cuatro columnas del resumen.
        for columna in range(4):
            self.summary_frame.grid_columnconfigure(
                columna,
                weight=1
            )

        # Etiqueta del total de posiciones.
        self.total_posiciones_label = ctk.CTkLabel(
            self.summary_frame,
            text="Posiciones: 0",
            font=("Arial", 13, "bold"),
            text_color="#192B40"
        )

        self.total_posiciones_label.grid(
            row=0,
            column=0,
            padx=10,
            pady=15
        )

        self.total_posiciones_label.grid(
        row=0, column=0, padx=10, pady=15
        )

        self.total_asignadas_label = ctk.CTkLabel(
            self.summary_frame,
            text="Asignadas: 0",
            font=("Arial", 13, "bold"),
            text_color="#16845B"
        )

        self.total_asignadas_label.grid(
            row=0, column=1, padx=10, pady=15
        )

        self.total_pendientes_label = ctk.CTkLabel(
            self.summary_frame,
            text="Pendientes: 0",
            font=("Arial", 13, "bold"),
            text_color="#B45B42"
        )

        self.total_pendientes_label.grid(
            row=0, column=2, padx=10, pady=15
        )

        self.total_sobrantes_label = ctk.CTkLabel(
            self.summary_frame,
            text="Paneles sobrantes: 0",
            font=("Arial", 13, "bold"),
            text_color="#435164"
        )

        self.total_sobrantes_label.grid(
           row=0, column=3, padx=10, pady=15
        )


        # ============================================================
        # BLOQUE: PESTAÑAS DE RESULTADOS
        # Separa las asignaciones, pendientes y paneles sobrantes.
        # ============================================================

        self.results_tabs = ctk.CTkTabview(
            self.work_card,
            width=950,
            height=230
        )

        self.results_tabs.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=25,
            pady=10
        ) 

        # Crear las tres pestañas.
        self.tab_asignaciones = self.results_tabs.add("Asignaciones")

        self.tab_pendientes = self.results_tabs.add("Posiciones pendientes")

        self.tab_sobrantes = self.results_tabs.add("Paneles sobrantes")

        # Nueva pestaña para el diagnóstico del inventario.
        self.tab_diagnostico = self.results_tabs.add(
        "Diagnóstico del inventario"
        )


        # ============================================================
        # CREAR LAS TABLAS
        # ============================================================

        self.tabla_asignaciones = self._crear_tabla(
        self.tab_asignaciones,
    [
        ("id_posicion", "Posición", 100),
        ("ubicacion", "Ubicación", 140),
        ("id_panel", "Panel", 100),
        ("altura_panel_mm", "Altura panel (mm)", 130),
        ("cota_apoyo_mm", "Cota apoyo (mm)", 130),
        ("cota_superior_mm", "Cota superior (mm)", 140)
    ]
)

        self.tabla_pendientes = self._crear_tabla(
        self.tab_pendientes,
    [
        ("id_posicion", "Posición", 100),
        ("ubicacion", "Ubicación", 140),
        ("cota_apoyo_mm", "Cota apoyo (mm)", 130),
        ("altura_min_mm", "Altura mínima (mm)", 130),
        ("altura_max_mm", "Altura máxima (mm)", 130),
        ("familia_admitida", "Familia", 110)
    ]
)

        self.tabla_sobrantes = self._crear_tabla(
        self.tab_sobrantes,
    [
        ("id_panel", "Panel", 130),
        ("altura_mm", "Altura (mm)", 150),
        ("familia", "Familia", 130)
    ]
)
        # ============================================================
        # BLOQUE: DIAGNÓSTICO DEL INVENTARIO
        # ============================================================

        self.diagnostico_resumen_label = ctk.CTkLabel(
        self.tab_diagnostico,
        text="El diagnóstico aparecerá después de calcular.",
        font=("Arial", 12, "bold"),
        text_color="#192B40",
        justify="left",
        anchor="w",
        wraplength=850
        )

        self.diagnostico_resumen_label.pack(
        fill="x",
        padx=10,
        pady=(10, 5)
        ) 

        # Tabla que muestra los candidatos y los motivos de rechazo.
        self.tabla_diagnostico = self._crear_tabla(
        self.tab_diagnostico,
    [
        ("orden", "Orden", 65),
        ("id_posicion", "Posición", 85),
        ("cantidad_candidatos", "Candidatos", 90),
        ("paneles_candidatos", "Paneles compatibles", 190),
        ("motivos_rechazo", "Motivos de rechazo", 390)
    ]
        )
        # ============================================================
        # BLOQUE: BOTONES DE EXPORTACIÓN
        # Permite exportar los resultados en CSV o PDF.
        # ============================================================

        self.export_actions_frame = ctk.CTkFrame(
            self.work_card,
            fg_color="transparent"
        )

        self.export_actions_frame.grid(
            row=7,
            column=0,
            padx=25,
            pady=(5, 20),
            sticky="w"
        )

        # ------------------------------------------------------------
        # BOTÓN PARA EXPORTAR CSV
        # ------------------------------------------------------------

        self.export_button = ctk.CTkButton(
            self.export_actions_frame,
            text="Exportar resultados (CSV)",
            width=220,
            height=40,
            fg_color="#16845B",
            hover_color="#116C49",
            text_color="#FFFFFF",
            font=("Arial", 13, "bold"),
            command=self.exportar_resultados,
            state="disabled"
        )

        self.export_button.pack(
            side="left",
            padx=(0, 12)
        )

        # ------------------------------------------------------------
        # BOTÓN PARA EXPORTAR PDF
        # ------------------------------------------------------------

        self.pdf_button = ctk.CTkButton(
            self.export_actions_frame,
            text="Exportar PDF",
            width=180,
            height=40,
            fg_color="#B45B42",
            hover_color="#914832",
            text_color="#FFFFFF",
            font=("Arial", 13, "bold"),
            command=self.exportar_pdf,
            state="disabled"
        )

        self.pdf_button.pack(
            side="left"
        )
        # ====================================================
        # BLOQUE 5: CREAR LA BARRA DE ESTADO
        # Nos permitirá informar qué está haciendo el programa.
        # ====================================================

        self.status_bar = ctk.CTkFrame(
            self,
            fg_color="#E2E7ED",
            corner_radius=0,
            height=35
        )

        self.status_bar.grid(
            row=2,
            column=0,
            sticky="ew"
        )

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Estado: Interfaz inicial",
            font=("Arial", 12),
            text_color="#435164"
        )

        self.status_label.pack(
            side="left",
            padx=20,
            pady=8
        )
    # ============================================================
    # MÉTODO: APLICAR ICONO DE LA VENTANA
    # Establece el icono personalizado de PANELMSE.
    # ============================================================

    def aplicar_icono_ventana(self):

        # Ubicación del icono dentro del proyecto.
        ruta_icono = (
            Path(__file__).resolve().parent
            / "assets"
            / "PANELMSE.ico"
        )

        # Comprobar que el archivo exista.
        if not ruta_icono.is_file():

            print(
                f"No se encontró el icono de PANELMSE: {ruta_icono}"
            )

            return

        try:

            # Aplicar el icono a la ventana.
            self.iconbitmap(str(ruta_icono))

        except OSError as error:

            print(
                f"No se pudo aplicar el icono: {error}"
            )
    # ============================================================
    # VALIDAR NOMBRE DEL RESPONSABLE
    # Acepta letras y espacios.
    # ============================================================

    def validar_nombre(self, nuevo_valor):

        return all(
            caracter.isalpha() or caracter == " "
            for caracter in nuevo_valor
        )


    # ============================================================
    # VALIDAR AÑO
    # Acepta únicamente números, máximo cuatro.
    # ============================================================

    def validar_anio(self, nuevo_valor):

        return (
            len(nuevo_valor) <= 4
            and all(
                caracter in "0123456789"
                for caracter in nuevo_valor
            )
        )


    # ============================================================
    # VALIDAR MES Y DÍA
    # Acepta únicamente números, máximo dos.
    # ============================================================

    def validar_dos_digitos(self, nuevo_valor):

        return (
            len(nuevo_valor) <= 2
            and all(
                caracter in "0123456789"
                for caracter in nuevo_valor
            )
        )
    # ============================================================
    # ABRIR EL CALENDARIO
    # ============================================================

    def abrir_calendario(self):

        # Evitar abrir varias ventanas de calendario.
        if (
            self.calendario_ventana is not None
            and self.calendario_ventana.winfo_exists()
        ):
            self.calendario_ventana.lift()
            return

        # Utilizar la fecha seleccionada o la fecha actual.
        fecha_base = self.fecha_seleccionada or date.today()

        self.calendario_anio = fecha_base.year
        self.calendario_mes = fecha_base.month

        # Crear la ventana del calendario.
        self.calendario_ventana = ctk.CTkToplevel(self)

        self.calendario_ventana.title("Seleccionar fecha")
        self.calendario_ventana.geometry("340x390")
        self.calendario_ventana.resizable(False, False)
        self.calendario_ventana.transient(self)

        self.calendario_ventana.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar_calendario
        )

        # Contenedor principal.
        contenedor = ctk.CTkFrame(
            self.calendario_ventana,
            fg_color="transparent"
        )

        contenedor.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        # --------------------------------------------------------
        # ENCABEZADO Y NAVEGACIÓN ENTRE MESES
        # --------------------------------------------------------

        navegacion = ctk.CTkFrame(
            contenedor,
            fg_color="transparent"
        )

        navegacion.pack(fill="x", pady=(0, 15))

        navegacion.grid_columnconfigure(1, weight=1)

        self.calendario_anterior_button = ctk.CTkButton(
            navegacion,
            text="<",
            width=40,
            command=lambda: self.cambiar_mes_calendario(-1)
        )

        self.calendario_anterior_button.grid(
            row=0,
            column=0,
            padx=5
        )

        self.calendario_titulo = ctk.CTkLabel(
            navegacion,
            text="",
            font=("Arial", 17, "bold"),
            text_color="#192B40"
        )

        self.calendario_titulo.grid(
            row=0,
            column=1
        )

        self.calendario_siguiente_button = ctk.CTkButton(
            navegacion,
            text=">",
            width=40,
            command=lambda: self.cambiar_mes_calendario(1)
        )

        self.calendario_siguiente_button.grid(
            row=0,
            column=2,
            padx=5
        )

        # --------------------------------------------------------
        # ENCABEZADOS DE LOS DÍAS DE LA SEMANA
        # --------------------------------------------------------

        encabezados = ctk.CTkFrame(
            contenedor,
            fg_color="transparent"
        )

        encabezados.pack(fill="x")

        dias_semana = [
            "Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"
        ]

        for columna, nombre in enumerate(dias_semana):

            encabezados.grid_columnconfigure(
                columna,
                weight=1
            )

            ctk.CTkLabel(
                encabezados,
                text=nombre,
                font=("Arial", 12, "bold"),
                text_color="#647386"
            ).grid(
                row=0,
                column=columna,
                padx=2,
                pady=5
            )

        # --------------------------------------------------------
        # CONTENEDOR DE LOS DÍAS DEL MES
        # --------------------------------------------------------

        self.calendario_dias_frame = ctk.CTkFrame(
            contenedor,
            fg_color="transparent"
        )

        self.calendario_dias_frame.pack(
            fill="both",
            expand=True
        )

        for columna in range(7):

            self.calendario_dias_frame.grid_columnconfigure(
                columna,
                weight=1
            )

        # Mostrar el mes correspondiente.
        self.actualizar_calendario()

        # Mantener el calendario delante de la ventana principal.
        self.calendario_ventana.grab_set()


    # ============================================================
    # ACTUALIZAR LOS DÍAS DEL CALENDARIO
    # ============================================================

    def actualizar_calendario(self):

        nombres_meses = [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        # Actualizar el título del calendario.
        self.calendario_titulo.configure(
            text=(
                f"{nombres_meses[self.calendario_mes - 1]} "
                f"{self.calendario_anio}"
            )
        )

        # Eliminar los días del mes anterior.
        for elemento in self.calendario_dias_frame.winfo_children():
            elemento.destroy()

        # Obtener las semanas del mes.
        semanas = calendar.monthcalendar(
            self.calendario_anio,
            self.calendario_mes
        )

        # Crear un botón para cada día.
        for fila, semana in enumerate(semanas):

            for columna, dia in enumerate(semana):

                if dia == 0:
                    continue

                color_fondo = "#FFFFFF"
                color_texto = "#192B40"

                # Resaltar la fecha que ya está seleccionada.
                if (
                    self.fecha_seleccionada is not None
                    and self.fecha_seleccionada.year == self.calendario_anio
                    and self.fecha_seleccionada.month == self.calendario_mes
                    and self.fecha_seleccionada.day == dia
                ):

                    color_fondo = "#2D6A8A"
                    color_texto = "#FFFFFF"

                boton_dia = ctk.CTkButton(
                    self.calendario_dias_frame,
                    text=str(dia),
                    width=35,
                    height=34,
                    fg_color=color_fondo,
                    hover_color="#DCE5EF",
                    text_color=color_texto,
                    font=("Arial", 12),
                    command=lambda numero=dia: self.seleccionar_fecha(numero)
                )

                boton_dia.grid(
                    row=fila,
                    column=columna,
                    padx=2,
                    pady=3,
                    sticky="nsew"
                )


    # ============================================================
    # CAMBIAR DE MES
    # ============================================================

    def cambiar_mes_calendario(self, desplazamiento):

        nuevo_mes = self.calendario_mes + desplazamiento
        nuevo_anio = self.calendario_anio

        if nuevo_mes < 1:

            nuevo_mes = 12
            nuevo_anio -= 1

        elif nuevo_mes > 12:

            nuevo_mes = 1
            nuevo_anio += 1

        # Evitar años fuera del rango admitido por datetime.
        if nuevo_anio < 1 or nuevo_anio > 9999:
            return

        self.calendario_mes = nuevo_mes
        self.calendario_anio = nuevo_anio

        self.actualizar_calendario()


    # ============================================================
    # GUARDAR LA FECHA SELECCIONADA
    # ============================================================

    def seleccionar_fecha(self, dia):

        self.fecha_seleccionada = date(
            self.calendario_anio,
            self.calendario_mes,
            dia
        )

        # Mostrar la fecha en el campo de la interfaz.
        self.fecha_entry.configure(state="normal")

        self.fecha_entry.delete(0, "end")

        self.fecha_entry.insert(
            0,
            self.fecha_seleccionada.strftime("%d/%m/%Y")
        )

        self.fecha_entry.configure(state="disabled")

        # Cerrar el calendario después de seleccionar.
        self.cerrar_calendario()


    # ============================================================
    # CERRAR EL CALENDARIO
    # ============================================================

    def cerrar_calendario(self):

        if self.calendario_ventana is not None:

            ventana = self.calendario_ventana

            self.calendario_ventana = None

            ventana.grab_release()

            ventana.destroy()
# ============================================================
# BLOQUE: SELECCIONAR EL ARCHIVO DE PANELES
# Abre el explorador y guarda la ruta del CSV seleccionado.
# ============================================================
  
    # ============================================================
    # MÉTODO: REGISTRAR PROYECTO
    # Valida y guarda la identificación del proyecto.
    # ============================================================


    # ============================================================
    # REGISTRAR PROYECTO Y VALIDAR GEOMETRIA
    # ============================================================

    def registrar_proyecto(self):

        # --------------------------------------------------------
        # 1. OBTENER DATOS GENERALES
        # --------------------------------------------------------

        responsable = self.responsable_entry.get().strip()
        nombre_proyecto = self.nombre_proyecto_entry.get().strip()
        fecha = self.fecha_seleccionada

        # Obtener las medidas introducidas.
        longitud_muro_texto = self.longitud_muro_entry.get().strip()
        longitud_panel_texto = self.longitud_panel_entry.get().strip()
        altura_inicial_texto = self.altura_inicial_entry.get().strip()
        altura_final_texto = self.altura_final_entry.get().strip()
        paso_altura_texto = self.paso_altura_entry.get().strip()

        modo = self.modo_altura_segmented.get()

        # --------------------------------------------------------
        # 2. COMPROBAR CAMPOS VACIOS
        # --------------------------------------------------------

        if (
            not responsable
            or not nombre_proyecto
            or fecha is None
            or not longitud_muro_texto
            or not longitud_panel_texto
            or not altura_inicial_texto
            or not altura_final_texto
            or not paso_altura_texto
        ):

            messagebox.showwarning(
                "Datos incompletos",
                "Debes completar todos los datos del proyecto "
                "y las dimensiones del muro, y seleccionar una fecha.",
                parent=self
            )
            return

        # --------------------------------------------------------
        # 3. CONVERTIR Y VALIDAR LAS MEDIDAS
        # --------------------------------------------------------

        def leer_medida_positiva(texto, nombre):

            try:
                valor = Decimal(
                    texto.replace(",", ".")
                )

            except InvalidOperation:

                raise ValueError(
                    f"La {nombre} debe ser un número válido."
                )

            if not valor.is_finite() or valor <= 0:

                raise ValueError(
                    f"La {nombre} debe ser mayor que cero."
                )

            return valor

        try:

            longitud_muro = leer_medida_positiva(
                longitud_muro_texto,
                "longitud del muro"
            )

            longitud_panel = leer_medida_positiva(
                longitud_panel_texto,
                "longitud del panel"
            )

            altura_inicial = leer_medida_positiva(
                altura_inicial_texto,
                "altura inicial"
            )

            altura_final = leer_medida_positiva(
                altura_final_texto,
                "altura final"
            )

            paso_altura = leer_medida_positiva(
                paso_altura_texto,
                "paso de altura"
            )

        except ValueError as error:

            messagebox.showwarning(
                "Medida incorrecta",
                str(error),
                parent=self
            )
            return

        # --------------------------------------------------------
        # 4. VALIDAR RELACION ENTRE LONGITUDES
        # --------------------------------------------------------

        if longitud_panel >= longitud_muro:

            messagebox.showwarning(
                "Longitud incorrecta",
                "La longitud de cada panel debe ser menor "
                "que la longitud total del muro.",
                parent=self
            )
            return

        # --------------------------------------------------------
        # 5. VALIDAR EL MODO DE PROGRESION
        # --------------------------------------------------------

        if modo not in ("Estricto", "Flexible"):

            messagebox.showwarning(
                "Modo incorrecto",
                "Selecciona el modo estricto o flexible.",
                parent=self
            )
            return

        # --------------------------------------------------------
        # 6. GUARDAR INFORMACION GENERAL
        # --------------------------------------------------------

        self.datos_proyecto = {
            "responsable": responsable,
            "nombre_proyecto": nombre_proyecto,
            "fecha": fecha.strftime("%Y-%m-%d")
        }

        # --------------------------------------------------------
        # 7. GUARDAR GEOMETRIA Y CONFIGURACION
        # --------------------------------------------------------

        self.datos_geometria = {
            "longitud_muro_m": str(longitud_muro),
            "longitud_panel_m": str(longitud_panel),
            "altura_inicial_m": str(altura_inicial),
            "altura_final_m": str(altura_final),
            "paso_altura_m": str(paso_altura),
            "modo_flexible": modo == "Flexible"
        }
        # --------------------------------------------------------
        # CALCULAR CANTIDAD DE PANELES NECESARIOS
        # --------------------------------------------------------

        distribucion = calcular_distribucion_longitud(
        longitud_muro,
        longitud_panel
        )
 
        cantidad_necesaria = (
        distribucion["cantidad_paneles_necesarios"]
        )

        longitud_cubierta = (
        distribucion["longitud_cubierta_m"]
        )

        espacio_sobrante = (
        distribucion["espacio_sobrante_m"]
        )

        # Mostrar los resultados en la interfaz.
        self.paneles_necesarios_label.configure(
        text=(
        f"Paneles necesarios: {cantidad_necesaria}    |    "
        f"Longitud cubierta: {longitud_cubierta} m    |    "
        f"Espacio sobrante: {espacio_sobrante} m"
        ),
        text_color="#16845B"
        )
        # --------------------------------------------------------
        # 8. BLOQUEAR LOS CAMPOS DEL PROYECTO
        # --------------------------------------------------------

        self.responsable_entry.configure(state="disabled")
        self.nombre_proyecto_entry.configure(state="disabled")
        self.fecha_calendario_button.configure(state="disabled")

        self.longitud_muro_entry.configure(state="disabled")
        self.longitud_panel_entry.configure(state="disabled")
        self.altura_inicial_entry.configure(state="disabled")
        self.altura_final_entry.configure(state="disabled")
        self.paso_altura_entry.configure(state="disabled")

        self.modo_altura_segmented.configure(state="disabled")

        # --------------------------------------------------------
        # 9. HABILITAR SELECCION DE ARCHIVOS
        # --------------------------------------------------------

        self.paneles_button.configure(state="normal")
        self.posiciones_button.configure(state="normal")

        self.project_button.configure(
            text="Modificar datos del proyecto",
            command=self.habilitar_edicion_proyecto
        )

        # --------------------------------------------------------
        # 10. ACTUALIZAR ESTADO
        # --------------------------------------------------------

        self.project_status_label.configure(
            text="Estado: Proyecto registrado correctamente.",
            text_color="#16845B"
        )

        self.actualizar_estado_archivos()

        messagebox.showinfo(
            "Registro completado",
            "Los datos del proyecto y las dimensiones del muro "
            "se registraron correctamente.\n\n"
            "Ya puedes seleccionar los archivos CSV.",
            parent=self
        )



    # ============================================================
    # HABILITAR EDICION DEL PROYECTO
    # ============================================================

    def habilitar_edicion_proyecto(self):

        confirmar = messagebox.askyesno(
            "Modificar proyecto",
            "¿Deseas modificar los datos del proyecto?\n\n"
            "Se eliminarán los resultados calculados anteriormente.",
            parent=self
        )

        if not confirmar:
            return

        # Eliminar resultados anteriores.
        self.resultados_actuales = None

        self.datos_proyecto = None
        self.datos_geometria = None

        self.actualizar_vista_resultados()

        # --------------------------------------------------------
        # HABILITAR DATOS GENERALES
        # --------------------------------------------------------

        self.responsable_entry.configure(state="normal")
        self.nombre_proyecto_entry.configure(state="normal")
        self.fecha_calendario_button.configure(state="normal")

        # --------------------------------------------------------
        # HABILITAR DIMENSIONES DEL MURO
        # --------------------------------------------------------

        self.longitud_muro_entry.configure(state="normal")
        self.longitud_panel_entry.configure(state="normal")
        self.altura_inicial_entry.configure(state="normal")
        self.altura_final_entry.configure(state="normal")
        self.paso_altura_entry.configure(state="normal")

        self.modo_altura_segmented.configure(state="normal")

        # --------------------------------------------------------
        # DESHABILITAR ARCHIVOS HASTA CONFIRMAR
        # --------------------------------------------------------

        self.paneles_button.configure(state="disabled")
        self.posiciones_button.configure(state="disabled")
        self.calculate_button.configure(state="disabled")

        # --------------------------------------------------------
        # RESTAURAR BOTON DE CONFIRMACION
        # --------------------------------------------------------

        self.project_button.configure(
            text="Confirmar datos del proyecto",
            command=self.registrar_proyecto
        )

        self.project_status_label.configure(
            text="Estado: Modifica los datos y confirma nuevamente.",
            text_color="#B8862B"
        )

        self.status_label.configure(
            text="Estado: Esperando confirmación del registro."
        )

    def seleccionar_paneles(self):

        ruta = filedialog.askopenfilename(
        title="Seleccionar archivo de paneles",
        filetypes=[("Archivos CSV", "*.csv")]
    )

    # Si el usuario cierra la ventana, no cambia nada.
        if not ruta:
           return

    # Guardamos la ubicación del archivo seleccionado.
        self.ruta_paneles = Path(ruta)

    # Mostramos el nombre del archivo en la interfaz.
        self.paneles_file_label.configure(
        text=self.ruta_paneles.name,
        text_color="#16845B"
    )
    # Invalidar resultados anteriores porque cambió el archivo.
        self.resultados_actuales = None

    # Limpiar las tablas y deshabilitar la exportación.
        self.actualizar_vista_resultados()


    # Actualizamos el estado de la aplicación.
        self.actualizar_estado_archivos()

# ============================================================
# MÉTODO: CREAR TABLAS
# Construye una tabla con sus encabezados y barra de desplazamiento.
# ============================================================

    def _crear_tabla(self, contenedor, columnas):

    # Crear el espacio donde estará la tabla.
     marco = ctk.CTkFrame(
        contenedor,
        fg_color="transparent"
    )

     marco.pack(
        fill="both",
        expand=True,
        padx=8,
        pady=8
    )

    # Obtener los identificadores de las columnas.
     identificadores = [
        columna[0] for columna in columnas
    ]

    # Crear la tabla.
     tabla = ttk.Treeview(
        marco,
        columns=identificadores,
        show="headings",
        height=7
    )

    # Configurar los encabezados y el ancho de las columnas.
     for identificador, titulo, ancho in columnas:

        tabla.heading(
            identificador,
            text=titulo
        )

        tabla.column(
            identificador,
            width=ancho,
            minwidth=80,
            anchor="center"
        )

    # Crear la barra de desplazamiento vertical.
     barra_vertical = ttk.Scrollbar(
        marco,
        orient="vertical",
        command=tabla.yview
    )

     tabla.configure(
        yscrollcommand=barra_vertical.set
    )

    # Ubicar la tabla y la barra de desplazamiento.
     marco.grid_columnconfigure(0, weight=1)
     marco.grid_rowconfigure(0, weight=1)

     tabla.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

     barra_vertical.grid(
        row=0,
        column=1,
        sticky="ns"
    )

     return tabla

    
# ============================================================
# BLOQUE: SELECCIONAR EL ARCHIVO DE POSICIONES
# Abre el explorador y guarda la ruta del CSV seleccionado.
# ============================================================

    def seleccionar_posiciones(self):

        ruta = filedialog.askopenfilename(
        title="Seleccionar archivo de posiciones",
        filetypes=[("Archivos CSV", "*.csv")]
    )

    # Si el usuario cierra la ventana, no cambia nada.
        if not ruta:
           return

    # Guardamos la ubicación del archivo seleccionado.
        self.ruta_posiciones = Path(ruta)

    # Mostramos el nombre del archivo en la interfaz.
        self.posiciones_file_label.configure(
        text=self.ruta_posiciones.name,
        text_color="#16845B"
    )
    # Invalidar resultados anteriores porque cambió el archivo.
        self.resultados_actuales = None

    # Limpiar las tablas y deshabilitar la exportación.
        self.actualizar_vista_resultados()

    # Actualizamos el estado de la aplicación.
        self.actualizar_estado_archivos()


    # ============================================================
    # MÉTODO: ACTUALIZAR EL ESTADO DE LOS ARCHIVOS
    # Comprueba el registro y la selección de ambos CSV.
    # ============================================================

    def actualizar_estado_archivos(self):

        # No permitir el procesamiento sin registro de proyecto.
        if self.datos_proyecto is None:

            self.calculate_button.configure(state="disabled")

            self.status_label.configure(
                text="Estado: Primero debes registrar el proyecto."
            )

            return

        # Ambos archivos están seleccionados.
        if self.ruta_paneles and self.ruta_posiciones:

            self.calculate_button.configure(state="normal")

            self.status_label.configure(
                text="Estado: Proyecto registrado y archivos seleccionados."
            )

        # Solo está seleccionado el archivo de paneles.
        elif self.ruta_paneles:

            self.calculate_button.configure(state="disabled")

            self.status_label.configure(
                text="Estado: Falta seleccionar el archivo de posiciones."
            )

        # Solo está seleccionado el archivo de posiciones.
        elif self.ruta_posiciones:

            self.calculate_button.configure(state="disabled")

            self.status_label.configure(
                text="Estado: Falta seleccionar el archivo de paneles."
            )

        # Todavía no se ha seleccionado ningún archivo.
        else:

            self.calculate_button.configure(state="disabled")

            self.status_label.configure(
                text="Estado: Proyecto registrado. Selecciona los dos CSV."
            )
# ============================================================
# BLOQUE: CALCULAR LA ASIGNACIÓN
# Ejecuta la lectura, validación y asignación de paneles.
# ============================================================

    def calcular_asignacion(self):

        # ----------------------------------------------------
        # 1. Comprobar que los dos archivos estén seleccionados.
        # ----------------------------------------------------

        if self.ruta_paneles is None or self.ruta_posiciones is None:

            messagebox.showwarning(
                "Archivos faltantes",
                "Debes seleccionar los archivos de paneles "
                "y posiciones antes de continuar.",
                parent=self
            )

            return

        # ----------------------------------------------------
        # 2. Actualizar el mensaje de estado.
        # ----------------------------------------------------

        self.status_label.configure(
            text="Estado: Procesando archivos y calculando asignación..."
        )

        self.update_idletasks()

        # ----------------------------------------------------
        # 3. Ejecutar la función principal de main.py.
        # ----------------------------------------------------

        try:

         respuesta = procesar_archivos_con_geometria(
         self.ruta_paneles,
         self.ruta_posiciones,

         self.datos_geometria["longitud_muro_m"],
         self.datos_geometria["longitud_panel_m"],

         self.datos_geometria["altura_inicial_m"],
         self.datos_geometria["altura_final_m"],

         self.datos_geometria["paso_altura_m"],
         self.datos_geometria["modo_flexible"]
        )

        except Exception as error:  # noqa: BLE001

            self.resultados_actuales = None

            # Mostrar el detalle técnico en la consola.
            print(f"Error inesperado durante el procesamiento: {error!r}")

            self.status_label.configure(
                text="Estado: Error inesperado durante el procesamiento."
            )

            messagebox.showerror(
                "Error inesperado",
                "No se pudo completar el procesamiento. "
                "Revisa la consola de Python para identificar el problema.",
                parent=self
            )

            return

        # ----------------------------------------------------
        # 4. Comprobar si existen errores de lectura o validación.
        # ----------------------------------------------------

        if not respuesta["correcto"]:

            self.resultados_actuales = None
            self.actualizar_vista_resultados()

            errores = respuesta["errores"]

            detalle_errores = "\n".join(
                f"- {error}" for error in errores
            )

            self.status_label.configure(
                text="Estado: Se encontraron errores en los archivos."
            )

            messagebox.showerror(
                "Errores en los archivos",
                detalle_errores,
                parent=self
            )

            return

        # ----------------------------------------------------
        # 5. Guardar los resultados obtenidos.
        # ----------------------------------------------------

        self.resultados_actuales = respuesta["resultados"]
        # Actualizar las tablas y el resumen de resultados.
        self.actualizar_vista_resultados()

        self.status_label.configure(
            text="Estado: Procesamiento completado correctamente."
        )

        messagebox.showinfo(
            "Proceso completado",
            "Los archivos fueron leídos y validados correctamente.\n\n"
            "La asignación de paneles se calculó correctamente. "
            "Los resultados están disponibles para mostrarlos "
            "en las tablas de la interfaz.",
            parent=self
        )
# ============================================================
# BLOQUE 6: INICIAR LA APLICACIÓN
# Este bloque abre la ventana y mantiene el programa activo.
# ============================================================
    # ============================================================
    # MÉTODO: ACTUALIZAR LA VISTA DE RESULTADOS
    # Llena las tres tablas y actualiza el resumen de cantidades.
    # ============================================================

    def actualizar_vista_resultados(self):

        # --------------------------------------------------------
        # 1. LIMPIAR LAS TABLAS ANTES DE CARGAR NUEVOS DATOS
        # --------------------------------------------------------

        tablas = [
            self.tabla_asignaciones,
            self.tabla_pendientes,
            self.tabla_sobrantes,
            self.tabla_diagnostico
        ]

        for tabla in tablas:

            for elemento in tabla.get_children():

                tabla.delete(elemento)

        # Obtener los resultados guardados.
        resultados = self.resultados_actuales

        # --------------------------------------------------------
        # 2. SI NO HAY RESULTADOS, RESTABLECER EL RESUMEN
        # --------------------------------------------------------

        if resultados is None:

            self.total_posiciones_label.configure(
                text="Posiciones: 0"
            )

            self.total_asignadas_label.configure(
                text="Asignadas: 0"
            )

            self.total_pendientes_label.configure(
                text="Pendientes: 0"
            )

            self.total_sobrantes_label.configure(
                text="Paneles sobrantes: 0"
            )
            self.export_button.configure(state="disabled")
            self.pdf_button.configure(state="disabled")
            self.diagnostico_resumen_label.configure(
            text="El diagnóstico aparecerá después de calcular."
            )
            return 
        # Habilitar la exportación porque existen resultados.
        self.export_button.configure(state="normal")
        self.pdf_button.configure(state="normal")

        # --------------------------------------------------------
        # 3. LLENAR LA TABLA DE ASIGNACIONES
        # Los registros son diccionarios.
        # --------------------------------------------------------

        for asignacion in resultados["asignaciones"]:

            self.tabla_asignaciones.insert(
                "",
                "end",
                values=(
                    asignacion["id_posicion"],
                    asignacion["ubicacion"],
                    asignacion["id_panel"],
                    asignacion["altura_panel_mm"],
                    asignacion["cota_apoyo_mm"],
                    asignacion["cota_superior_mm"]
                )
            )

        # --------------------------------------------------------
        # 4. LLENAR LA TABLA DE POSICIONES PENDIENTES
        # Los registros son objetos de tipo Posicion.
        # --------------------------------------------------------

        for posicion in resultados["posiciones_pendientes"]:

            self.tabla_pendientes.insert(
                "",
                "end",
                values=(
                    posicion.id_posicion,
                    posicion.ubicacion,
                    posicion.cota_apoyo_mm,
                    posicion.altura_min_mm,
                    posicion.altura_max_mm,
                    posicion.familia_admitida
                )
            )

        # --------------------------------------------------------
        # 5. LLENAR LA TABLA DE PANELES SOBRANTES
        # Los registros son objetos de tipo Panel.
        # --------------------------------------------------------

        for panel in resultados["paneles_sobrantes"]:

            self.tabla_sobrantes.insert(
                "",
                "end",
                values=(
                    panel.id_panel,
                    panel.altura_mm,
                    panel.familia
                )
            )

        # --------------------------------------------------------
        # 6. LLENAR EL DIAGNÓSTICO DEL INVENTARIO
        # --------------------------------------------------------

        diagnostico = resultados.get(
            "diagnostico_asignacion", {}
        )

        candidatos = diagnostico.get(
            "candidatos_por_posicion", []
        )

        rechazos = diagnostico.get(
            "rechazos_por_posicion", []
        )

        # Relacionar los motivos de rechazo con cada posición.
        rechazos_por_orden = {
            registro["orden"]: registro.get("motivos", {})
            for registro in rechazos
        }

        nombres_motivos = {
            "no_disponible": "No disponibles",
            "familia_incompatible": "Familia incompatible",
            "fuera_intervalo_altura": "Fuera del intervalo",
            "no_cumple_paso_altura": "No cumple el paso",
            "no_cumple_altura_inicial": "No cumple altura inicial"
        }

        for candidato in candidatos:

            orden = candidato["orden"]

            ids_candidatos = candidato.get(
                "ids_paneles_candidatos", []
            )

            motivos = rechazos_por_orden.get(
                orden, {}
            )

            # Construir el texto de motivos de rechazo.
            detalles_rechazo = []

            for clave, nombre in nombres_motivos.items():

                ids_rechazados = motivos.get(clave, [])

                if ids_rechazados:

                    detalles_rechazo.append(
                        f"{nombre}: {', '.join(ids_rechazados)}"
                    )

            texto_candidatos = (
                ", ".join(ids_candidatos)
                if ids_candidatos
                else "Ninguno"
            )

            texto_rechazos = (
                " | ".join(detalles_rechazo)
                if detalles_rechazo
                else "Sin rechazos"
            )

            self.tabla_diagnostico.insert(
                "",
                "end",
                values=(
                    orden,
                    candidato["id_posicion"],
                    candidato["cantidad_candidatos"],
                    texto_candidatos,
                    texto_rechazos
                )
            )

        # --------------------------------------------------------
        # RESUMEN DEL INVENTARIO
        # --------------------------------------------------------

        total_inventario = diagnostico.get(
            "total_paneles_inventario", 0
        )

        total_disponibles = diagnostico.get(
            "total_paneles_disponibles", 0
        )

        total_candidatos = diagnostico.get(
            "total_paneles_candidatos", 0
        )

        total_asignados = diagnostico.get(
            "total_paneles_asignados", 0
        )

        total_sin_compatibilidad = diagnostico.get(
            "total_paneles_disponibles_sin_candidato",
            0
        )

        total_no_disponibles = len(
            diagnostico.get("paneles_no_disponibles", [])
        )

        direccion = diagnostico.get(
            "direccion_muro", "No disponible"
        )

        modo = diagnostico.get(
            "modo_altura", "No disponible"
        )

        paso = diagnostico.get(
            "paso_altura_mm", 0
        )

        salto = diagnostico.get(
            "salto_maximo_mm", 0
        )

        self.diagnostico_resumen_label.configure(
            text=(
                f"Inventario: {total_inventario} | "
                f"Disponibles: {total_disponibles} | "
                f"Candidatos: {total_candidatos} | "
                f"Asignados: {total_asignados}\n"
                f"Disponibles sin compatibilidad: "
                f"{total_sin_compatibilidad} | "
                f"No disponibles: {total_no_disponibles}\n"
                f"Perfil: {direccion} | Modo: {modo} | "
                f"Paso: {paso} mm | Salto máximo: {salto} mm"
            )
        )

        # --------------------------------------------------------
        # 6. ACTUALIZAR EL RESUMEN GENERAL
        # --------------------------------------------------------

        self.total_posiciones_label.configure(
            text=f"Posiciones: {resultados['total_posiciones']}"
        )

        self.total_asignadas_label.configure(
            text=f"Asignadas: {resultados['total_asignadas']}"
        )

        self.total_pendientes_label.configure(
            text=f"Pendientes: {resultados['total_pendientes']}"
        )

        self.total_sobrantes_label.configure(
            text=(
                f"Paneles sobrantes: "
                f"{resultados['total_paneles_sobrantes']}"
            )
        )
        # ============================================================
    # MÉTODO: EXPORTAR RESULTADOS
    # Guarda las tablas y el resumen en cuatro archivos CSV.
    # ============================================================

    # ============================================================
    # MÉTODO: EXPORTAR RESULTADOS
    # Guarda los resultados y la identificación del proyecto
    # en archivos CSV.
    # ============================================================

    def exportar_resultados(self):

        # --------------------------------------------------------
        # 1. Comprobar que existan resultados y registro.
        # --------------------------------------------------------

        if self.resultados_actuales is None:

            messagebox.showwarning(
                "Sin resultados",
                "Primero debes calcular la asignación.",
                parent=self
            )
            return

        if self.datos_proyecto is None:

            messagebox.showwarning(
                "Proyecto sin registrar",
                "Primero debes registrar la información del proyecto.",
                parent=self
            )
            return

        # --------------------------------------------------------
        # 2. Solicitar la carpeta de destino.
        # --------------------------------------------------------

        carpeta = filedialog.askdirectory(
            title="Seleccionar carpeta para guardar los resultados",
            mustexist=True
        )

        if not carpeta:
            return

        carpeta_salida = Path(carpeta)

        resultados = self.resultados_actuales

        # --------------------------------------------------------
        # 3. Preparar la identificación del proyecto.
        # --------------------------------------------------------

         # Identificación y trazabilidad de la exportación.
        datos_proyecto = {

            "responsable": self.datos_proyecto["responsable"],

            "nombre_proyecto": self.datos_proyecto["nombre_proyecto"],

            "fecha_proyecto": self.datos_proyecto["fecha"],

            "fecha_generacion_informe": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "archivo_paneles": self.ruta_paneles.name,

            "archivo_posiciones": self.ruta_posiciones.name

        }
        columnas_proyecto = list(datos_proyecto.keys())

        # Agregar los datos del proyecto a cada registro.
        def agregar_identificacion(filas):

            return [
                {**datos_proyecto, **fila}
                for fila in filas
            ]

        # --------------------------------------------------------
        # 4. Organizar las posiciones pendientes.
        # --------------------------------------------------------

        filas_pendientes = []

        for posicion in resultados["posiciones_pendientes"]:

            filas_pendientes.append({
                
                "orden": posicion.orden,

                "id_posicion": posicion.id_posicion,

                "ubicacion": posicion.ubicacion,

                "cota_apoyo_mm": posicion.cota_apoyo_mm,

                "altura_min_mm": posicion.altura_min_mm,

                "altura_max_mm": posicion.altura_max_mm,

                "familia_admitida": posicion.familia_admitida

            })

        # --------------------------------------------------------
        # 5. Organizar los paneles sobrantes.
        # --------------------------------------------------------

        filas_sobrantes = []

        for panel in resultados["paneles_sobrantes"]:

            filas_sobrantes.append({

                "id_panel": panel.id_panel,

                "altura_mm": panel.altura_mm,

                "familia": panel.familia

            })

        # --------------------------------------------------------
        # 5.1 ORGANIZAR POSICIONES GEOMETRICAS
        # --------------------------------------------------------

        geometria = resultados["geometria_muro"]

        comparacion = resultados["comparacion_geometrica"]

        coincidencias_por_orden = {
            registro["orden"]: registro
            for registro in comparacion["posiciones_coincidentes"]
        }

        filas_geometricas = []

        for posicion_geo in geometria["posiciones_geometricas"]:

            coincidencia = coincidencias_por_orden.get(
                posicion_geo["orden"], {}
            )

            filas_geometricas.append({
                "orden": posicion_geo["orden"],
                "id_posicion_geometrica":
                    posicion_geo["id_posicion_geometrica"],
                "progresiva_inicio_m":
                    posicion_geo["progresiva_inicio_m"],
                "progresiva_fin_m":
                    posicion_geo["progresiva_fin_m"],
                "id_posicion_csv":
                    coincidencia.get("id_posicion_csv", ""),
                "ubicacion":
                    coincidencia.get("ubicacion", "")
            })

        # --------------------------------------------------------
        # 5.2 ORGANIZAR DIAGNOSTICO DEL INVENTARIO
        # --------------------------------------------------------

        diagnostico = resultados["diagnostico_asignacion"]

        candidatos = diagnostico["candidatos_por_posicion"]

        rechazos = diagnostico["rechazos_por_posicion"]

        rechazos_por_orden = {
            registro["orden"]: registro.get("motivos", {})
            for registro in rechazos
        }

        filas_diagnostico = []

        for candidato in candidatos:

            orden = candidato["orden"]

            motivos = rechazos_por_orden.get(orden, {})

            filas_diagnostico.append({
                "orden": orden,
                "id_posicion": candidato["id_posicion"],
                "cantidad_candidatos":
                    candidato["cantidad_candidatos"],
                "paneles_candidatos": ", ".join(
                    candidato["ids_paneles_candidatos"]
                ),
                "no_disponibles": ", ".join(
                    motivos.get("no_disponible", [])
                ),
                "familia_incompatible": ", ".join(
                    motivos.get("familia_incompatible", [])
                ),
                "fuera_intervalo_altura": ", ".join(
                    motivos.get("fuera_intervalo_altura", [])
                ),
                "no_cumple_paso_altura": ", ".join(
                    motivos.get("no_cumple_paso_altura", [])
                ),
                "no_cumple_altura_inicial": ", ".join(
                    motivos.get("no_cumple_altura_inicial", [])
                )
            })

        # --------------------------------------------------------
        # 5.3 ORGANIZAR PANELES DISPONIBLES SIN COMPATIBILIDAD
        # --------------------------------------------------------

        filas_sin_compatibilidad = []

        for panel in diagnostico[
            "paneles_disponibles_sin_candidato"
        ]:

            filas_sin_compatibilidad.append({
                "id_panel": panel.id_panel,
                "altura_mm": panel.altura_mm,
                "familia": panel.familia,
                "motivo": (
                    "No cumple las condiciones de ninguna posición."
                )
            })

        # --------------------------------------------------------
        # 6. Preparar el resumen general.
        # --------------------------------------------------------

        # --------------------------------------------------------
        # 6. PREPARAR EL RESUMEN GENERAL
        # --------------------------------------------------------

        geometria_configurada = self.datos_geometria

        filas_resumen = [{

            "longitud_muro_m": geometria_configurada[
                "longitud_muro_m"
            ],

            "longitud_panel_m": geometria_configurada[
                "longitud_panel_m"
            ],

            "cantidad_paneles_necesarios": (
                resultados["cantidad_paneles_necesarios"]
            ),

            "longitud_cubierta_m": (
                resultados["longitud_cubierta_m"]
            ),

            "espacio_sobrante_m": (
                resultados["espacio_sobrante_m"]
            ),

            "altura_inicial_m": geometria_configurada[
                "altura_inicial_m"
            ],

            "altura_final_m": geometria_configurada[
                "altura_final_m"
            ],

            "paso_altura_m": geometria_configurada[
                "paso_altura_m"
            ],

            "modo_altura": resultados["modo_altura"],

            "direccion_muro": resultados["direccion_muro"],

            "alcanza_altura_final": (
                resultados["alcanza_altura_final"]
            ),

            "total_paneles_inventario": (
                diagnostico["total_paneles_inventario"]
            ),

            "total_paneles_disponibles": (
                diagnostico["total_paneles_disponibles"]
            ),

            "total_paneles_candidatos": (
                diagnostico["total_paneles_candidatos"]
            ),

            "total_paneles_asignados": (
                diagnostico["total_paneles_asignados"]
            ),

            "total_paneles_sin_compatibilidad": (
                diagnostico[
                    "total_paneles_disponibles_sin_candidato"
                ]
            ),

            "total_posiciones": resultados["total_posiciones"],

            "total_asignadas": resultados["total_asignadas"],

            "total_pendientes": resultados["total_pendientes"],

            "total_paneles_sobrantes": (
                resultados["total_paneles_sobrantes"]
            )

        }]
        # --------------------------------------------------------
        # 7. Preparar los cinco archivos CSV.
        # --------------------------------------------------------

        archivos_exportacion = {

            # Archivo exclusivo de identificación del proyecto.
            "identificacion_proyecto.csv": (
                columnas_proyecto,
                [datos_proyecto]
            ),

            # Tabla de asignaciones.
            "asignaciones.csv": (
            columnas_proyecto + [
            "orden",
            "id_posicion",
            "ubicacion",
            "id_panel",
            "altura_panel_mm",
            "cota_apoyo_mm",
            "cota_superior_mm"
            ],
               agregar_identificacion(resultados["asignaciones"])
        ),
            # Tabla de posiciones pendientes.
            "posiciones_pendientes.csv": (
            columnas_proyecto + [
            "orden",
            "id_posicion",
            "ubicacion",
            "cota_apoyo_mm",
            "altura_min_mm",
            "altura_max_mm",
            "familia_admitida"
                ],
               agregar_identificacion(filas_pendientes)
            ),

            # Tabla de paneles sobrantes.
            "paneles_sobrantes.csv": (
                columnas_proyecto + [
                    "id_panel",
                    "altura_mm",
                    "familia"
                ],
                agregar_identificacion(filas_sobrantes)
            ),

            # Resumen general.
            "resumen.csv": (
                columnas_proyecto + [
                    "total_posiciones",
                    "total_asignadas",
                    "total_pendientes",
                    "total_paneles_sobrantes"
                ],
                agregar_identificacion(filas_resumen)
            ),
            # Posiciones generadas por la geometría.
            "posiciones_geometricas.csv": (
                columnas_proyecto + [
                    "orden",
                    "id_posicion_geometrica",
                    "progresiva_inicio_m",
                    "progresiva_fin_m",
                    "id_posicion_csv",
                    "ubicacion"
                ],
                agregar_identificacion(filas_geometricas)
            ),

            # Diagnóstico de compatibilidad por posición.
            "diagnostico_inventario.csv": (
                columnas_proyecto + [
                    "orden",
                    "id_posicion",
                    "cantidad_candidatos",
                    "paneles_candidatos",
                    "no_disponibles",
                    "familia_incompatible",
                    "fuera_intervalo_altura",
                    "no_cumple_paso_altura",
                    "no_cumple_altura_inicial"
                ],
                agregar_identificacion(filas_diagnostico)
            ),

            # Paneles disponibles que no sirven para ninguna posición.
            "paneles_sin_compatibilidad.csv": (
                columnas_proyecto + [
                    "id_panel",
                    "altura_mm",
                    "familia",
                    "motivo"
                ],
                agregar_identificacion(filas_sin_compatibilidad)
            )
        }

        # --------------------------------------------------------
        # 8. Comprobar si los archivos ya existen.
        # --------------------------------------------------------

        existentes = [

            nombre

            for nombre in archivos_exportacion

            if (carpeta_salida / nombre).exists()

        ]

        if existentes:

            lista_existentes = "\n".join(
                f"- {nombre}" for nombre in existentes
            )

            confirmar = messagebox.askyesno(
                "Confirmar reemplazo",
                "Los siguientes archivos ya existen:\n\n"
                f"{lista_existentes}\n\n"
                "¿Deseas reemplazarlos?",
                parent=self
            )

            if not confirmar:
                return

        # --------------------------------------------------------
        # 9. Escribir los archivos CSV.
        # --------------------------------------------------------

        try:

            for nombre, (columnas, filas) in archivos_exportacion.items():

                ruta_salida = carpeta_salida / nombre

                with open(
                    ruta_salida,
                    "w",
                    newline="",
                    encoding="utf-8-sig"
                ) as archivo:

                    escritor = csv.DictWriter(
                        archivo,
                        fieldnames=columnas,
                        delimiter=";"
                    )

                    escritor.writeheader()

                    escritor.writerows(filas)

        except (OSError, csv.Error) as error:

            self.status_label.configure(
                text="Estado: Error durante la exportación."
            )

            messagebox.showerror(
                "Error de exportación",
                "No fue posible guardar todos los archivos.\n\n"
                f"Detalle: {error}",
                parent=self
            )

            return

        # --------------------------------------------------------
        # 10. Informar que la exportación terminó correctamente.
        # --------------------------------------------------------

        self.status_label.configure(
            text="Estado: Resultados exportados correctamente."
        )

        messagebox.showinfo(
            "Exportación completada",
            "Los ocho archivos CSV se guardaron correctamente en:\n\n"
            f"{carpeta_salida}",
            parent=self
        )
    # ============================================================
    # MÉTODO: EXPORTAR PDF
    # Genera un informe completo con los datos del proyecto
    # y las tres tablas de resultados.
    # ============================================================

    def exportar_pdf(self):

        # --------------------------------------------------------
        # 1. COMPROBAR QUE EXISTAN LOS DATOS NECESARIOS
        # --------------------------------------------------------

        if self.resultados_actuales is None:

            messagebox.showwarning(
                "Sin resultados",
                "Primero debes calcular la asignación.",
                parent=self
            )
            return

        if self.datos_proyecto is None:

            messagebox.showwarning(
                "Proyecto sin registrar",
                "Primero debes registrar los datos del proyecto.",
                parent=self
            )
            return

        # --------------------------------------------------------
        # 2. SOLICITAR DÓNDE GUARDAR EL DOCUMENTO
        # --------------------------------------------------------

        ruta = filedialog.asksaveasfilename(
            title="Guardar informe de PANELMSE",
            initialfile="Informe_PANELMSE.pdf",
            defaultextension=".pdf",
            filetypes=[
                ("Documento PDF", "*.pdf")
            ]
        )

        if not ruta:
            return

        ruta_pdf = Path(ruta)

        resultados = self.resultados_actuales
        proyecto = self.datos_proyecto

        # Registrar cuándo se genera este informe.

        fecha_generacion = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Obtener los nombres de los archivos utilizados.
        archivo_paneles = self.ruta_paneles.name

        archivo_posiciones = self.ruta_posiciones.name

        # --------------------------------------------------------
        # 3. DEFINIR LOS ESTILOS DEL DOCUMENTO
        # --------------------------------------------------------

        estilos = getSampleStyleSheet()

        estilo_titulo = ParagraphStyle(
            "TituloPANELMSE",
            parent=estilos["Title"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=23,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#192B40"),
            spaceAfter=5
        )

        estilo_subtitulo = ParagraphStyle(
            "SubtituloPANELMSE",
            parent=estilos["Normal"],
            fontName="Helvetica",
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#647386"),
            spaceAfter=18
        )

        estilo_seccion = ParagraphStyle(
            "SeccionPANELMSE",
            parent=estilos["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#192B40"),
            spaceBefore=12,
            spaceAfter=8
        )

        estilo_celda = ParagraphStyle(
            "CeldaPANELMSE",
            parent=estilos["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=9,
            textColor=colors.HexColor("#273447")
        )

        estilo_encabezado = ParagraphStyle(
            "EncabezadoTablaPANELMSE",
            parent=estilo_celda,
            fontName="Helvetica-Bold",
            textColor=colors.white
        )

        estilo_etiqueta = ParagraphStyle(
            "EtiquetaPANELMSE",
            parent=estilo_celda,
            fontName="Helvetica-Bold",
            fontSize=9
        )

        estilo_valor_resumen = ParagraphStyle(
            "ValorResumenPANELMSE",
            parent=estilo_celda,
            fontName="Helvetica-Bold",
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#192B40")
        )

        estilo_etiqueta_resumen = ParagraphStyle(
            "EtiquetaResumenPANELMSE",
            parent=estilo_celda,
            fontName="Helvetica-Bold",
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#647386")
        )

        estilo_nota = ParagraphStyle(
            "NotaPANELMSE",
            parent=estilo_celda,
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#647386")
        )

        # Convertir los datos en texto seguro para los párrafos.
        def texto_seguro(valor):

            if valor is None:
                return "—"

            return escape(str(valor))

        # --------------------------------------------------------
        # 4. CREAR UNA FUNCIÓN PARA CONSTRUIR TABLAS
        # --------------------------------------------------------

        def crear_tabla(encabezados, filas, anchos):

            datos_tabla = [

                [
                    Paragraph(
                        texto_seguro(encabezado),
                        estilo_encabezado
                    )
                    for encabezado in encabezados
                ]

            ]

            # Convertir los registros en celdas de texto.
            for fila in filas:

                datos_tabla.append(

                    [
                        Paragraph(
                            texto_seguro(valor),
                            estilo_celda
                        )
                        for valor in fila
                    ]

                )

            # LongTable permite dividir tablas entre páginas
            # y repetir el encabezado en cada página.
            tabla = LongTable(
                datos_tabla,
                colWidths=anchos,
                repeatRows=1,
                hAlign="LEFT"
            )

            formato = [

                ("BACKGROUND", (0, 0), (-1, 0),
                 colors.HexColor("#192B40")),

                ("GRID", (0, 0), (-1, -1),
                 0.4, colors.HexColor("#DCE2EA")),

                ("VALIGN", (0, 0), (-1, -1), "TOP"),

                ("LEFTPADDING", (0, 0), (-1, -1), 5),

                ("RIGHTPADDING", (0, 0), (-1, -1), 5),

                ("TOPPADDING", (0, 0), (-1, -1), 6),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)

            ]

            # Aplicar fondos alternos para facilitar la lectura.
            for numero_fila in range(1, len(datos_tabla)):

                if numero_fila % 2 == 0:

                    formato.append(
                        (
                            "BACKGROUND",
                            (0, numero_fila),
                            (-1, numero_fila),
                            colors.HexColor("#F3F5F8")
                        )
                    )

            tabla.setStyle(TableStyle(formato))

            return tabla

        # --------------------------------------------------------
        # 5. INICIAR EL CONTENIDO DEL INFORME
        # --------------------------------------------------------

        contenido = []

        contenido.append(
            Paragraph(
                "PANELMSE",
                estilo_titulo
            )
        )

        contenido.append(
            Paragraph(
                "INFORME DE ASIGNACIÓN DE PANELES PREFABRICADOS MSE",
                estilo_subtitulo
            )
        )

        # --------------------------------------------------------
        # 6. IDENTIFICACIÓN DEL PROYECTO
        # --------------------------------------------------------

        contenido.append(
            Paragraph(
                "Identificación del proyecto",
                estilo_seccion
            )
        )

        datos_identificacion = [

            [
                Paragraph("Responsable:", estilo_etiqueta),
                Paragraph(
                    texto_seguro(proyecto["responsable"]),
                    estilo_celda
                )
            ],

            [
                Paragraph("Nombre del proyecto:", estilo_etiqueta),
                Paragraph(
                    texto_seguro(proyecto["nombre_proyecto"]),
                    estilo_celda
                )
            ],

            [
                Paragraph("Fecha del proyecto:", estilo_etiqueta),
                Paragraph(
                    texto_seguro(proyecto["fecha"]),
                    estilo_celda
                )
            ],

            [
                Paragraph( 
                    "Fecha de generación del informe:",
                     estilo_etiqueta
                ),
                Paragraph(
                    texto_seguro(fecha_generacion),
                    estilo_celda
                )
            ],

            [
                Paragraph(
                    "Archivo de paneles utilizado:",
                    estilo_etiqueta
                ),
                Paragraph(
                    texto_seguro(archivo_paneles),
                    estilo_celda
                )
            ],

            [
                Paragraph(
                    "Archivo de posiciones utilizado:",
                    estilo_etiqueta
                ),
                Paragraph(
                    texto_seguro(archivo_posiciones),
                    estilo_celda
                )
            ]

        ]

        tabla_identificacion = Table(
            datos_identificacion,
            colWidths=[190, 565]
        )

        tabla_identificacion.setStyle(
            TableStyle([

                ("BACKGROUND", (0, 0), (0, -1),
                 colors.HexColor("#F3F5F8")),

                ("GRID", (0, 0), (-1, -1),
                 0.5, colors.HexColor("#DCE2EA")),

                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                ("LEFTPADDING", (0, 0), (-1, -1), 8),

                ("RIGHTPADDING", (0, 0), (-1, -1), 8),

                ("TOPPADDING", (0, 0), (-1, -1), 7),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 7)

            ])
        )

        contenido.append(tabla_identificacion)

        contenido.append(Spacer(1, 12))

        # --------------------------------------------------------
        # 7. RESUMEN GENERAL DE LOS RESULTADOS
        # --------------------------------------------------------

        contenido.append(
            Paragraph(
                "Resumen general",
                estilo_seccion
            )
        )

        datos_resumen = [

            [
                Paragraph("POSICIONES", estilo_etiqueta_resumen),
                Paragraph("ASIGNADAS", estilo_etiqueta_resumen),
                Paragraph("PENDIENTES", estilo_etiqueta_resumen),
                Paragraph("PANELES SOBRANTES", estilo_etiqueta_resumen)
            ],

            [
                Paragraph(
                    str(resultados["total_posiciones"]),
                    estilo_valor_resumen
                ),

                Paragraph(
                    str(resultados["total_asignadas"]),
                    estilo_valor_resumen
                ),

                Paragraph(
                    str(resultados["total_pendientes"]),
                    estilo_valor_resumen
                ),

                Paragraph(
                    str(resultados["total_paneles_sobrantes"]),
                    estilo_valor_resumen
                )
            ]

        ]

        tabla_resumen = Table(
            datos_resumen,
            colWidths=[188, 188, 188, 188]
        )

        tabla_resumen.setStyle(
            TableStyle([

                ("BACKGROUND", (0, 0), (-1, 0),
                 colors.HexColor("#F3F5F8")),

                ("GRID", (0, 0), (-1, -1),
                 0.5, colors.HexColor("#DCE2EA")),

                ("ALIGN", (0, 0), (-1, -1), "CENTER"),

                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                ("TOPPADDING", (0, 0), (-1, -1), 8),

                ("BOTTOMPADDING", (0, 0), (-1, -1), 8)

            ])
        )

        contenido.append(tabla_resumen)
                # --------------------------------------------------------
        # GEOMETRIA Y PERFIL DE ALTURAS DEL MURO
        # --------------------------------------------------------

        geometria_configurada = self.datos_geometria

        contenido.append(Spacer(1, 12))

        contenido.append(
            Paragraph(
                "Geometría y perfil de alturas del muro",
                estilo_seccion
            )
        )

        filas_geometria = [

            [
                "Longitud total del muro",
                f"{geometria_configurada['longitud_muro_m']} m",
                "Longitud de cada panel",
                f"{geometria_configurada['longitud_panel_m']} m"
            ],

            [
                "Paneles necesarios",
                str(resultados["cantidad_paneles_necesarios"]),
                "Longitud cubierta",
                f"{resultados['longitud_cubierta_m']} m"
            ],

            [
                "Espacio sobrante",
                f"{resultados['espacio_sobrante_m']} m",
                "Dirección del muro",
                resultados["direccion_muro"]
            ],

            [
                "Altura inicial",
                f"{geometria_configurada['altura_inicial_m']} m",
                "Altura final",
                f"{geometria_configurada['altura_final_m']} m"
            ],

            [
                "Paso de altura",
                f"{geometria_configurada['paso_altura_m']} m",
                "Modo de progresión",
                resultados["modo_altura"]
            ],

            [
                "Altura final alcanzada",
                "Sí" if resultados["alcanza_altura_final"] else "No",
                "Posiciones geométricas",
                str(resultados["cantidad_paneles_necesarios"])
            ]

        ]

        contenido.append(
            crear_tabla(
                [
                    "Parámetro",
                    "Resultado",
                    "Parámetro",
                    "Resultado"
                ],
                filas_geometria,
                [190, 200, 190, 200]
            )
        )
        # --------------------------------------------------------
        # ACLARACIÓN SOBRE EL ALCANCE DEL PROGRAMA
        # --------------------------------------------------------

        contenido.append(Spacer(1, 12))

        contenido.append(
            Paragraph(
                "<b>ALCANCE Y LIMITACIONES</b>",
                estilo_seccion
            )
        )

        contenido.append(
            Paragraph(
                "PANELMSE es una herramienta de apoyo para la "
                "asignación de paneles prefabricados MSE. Los "
                "resultados se basan en los criterios de "
                "compatibilidad de altura, familia y disponibilidad "
                "establecidos en los archivos de entrada. Este "
                "procesamiento no sustituye la verificación "
                "estructural del muro ni realiza cálculos de "
                "refuerzos, anclajes, estabilidad o modificaciones "
                "de los elementos constructivos.",
                estilo_nota
            )
        )

        contenido.append(Spacer(1, 10))

        # --------------------------------------------------------
        # 8. TABLA DE ASIGNACIONES
        # --------------------------------------------------------

        contenido.append(
            Paragraph(
                "Asignaciones realizadas",
                estilo_seccion
            )
        )

        filas_asignaciones = [

            [
                registro["orden"],
                registro["id_posicion"],
                registro["ubicacion"],
                registro["id_panel"],
                registro["altura_panel_mm"],
                registro["cota_apoyo_mm"],
                registro["cota_superior_mm"]
            ]

            for registro in resultados["asignaciones"]

        ]

        if filas_asignaciones:

            contenido.append(
                crear_tabla(
                    [
                        "Orden",
                        "Posición",
                        "Ubicación",
                        "Panel",
                        "Altura panel (mm)",
                        "Cota apoyo (mm)",
                        "Cota superior (mm)"
                    ],
                    filas_asignaciones,
                    [40, 65, 145, 65, 120, 120, 200]
                )
            )

        else:

            contenido.append(
                Paragraph(
                    "No se registraron asignaciones.",
                    estilo_celda
                )
            )

        # --------------------------------------------------------
        # 9. TABLA DE POSICIONES PENDIENTES
        # --------------------------------------------------------

        contenido.append(
            Paragraph(
                "Posiciones pendientes",
                estilo_seccion
            )
        )

        filas_pendientes = [

            [
                posicion.orden,
                posicion.id_posicion,
                posicion.ubicacion,
                posicion.cota_apoyo_mm,
                posicion.altura_min_mm,
                posicion.altura_max_mm,
                posicion.familia_admitida
            ]

            for posicion in resultados["posiciones_pendientes"]

        ]

        if filas_pendientes:

            contenido.append(
                crear_tabla(
                     [
                        "Orden",
                        "Posición",
                        "Ubicación",
                        "Cota apoyo (mm)",
                        "Altura mínima (mm)",
                        "Altura máxima (mm)",
                        "Familia admitida"
                    ],
                    filas_pendientes,
                    [40, 65, 135, 110, 110, 110, 130]
            )
            )
        else:

            contenido.append(
                Paragraph(
                    "No hay posiciones pendientes.",
                    estilo_celda
                )
            )

        # --------------------------------------------------------
        # 10. TABLA DE PANELES SOBRANTES
        # --------------------------------------------------------

        contenido.append(
            Paragraph(
                "Paneles sobrantes",
                estilo_seccion
            )
        )

        filas_sobrantes = [

            [
                panel.id_panel,
                panel.altura_mm,
                panel.familia
            ]

            for panel in resultados["paneles_sobrantes"]

        ]

        if filas_sobrantes:

            contenido.append(
                crear_tabla(
                    [
                        "Identificador del panel",
                        "Altura (mm)",
                        "Familia"
                    ],
                    filas_sobrantes,
                    [220, 200, 220]
                )
            )

        else:

            contenido.append(
                Paragraph(
                    "No hay paneles sobrantes.",
                    estilo_celda
                )
            )

        # --------------------------------------------------------
        # 11. DIAGNOSTICO DEL INVENTARIO
        # --------------------------------------------------------

        diagnostico = resultados["diagnostico_asignacion"]

        contenido.append(Spacer(1, 12))

        contenido.append(
            Paragraph(
                "Diagnóstico de compatibilidad del inventario",
                estilo_seccion
            )
        )

        rechazos_por_orden = {
            registro["orden"]: registro.get("motivos", {})
            for registro in diagnostico["rechazos_por_posicion"]
        }

        filas_diagnostico = []

        nombres_motivos = {
            "no_disponible": "No disponible",
            "familia_incompatible": "Familia incompatible",
            "fuera_intervalo_altura": "Fuera del intervalo",
            "no_cumple_paso_altura": "No cumple el paso",
            "no_cumple_altura_inicial": "No cumple altura inicial"
        }

        for candidato in diagnostico["candidatos_por_posicion"]:

            orden = candidato["orden"]

            motivos = rechazos_por_orden.get(orden, {})

            detalles = []

            for clave, nombre in nombres_motivos.items():

                ids_rechazados = motivos.get(clave, [])

                if ids_rechazados:

                    detalles.append(
                        f"{nombre}: {', '.join(ids_rechazados)}"
                    )

            texto_candidatos = (
                ", ".join(candidato["ids_paneles_candidatos"])
                if candidato["ids_paneles_candidatos"]
                else "Ninguno"
            )

            texto_rechazos = (
                "; ".join(detalles)
                if detalles
                else "Sin rechazos"
            )

            filas_diagnostico.append([
                orden,
                candidato["id_posicion"],
                candidato["cantidad_candidatos"],
                texto_candidatos,
                texto_rechazos
            ])

        if filas_diagnostico:

            contenido.append(
                crear_tabla(
                    [
                        "Orden",
                        "Posición",
                        "Candidatos",
                        "Paneles compatibles",
                        "Motivos de rechazo"
                    ],
                    filas_diagnostico,
                    [35, 65, 75, 180, 425]
                )
            )

        else:

            contenido.append(
                Paragraph(
                    "No hay posiciones disponibles para el diagnóstico.",
                    estilo_celda
                )
            )

        # --------------------------------------------------------
        # 12. PANELES DISPONIBLES SIN COMPATIBILIDAD
        # --------------------------------------------------------

        contenido.append(
            Paragraph(
                "Paneles disponibles sin posición compatible",
                estilo_seccion
            )
        )

        paneles_sin_compatibilidad = diagnostico[
            "paneles_disponibles_sin_candidato"
        ]

        filas_sin_compatibilidad = [

            [
                panel.id_panel,
                panel.altura_mm,
                panel.familia
            ]

            for panel in paneles_sin_compatibilidad

        ]

        if filas_sin_compatibilidad:

            contenido.append(
                crear_tabla(
                    [
                        "Identificador del panel",
                        "Altura (mm)",
                        "Familia"
                    ],
                    filas_sin_compatibilidad,
                    [220, 200, 220]
                )
            )

        else:

            contenido.append(
                Paragraph(
                    "Todos los paneles disponibles tienen "
                    "compatibilidad con al menos una posición.",
                    estilo_celda
                )
            )

        # --------------------------------------------------------
        # 13. ADVERTENCIAS DE LA ASIGNACION
        # --------------------------------------------------------

        contenido.append(
            Paragraph(
                "Advertencias del procesamiento",
                estilo_seccion
            )
        )

        advertencias = resultados.get("advertencias", [])

        if advertencias:

            for advertencia in advertencias:

                contenido.append(
                    Paragraph(
                        "• " + texto_seguro(advertencia),
                        estilo_nota
                    )
                )

                contenido.append(Spacer(1, 4))

        else:

            contenido.append(
                Paragraph(
                    "No se generaron advertencias.",
                    estilo_nota
                )
            )

        # --------------------------------------------------------
        # 11. CONFIGURAR EL ENCABEZADO Y PIE DE PÁGINA
        # --------------------------------------------------------

        def dibujar_pie_pagina(canvas, documento):

            canvas.saveState()

            ancho_pagina, _alto_pagina = documento.pagesize

            canvas.setStrokeColor(
                colors.HexColor("#DCE2EA")
            )

            canvas.line(
                documento.leftMargin,
                29,
                ancho_pagina - documento.rightMargin,
                29
            )

            canvas.setFont("Helvetica", 8)

            canvas.setFillColor(
                colors.HexColor("#647386")
            )

            canvas.drawString(
                documento.leftMargin,
                17,
                "PANELMSE - Informe de asignación"
            )

            canvas.drawRightString(
                ancho_pagina - documento.rightMargin,
                17,
                f"Página {documento.page}"
            )

            canvas.restoreState()

        # --------------------------------------------------------
        # 12. GENERAR EL ARCHIVO PDF
        # --------------------------------------------------------

        documento = SimpleDocTemplate(
            str(ruta_pdf),
            pagesize=landscape(A4),
            rightMargin=30,
            leftMargin=30,
            topMargin=35,
            bottomMargin=45,
            title="Informe de asignación PANELMSE",
            author=proyecto["responsable"]
        )

        try:

            documento.build(
                contenido,
                onFirstPage=dibujar_pie_pagina,
                onLaterPages=dibujar_pie_pagina
            )

        except Exception as error:

            print(
                f"Error al generar el PDF: {error!r}"
            )

            self.status_label.configure(
                text="Estado: Error durante la generación del PDF."
            )

            messagebox.showerror(
                "Error al generar PDF",
                "No fue posible generar el informe.\n\n"
                f"Detalle: {error}",
                parent=self
            )

            return

        # --------------------------------------------------------
        # 13. CONFIRMAR LA GENERACIÓN DEL INFORME
        # --------------------------------------------------------

        self.status_label.configure(
            text="Estado: Informe PDF generado correctamente."
        )

        messagebox.showinfo(
            "PDF generado",
            "El informe de PANELMSE se generó correctamente en:\n\n"
            f"{ruta_pdf}",
            parent=self
        )
if __name__ == "__main__":

    aplicacion = PanelMSEApp()

    aplicacion.mainloop()
