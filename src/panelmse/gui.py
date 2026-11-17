
# ============================================================
# PANELMSE - STAGE 07
# BLOQUE 1: IMPORTAR LA BIBLIOTECA DE INTERFAZ
# ============================================================

# Permite manejar las rutas y los nombres de los archivos.
import csv
from datetime import datetime
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
    LongTable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Importamos la función principal de procesamiento.
from .main import procesar_archivos

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
        # FECHA DEL PROYECTO
        # Tres campos numéricos separados visualmente por guiones.
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

        # Etiquetas de los tres campos.
        for columna, texto in [
            (0, "Año"),
            (2, "Mes"),
            (4, "Día")
        ]:

            ctk.CTkLabel(
                self.fecha_frame,
                text=texto,
                font=("Arial", 11),
                text_color="#647386"
            ).grid(
                row=0,
                column=columna
            )

        # Campo del año: máximo cuatro números.
        self.fecha_anio_entry = ctk.CTkEntry(
            self.fecha_frame,
            width=85,
            height=35,
            validate="key",
            validatecommand=(
                self.register(self.validar_anio),
                "%P"
            )
        )

        self.fecha_anio_entry.grid(
            row=1,
            column=0,
            padx=(0, 5)
        )

        # Primer guion.
        ctk.CTkLabel(
            self.fecha_frame,
            text="-",
            font=("Arial", 16, "bold")
        ).grid(
            row=1,
            column=1,
            padx=5
        )

        # Campo del mes: máximo dos números.
        self.fecha_mes_entry = ctk.CTkEntry(
            self.fecha_frame,
            width=55,
            height=35,
            validate="key",
            validatecommand=(
                self.register(self.validar_dos_digitos),
                "%P"
            )
        )

        self.fecha_mes_entry.grid(
            row=1,
            column=2,
            padx=5
        )

        # Segundo guion.
        ctk.CTkLabel(
            self.fecha_frame,
            text="-",
            font=("Arial", 16, "bold")
        ).grid(
            row=1,
            column=3,
            padx=5
        )

        # Campo del día: máximo dos números.
        self.fecha_dia_entry = ctk.CTkEntry(
            self.fecha_frame,
            width=55,
            height=35,
            validate="key",
            validatecommand=(
                self.register(self.validar_dos_digitos),
                "%P"
            )
        )

        self.fecha_dia_entry.grid(
            row=1,
            column=4,
            padx=(5, 0)
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
            row=4,
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
            row=4,
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

        except Exception as error:

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
# BLOQUE: SELECCIONAR EL ARCHIVO DE PANELES
# Abre el explorador y guarda la ruta del CSV seleccionado.
# ============================================================
  
    # ============================================================
    # MÉTODO: REGISTRAR PROYECTO
    # Valida y guarda la identificación del proyecto.
    # ============================================================

    def registrar_proyecto(self):

        # --------------------------------------------------------
        # 1. Obtener los datos escritos por el usuario.
        # --------------------------------------------------------

        responsable = self.responsable_entry.get().strip()
        nombre_proyecto = self.nombre_proyecto_entry.get().strip()

        anio = self.fecha_anio_entry.get()
        mes = self.fecha_mes_entry.get()
        dia = self.fecha_dia_entry.get()

        # --------------------------------------------------------
        # 2. Comprobar que ningún campo esté vacío.
        # --------------------------------------------------------

        if not responsable or not nombre_proyecto or not anio or not mes or not dia:

            messagebox.showwarning(
                "Datos incompletos",
                "Debes completar todos los campos del proyecto.",
                parent=self
            )
            return

        # --------------------------------------------------------
        # 3. Validar que el año tenga cuatro números.
        # --------------------------------------------------------

        if len(anio) != 4:

            messagebox.showwarning(
                "Año incorrecto",
                "El año debe contener exactamente cuatro números.",
                parent=self
            )
            return

        # --------------------------------------------------------
        # 4. Construir y validar la fecha completa.
        # --------------------------------------------------------

        fecha_texto = f"{anio}-{mes.zfill(2)}-{dia.zfill(2)}"

        try:

            fecha_validada = datetime.strptime(
                fecha_texto,
                "%Y-%m-%d"
            )

        except ValueError:

            messagebox.showwarning(
                "Fecha incorrecta",
                "La fecha introducida no existe.\n\n"
                "Comprueba el año, el mes y el día.",
                parent=self
            )
            return

        # --------------------------------------------------------
        # 5. Guardar la información del proyecto.
        # --------------------------------------------------------

        self.datos_proyecto = {
            "responsable": responsable,
            "nombre_proyecto": nombre_proyecto,
            "fecha": fecha_validada.strftime("%Y-%m-%d")
        }

        # --------------------------------------------------------
        # 6. Bloquear los campos para evitar cambios accidentales.
        # --------------------------------------------------------

        self.responsable_entry.configure(state="disabled")
        self.nombre_proyecto_entry.configure(state="disabled")

        self.fecha_anio_entry.configure(state="disabled")
        self.fecha_mes_entry.configure(state="disabled")
        self.fecha_dia_entry.configure(state="disabled")

        # --------------------------------------------------------
        # 7. Habilitar la selección de archivos CSV.
        # --------------------------------------------------------

        self.paneles_button.configure(state="normal")
        self.posiciones_button.configure(state="normal")

        self.project_button.configure(
            text="Modificar datos del proyecto",
            command=self.habilitar_edicion_proyecto
        )

        # --------------------------------------------------------
        # 8. Actualizar los mensajes de la interfaz.
        # --------------------------------------------------------

        self.project_status_label.configure(
            text="Estado: Proyecto registrado correctamente.",
            text_color="#16845B"
        )

        self.actualizar_estado_archivos()

        messagebox.showinfo(
            "Registro completado",
            "La información del proyecto se registró correctamente.\n\n"
            "Ya puedes seleccionar los archivos CSV.",
            parent=self
        )


    def habilitar_edicion_proyecto(self):

        confirmar = messagebox.askyesno(
            "Modificar proyecto",
            "¿Deseas modificar los datos del proyecto?\n\n"
            "Se eliminarán los resultados calculados anteriormente.",
            parent=self
        )

        if not confirmar:
            return

        # Eliminar los resultados anteriores.
        self.resultados_actuales = None

        self.actualizar_vista_resultados()

        # Permitir modificar los campos.
        self.responsable_entry.configure(state="normal")

        self.nombre_proyecto_entry.configure(state="normal")

        self.fecha_anio_entry.configure(state="normal")

        self.fecha_mes_entry.configure(state="normal")

        self.fecha_dia_entry.configure(state="normal")

        # Deshabilitar la selección mientras se modifica el registro.
        self.paneles_button.configure(state="disabled")

        self.posiciones_button.configure(state="disabled")

        self.calculate_button.configure(state="disabled")

        # Restaurar el botón de confirmación.
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

            respuesta = procesar_archivos(
                self.ruta_paneles,
                self.ruta_posiciones
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
            self.tabla_sobrantes
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
        # 6. Preparar el resumen general.
        # --------------------------------------------------------

        filas_resumen = [{

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
            "Los cinco archivos CSV se guardaron correctamente en:\n\n"
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
                        "Posición",
                        "Ubicación",
                        "Panel",
                        "Altura panel (mm)",
                        "Cota apoyo (mm)",
                        "Cota superior (mm)"
                    ],
                    filas_asignaciones,
                    [75, 155, 75, 125, 125, 200]
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
                        "Posición",
                        "Ubicación",
                        "Cota apoyo (mm)",
                        "Altura mínima (mm)",
                        "Altura máxima (mm)",
                        "Familia admitida"
                    ],
                    filas_pendientes,
                    [75, 150, 120, 125, 125, 160]
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
