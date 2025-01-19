import os
import threading
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog, colorchooser
import whisper
from moviepy.config import change_settings
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.VideoClip import ImageClip
from googletrans import Translator
import tempfile
import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Variable global para selección de idioma (0: Español, 1: Inglés, 2: Chino)
lenguajeSelect = 0
# Diccionario de textos en diferentes idiomas
APP_TEXTS = {
    # Español
    0: {
        'TEXT_LOAD_VIDEO': "Cargar video",
        'TEXT_SAVE_WORKFLOW': "Guardar workflow",
        'TEXT_SUBTITLE_CONFIG': "Configuracion de subtitulos",
        'TEXT_ADD_SUBTITLE': "Agregar subtitulo",
        'TEXT_LANGUAGE': "Idioma",
        'TEXT_LANGUAGE_N': "idioma {}",
        'TEXT_COLOR': "Color",
        'TEXT_SIZE': "Tamaño",
        'TEXT_Y_POSITION': "Posicion Y",
        'TEXT_OPEN_PREVIEW': "Abrir previsualizador",
        'TEXT_GENERATE_SUBTITLES': "Generar subtitulos",
        'TEXT_RESOLUTION': "Resolucion",
        'TEXT_UPDATE': "Actualizar",
        'TEXT_NO_VIDEO': "No hay video cargado",
        'TEXT_RESOLUTION_LABEL': "Resolución: ",
        'TEXT_SIZE_LABEL': "Tamaño: ",
        'TEXT_DURATION_LABEL': "Duración: ",
        'TEXT_BORDER_COLOR': "Color del borde",
        'TEXT_BORDER_SIZE': "Tamaño del borde",
        'TEXT_GENERATE_VIDEO': "Generar video"
    },
    # English
    1: {
        'TEXT_LOAD_VIDEO': "Load video",
        'TEXT_SAVE_WORKFLOW': "Save workflow",
        'TEXT_SUBTITLE_CONFIG': "Subtitle configuration",
        'TEXT_ADD_SUBTITLE': "Add subtitle",
        'TEXT_LANGUAGE': "Language",
        'TEXT_LANGUAGE_N': "language {}",
        'TEXT_COLOR': "color",
        'TEXT_SIZE': "size",
        'TEXT_Y_POSITION': "Y Position",
        'TEXT_OPEN_PREVIEW': "Open preview",
        'TEXT_GENERATE_SUBTITLES': "generate subtitles",
        'TEXT_RESOLUTION': "resolution",
        'TEXT_UPDATE': "Update",
        'TEXT_NO_VIDEO': "No video loaded",
        'TEXT_RESOLUTION_LABEL': "Resolution: ",
        'TEXT_SIZE_LABEL': "Size: ",
        'TEXT_DURATION_LABEL': "Duration: ",
        'TEXT_BORDER_COLOR': "Border color",
        'TEXT_BORDER_SIZE': "Border size",
        'TEXT_GENERATE_VIDEO': "Generate video"
    },
    # Chinese
    2: {
        'TEXT_LOAD_VIDEO': "加载视频",
        'TEXT_SAVE_WORKFLOW': "保存工作流程",
        'TEXT_SUBTITLE_CONFIG': "字幕配置",
        'TEXT_ADD_SUBTITLE': "添加字幕",
        'TEXT_LANGUAGE': "语言",
        'TEXT_LANGUAGE_N': "语言 {}",
        'TEXT_COLOR': "颜色",
        'TEXT_SIZE': "大小",
        'TEXT_Y_POSITION': "Y位置",
        'TEXT_OPEN_PREVIEW': "打开预览",
        'TEXT_GENERATE_SUBTITLES': "生成字幕",
        'TEXT_RESOLUTION': "分辨率",
        'TEXT_UPDATE': "更新",
        'TEXT_NO_VIDEO': "未加载视频",
        'TEXT_RESOLUTION_LABEL': "分辨率：",
        'TEXT_SIZE_LABEL': "大小：",
        'TEXT_DURATION_LABEL': "持续时间：",
        'TEXT_BORDER_COLOR': "边框颜色",
        'TEXT_BORDER_SIZE': "边框大小",
        'TEXT_GENERATE_VIDEO': "生成视频"
    }
}

def initialize_interface_texts():
    """Inicializa los textos de la interfaz según el idioma seleccionado"""
    global TEXT_LOAD_VIDEO, TEXT_SAVE_WORKFLOW, TEXT_SUBTITLE_CONFIG, TEXT_ADD_SUBTITLE
    global TEXT_LANGUAGE, TEXT_LANGUAGE_N, TEXT_COLOR, TEXT_SIZE, TEXT_Y_POSITION
    global TEXT_OPEN_PREVIEW, TEXT_GENERATE_SUBTITLES, TEXT_RESOLUTION, TEXT_UPDATE
    global TEXT_NO_VIDEO, TEXT_RESOLUTION_LABEL, TEXT_SIZE_LABEL, TEXT_DURATION_LABEL
    global TEXT_BORDER_COLOR, TEXT_BORDER_SIZE, TEXT_GENERATE_VIDEO
    
    selected_texts = APP_TEXTS[lenguajeSelect]
    
    TEXT_LOAD_VIDEO = selected_texts['TEXT_LOAD_VIDEO']
    TEXT_SAVE_WORKFLOW = selected_texts['TEXT_SAVE_WORKFLOW']
    TEXT_SUBTITLE_CONFIG = selected_texts['TEXT_SUBTITLE_CONFIG']
    TEXT_ADD_SUBTITLE = selected_texts['TEXT_ADD_SUBTITLE']
    TEXT_LANGUAGE = selected_texts['TEXT_LANGUAGE']
    TEXT_LANGUAGE_N = selected_texts['TEXT_LANGUAGE_N']
    TEXT_COLOR = selected_texts['TEXT_COLOR']
    TEXT_SIZE = selected_texts['TEXT_SIZE']
    TEXT_Y_POSITION = selected_texts['TEXT_Y_POSITION']
    TEXT_OPEN_PREVIEW = selected_texts['TEXT_OPEN_PREVIEW']
    TEXT_GENERATE_SUBTITLES = selected_texts['TEXT_GENERATE_SUBTITLES']
    TEXT_RESOLUTION = selected_texts['TEXT_RESOLUTION']
    TEXT_UPDATE = selected_texts['TEXT_UPDATE']
    TEXT_NO_VIDEO = selected_texts['TEXT_NO_VIDEO']
    TEXT_RESOLUTION_LABEL = selected_texts['TEXT_RESOLUTION_LABEL']
    TEXT_SIZE_LABEL = selected_texts['TEXT_SIZE_LABEL']
    TEXT_DURATION_LABEL = selected_texts['TEXT_DURATION_LABEL']
    TEXT_BORDER_COLOR = selected_texts['TEXT_BORDER_COLOR']
    TEXT_BORDER_SIZE = selected_texts['TEXT_BORDER_SIZE']
    TEXT_GENERATE_VIDEO = selected_texts['TEXT_GENERATE_VIDEO']

# Inicializar los textos al cargar el módulo
initialize_interface_texts()

# Global Settings
MAIN_WINDOW_WIDTH = 500
MAIN_WINDOW_HEIGHT = 600

# Preview window settings (percentage of screen size)
PREVIEW_WINDOW_SCREEN_RATIO = 0.6  # 60% del tamaño de la pantalla

# Subtitle positioning and styling
SUBTITLE_Y_MARGIN = -200  # Margen en píxeles para los subtítulos
SUBTITLE_DEFAULT_FONTSIZE = 35
SUBTITLE_MIN_FONTSIZE = 20
SUBTITLE_MAX_FONTSIZE = 100
SLIDER_WIDTH = 200  # Ancho de los sliders en píxeles

# Font size scaling factors
PREVIEW_FONT_SCALE = 1.0  # Factor de escala para la previsualización
VIDEO_FONT_SCALE = 1.5    # Factor de escala para el video final

# Configure MoviePy to use ImageMagick
change_settings({"IMAGEMAGICK_BINARY": "magick"})

# Diccionario de frases de ejemplo en diferentes idiomas
SAMPLE_TEXTS = {
    'Afrikaans': "Dit is 'n toetssin",
    'Arabic': "هذه جملة اختبار",
    'Armenian': "Սա փորձարկման նախադասություն է",
    'Azerbaijani': "Bu bir test cümləsidir",
    'Belarusian': "Гэта тэставае сказ",
    'Bosnian': "Ovo je testna rečenica",
    'Bulgarian': "Това е тестово изречение",
    'Catalan': "Aquesta és una frase de prova",
    'Chinese': "这是一个测试句子",
    'Croatian': "Ovo je testna rečenica",
    'Czech': "Toto je testovací věta",
    'Danish': "Dette er en testsætning",
    'Dutch': "Dit is een testzin",
    'English': "This is a test sentence",
    'Estonian': "See on testlause",
    'Finnish': "Tämä on testilause",
    'French': "C'est une phrase de test",
    'Galician': "Esta é unha frase de proba",
    'German': "Dies ist ein Testsatz",
    'Greek': "Αυτή είναι μια δοκιμαστική πρόταση",
    'Hebrew': "זהו משפט בדיקה",
    'Hindi': "यह एक परीक्षण वाक्य है",
    'Hungarian': "Ez egy tesztmondat",
    'Icelandic': "Þetta er prófsetning",
    'Indonesian': "Ini adalah kalimat tes",
    'Italian': "Questa è una frase di prova",
    'Japanese': "これはテストの文章です",
    'Kannada': "ಇದು ಪರೀಕ್ಷಾ ವಾಕ್ಯ",
    'Kazakh': "Бұл сынақ сөйлем",
    'Korean': "이것은 테스트 문장입니다",
    'Latvian': "Šis ir testa teikums",
    'Lithuanian': "Tai yra bandomasis sakinys",
    'Macedonian': "Ова е тест реченица",
    'Malay': "Ini adalah ayat ujian",
    'Marathi': "ही एक चाचणी वाक्य आहे",
    'Maori': "He rerenga whakamātautau tēnei",
    'Nepali': "यो एक परीक्षण वाक्य हो",
    'Norwegian': "Dette er en testsetning",
    'Persian': "این یک جمله آزمایشی است",
    'Polish': "To jest zdanie testowe",
    'Portuguese': "Esta é uma frase de teste",
    'Romanian': "Aceasta este o propoziție de test",
    'Russian': "Это тестовое предложение",
    'Serbian': "Ово је тестна реченица",
    'Slovak': "Toto je testovacia veta",
    'Slovenian': "To je testni stavek",
    'Spanish': "Esta es una frase de prueba",
    'Swahili': "Hii ni sentensi ya majaribio",
    'Swedish': "Detta är en testmening",
    'Tagalog': "Ito ay isang pangsubok na pangungusap",
    'Tamil': "இது ஒரு சோதனை வாக்கியம்",
    'Thai': "นี่คือประโยคทดสอบ",
    'Turkish': "Bu bir test cümlesidir",
    'Ukrainian': "Це тестове речення",
    'Urdu': "یہ ایک ٹیسٹ جملہ ہے",
    'Vietnamese': "Đây là một câu thử nghiệm",
    'Welsh': "Mae hon yn frawddeg prawf"
}

# Resoluciones comunes de video
COMMON_RESOLUTIONS = [
    "3840x2160 (4K UHD)",
    "2560x1440 (2K QHD)",
    "1920x1080 (Full HD)",
    "1280x720 (HD)",
    "854x480 (480p)",
    "640x360 (360p)",
    "Custom"
]

def format_timecode(seconds):
    """Convert seconds to SRT timecode format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def create_text_clip(text, size, duration, font_path, font_size=35, color='white', border_color='black', border_size=2):
    """Create a text clip using PIL for better CJK support"""
    # Create a temporary PIL image
    w, h = size
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        # Fallback to default font if custom font fails
        font = ImageFont.load_default()
    
    # Calculate maximum width for text (80% of video width)
    max_width = int(w * 0.8)
    
    # Function to wrap text
    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            # Check width with current word added
            test_line = current_line + " " + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)
        return lines

    # For Chinese text, wrap by characters if needed
    def wrap_chinese_text(text, font, max_width):
        lines = []
        current_line = ""
        
        for char in text:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        return lines

    # Determine if text contains Chinese characters
    def has_chinese(text):
        return any('\u4e00' <= char <= '\u9fff' for char in text)
    
    # Wrap text based on language
    if has_chinese(text):
        lines = wrap_chinese_text(text, font, max_width)
    else:
        lines = wrap_text(text, font, max_width)
    
    # Calculate total height needed for all lines
    line_spacing = font_size * 1.2
    total_height = len(lines) * line_spacing
    
    # Draw each line centered
    y = h - total_height - 40  # 40 pixels from bottom
    for line in lines:
        # Get line width for centering
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (w - text_width) // 2
        
        # Draw the border by offsetting text in multiple directions
        if border_size > 0:
            for dx in range(-border_size, border_size + 1):
                for dy in range(-border_size, border_size + 1):
                    if dx != 0 or dy != 0:  # Skip the center position
                        draw.text((x + dx, y + dy), line, font=font, fill=border_color)
        
        # Draw the main text
        draw.text((x, y), line, font=font, fill=color)
        y += line_spacing
    
    # Convert to numpy array
    return np.array(img)

class PreviewWindow(ctk.CTkToplevel):
    def __init__(self, master, subtitle_configs):
        super().__init__(master)
        
        self.title("Previsualizador de Subtítulos")
        self.subtitle_configs = subtitle_configs
        
        # Default resolution - check if master has video resolution
        if hasattr(master, 'video_resolution') and master.video_resolution:
            width, height = master.video_resolution
        else:
            width, height = 1920, 1080  # Default if no video loaded
            
        self.width_var = ctk.StringVar(value=str(width))
        self.height_var = ctk.StringVar(value=str(height))
        
        # Set window size based on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate window size (60% of screen)
        window_width = int(screen_width * PREVIEW_WINDOW_SCREEN_RATIO)
        window_height = int(screen_height * PREVIEW_WINDOW_SCREEN_RATIO)
        
        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Inicializar canvas como None
        self.canvas = None
        
        # Variable para controlar la actualización automática
        self.auto_update = True
        
        # Crear widgets después de que la ventana esté configurada
        self.create_widgets()
        
        # Esperar a que la ventana esté completamente creada antes de actualizar el preview
        self.after(200, self.initial_update)
        
        # Bind resize event
        self.bind("<Configure>", self.on_window_resize)
        
        # Iniciar actualización automática
        self.start_auto_update()

    def on_window_resize(self, event):
        """Llamado cuando se redimensiona la ventana"""
        self.update_preview()
    
    def start_auto_update(self):
        """Actualiza en cada frame usando el sistema de eventos de Tkinter"""
        if self.auto_update:
            self.update_preview()
            # Solicitar la próxima actualización tan pronto como sea posible
            self.update_idletasks()
            self.after(1, self.start_auto_update)
    
    def stop_auto_update(self):
        """Detiene la actualización automática"""
        self.auto_update = False
    
    def on_close(self):
        """Llamado cuando se cierra la ventana"""
        self.stop_auto_update()
        self.destroy()
    
    def initial_update(self):
        """Actualización inicial después de que la ventana esté completamente creada"""
        if not self.canvas:
            self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="black", highlightthickness=0)
            self.canvas.pack(fill="both", expand=True)
        self.update_preview()
    
    def create_widgets(self):
        # Resolution controls
        resolution_frame = ctk.CTkFrame(self)
        resolution_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        resolution_label = ctk.CTkLabel(resolution_frame, text=TEXT_RESOLUTION+":")
        resolution_label.pack(side="left", padx=5)
        
        self.width_entry = ctk.CTkEntry(resolution_frame, textvariable=self.width_var, width=60)
        self.width_entry.pack(side="left", padx=2)
        
        x_label = ctk.CTkLabel(resolution_frame, text="x")
        x_label.pack(side="left", padx=2)
        
        self.height_entry = ctk.CTkEntry(resolution_frame, textvariable=self.height_var, width=60)
        self.height_entry.pack(side="left", padx=2)
        
        update_btn = ctk.CTkButton(
            resolution_frame,
            text=TEXT_UPDATE,
            command=self.update_resolution,
            width=100
        )
        update_btn.pack(side="left", padx=5)
        
        # Preview canvas frame
        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    def safe_update_preview(self):
        """Método seguro para actualizar la vista previa"""
        try:
            self.update_preview()
        except Exception as e:
            print(f"Error al actualizar preview: {str(e)}")
            # Recrear el canvas si es necesario
            if not self.canvas or not self.canvas.winfo_exists():
                self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="black", highlightthickness=0)
                self.canvas.pack(fill="both", expand=True)
    
    def update_preview(self):
        """Actualiza la vista previa del video"""
        if not self.canvas or not self.canvas.winfo_exists():
            self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="black", highlightthickness=0)
            self.canvas.pack(fill="both", expand=True)
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Get canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Get video dimensions
        video_width = int(self.width_var.get())
        video_height = int(self.height_var.get())
        
        # Draw black background and preview area
        self.update_canvas_size()
        
        # Get system fonts directory
        system_fonts_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
        
        # Create preview text for each subtitle configuration
        for config in self.subtitle_configs:
            # Get configuration
            config_data = config.get_config()
            language = config_data['language']
            color = config_data['color']
            font_size = config_data['font_size']
            y_position = config_data['y_position']
            border_color = config_data['border_color']
            border_size = config_data['border_size']
            
            # Get appropriate font for language
            language_name = language.split(' (')[0]  # Remove parentheses part
            if language_name in ['Chinese', 'Japanese', 'Korean']:
                possible_fonts = ['MSYH.TTC', 'SIMHEI.TTF', 'SIMSUN.TTC', 'MALGUN.TTF', 'MEIRYO.TTC']
            elif language_name in ['Arabic', 'Hebrew']:
                possible_fonts = ['ARIAL.TTF']
            else:
                possible_fonts = ['ARIAL.TTF', 'SEGOEUI.TTF']
            
            font_path = None
            for font in possible_fonts:
                temp_path = os.path.join(system_fonts_dir, font)
                if os.path.exists(temp_path):
                    font_path = temp_path
                    break
            
            if not font_path:
                font_path = 'Arial'
            
            # Create sample text based on language
            text = SAMPLE_TEXTS.get(language_name, "This is a sample text")
            
            # Calculate Y position
            margin = SUBTITLE_Y_MARGIN * (canvas_height / video_height)  # Scale margin according to preview size
            y = (canvas_height - margin) * (1 - y_position / 100) + margin
            
            # Scale font size according to preview size vs video size
            scale_factor = (canvas_height / video_height)  # Use height as reference
            scaled_font_size = int(font_size * scale_factor)
            scaled_border_size = int(border_size * scale_factor)
            
            # Draw border by creating multiple offset text items
            if border_size > 0:
                for dx in range(-scaled_border_size, scaled_border_size + 1):
                    for dy in range(-scaled_border_size, scaled_border_size + 1):
                        if dx != 0 or dy != 0:  # Skip the center position
                            self.canvas.create_text(
                                canvas_width / 2 + dx,  # Center horizontally + offset
                                y + dy,  # Y position + offset
                                text=text,
                                fill=border_color,
                                font=("Arial", scaled_font_size),
                                anchor="s"  # Bottom anchor
                            )
            
            # Create text on canvas (main text on top of border)
            self.canvas.create_text(
                canvas_width / 2,  # Center horizontally
                y,
                text=text,
                fill=color,
                font=("Arial", scaled_font_size),
                anchor="s"  # Bottom anchor
            )
    
    def on_resolution_change(self, choice):
        # Si es una resolución predefinida, usar esos valores
        if choice in self.resolutions and self.resolutions[choice]:
            width, height = self.resolutions[choice]
            self.width_var.set(str(width))
            self.height_var.set(str(height))
        # Si es Custom, mantener los valores actuales
        self.update_resolution()
    
    def set_resolution(self, width, height):
        # Find matching common resolution or set to custom
        resolution = f"{width}x{height}"
        found = False
        for res in self.resolutions:
            if res.startswith(resolution):
                self.resolution_var.set(res)
                found = True
                break
        if not found:
            self.resolution_var.set("Custom")
            self.width_var.set(str(width))
            self.height_var.set(str(height))
            self.custom_frame.pack(side="left", padx=5)
        self.update_preview()

    def update_resolution(self):
        try:
            self.update_preview()
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos para la resolución")
    
    def update_canvas_size(self):
        try:
            if not self.canvas or not isinstance(self.canvas, ctk.CTkCanvas):
                self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="black", highlightthickness=0)
                self.canvas.pack(fill="both", expand=True)
            
            # Get current frame size
            frame_width = self.canvas_frame.winfo_width()
            frame_height = self.canvas_frame.winfo_height()
            
            if frame_width > 1 and frame_height > 1:  # Asegurarse de que el tamaño sea válido
                # Clear canvas
                self.canvas.delete("all")
                
                # Draw black background
                self.canvas.create_rectangle(0, 0, frame_width, frame_height, fill="black")
                
                # Get video dimensions
                try:
                    width = int(self.width_var.get())
                    height = int(self.height_var.get())
                except ValueError:
                    return
                
                # Calculate aspect ratio
                video_ratio = width / height
                frame_ratio = frame_width / frame_height
                
                if frame_ratio > video_ratio:
                    # Frame is wider than video
                    new_height = frame_height
                    new_width = int(frame_height * video_ratio)
                else:
                    # Frame is taller than video
                    new_width = frame_width
                    new_height = int(frame_width / video_ratio)
                
                # Calculate position to center the preview
                x = (frame_width - new_width) // 2
                y = (frame_height - new_height) // 2
                
                # Draw preview area
                self.canvas.create_rectangle(x, y, x + new_width, y + new_height, outline="white")
        except Exception as e:
            print(f"Error al actualizar canvas: {str(e)}")
            # Recrear el canvas si hay error
            self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="black", highlightthickness=0)
            self.canvas.pack(fill="both", expand=True)

class SubtitleConfigFrame(ctk.CTkFrame):
    def __init__(self, master, available_languages, available_colors, index, delete_callback):
        super().__init__(master)
        self.configure(fg_color="#E0E0E0")
        self.grid(row=index, column=0, padx=20, pady=10, sticky="ew")
        self.index = index

        # Container principal centrado
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        main_container.grid_columnconfigure(0, weight=1)

        # Header con título y botón de eliminar
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(5,10))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(header_frame, text=TEXT_LANGUAGE_N.format(index + 1), font=("Segoe UI", 12, "bold"))
        title_label.grid(row=0, column=0, sticky="w", padx=5)

        self.delete_btn = ctk.CTkButton(
            header_frame,
            text="✕",
            command=lambda: delete_callback(self.index),
            width=30,
            height=24
        )
        self.delete_btn.grid(row=0, column=1)

        # Contenedor para los controles
        controls_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        controls_frame.grid_columnconfigure(1, weight=1)

        # Language selection
        language_label = ctk.CTkLabel(controls_frame, text=TEXT_LANGUAGE+":", anchor="e", width=120)
        language_label.grid(row=0, column=0, padx=(0,10), pady=5, sticky="e")
        
        self.language_var = ctk.StringVar(value=available_languages[0])
        self.language_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=available_languages,
            variable=self.language_var,
            command=self.on_config_change,
            width=280
        )
        self.language_menu.grid(row=0, column=1, pady=5, sticky="ew")

        # Color selection
        color_label = ctk.CTkLabel(controls_frame, text=TEXT_COLOR+":", anchor="e", width=120)
        color_label.grid(row=1, column=0, padx=(0,10), pady=5, sticky="e")
        
        self.color_var = ctk.StringVar(value="#FFFFFF")
        self.color_button = ctk.CTkButton(
            controls_frame,
            text="",
            width=280,
            height=30,
            fg_color=self.color_var.get(),
            command=self.choose_color
        )
        self.color_button.grid(row=1, column=1, pady=5, sticky="ew")

        # Font size
        fontsize_label = ctk.CTkLabel(controls_frame, text=TEXT_SIZE+":", anchor="e", width=120)
        fontsize_label.grid(row=2, column=0, padx=(0,10), pady=5, sticky="e")
        
        self.fontsize_var = ctk.IntVar(value=SUBTITLE_DEFAULT_FONTSIZE)
        self.fontsize_slider = ctk.CTkSlider(
            controls_frame,
            from_=SUBTITLE_MIN_FONTSIZE,
            to=SUBTITLE_MAX_FONTSIZE,
            number_of_steps=SUBTITLE_MAX_FONTSIZE - SUBTITLE_MIN_FONTSIZE,
            variable=self.fontsize_var,
            command=self.on_config_change,
            width=280
        )
        self.fontsize_slider.grid(row=2, column=1, pady=5, sticky="ew")

        # Y position
        ypos_label = ctk.CTkLabel(controls_frame, text=TEXT_Y_POSITION+":", anchor="e", width=120)
        ypos_label.grid(row=3, column=0, padx=(0,10), pady=5, sticky="e")
        
        self.ypos_var = ctk.IntVar(value=40)
        self.ypos_slider = ctk.CTkSlider(
            controls_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            variable=self.ypos_var,
            command=self.on_config_change,
            width=280
        )
        self.ypos_slider.grid(row=3, column=1, pady=5, sticky="ew")

        # Border color
        border_color_label = ctk.CTkLabel(controls_frame, text=TEXT_BORDER_COLOR+":", anchor="e", width=120)
        border_color_label.grid(row=4, column=0, padx=(0,10), pady=5, sticky="e")
        
        self.border_color_var = ctk.StringVar(value="#000000")
        self.border_color_button = ctk.CTkButton(
            controls_frame,
            text="",
            width=280,
            height=30,
            fg_color=self.border_color_var.get(),
            command=self.choose_border_color
        )
        self.border_color_button.grid(row=4, column=1, pady=5, sticky="ew")

        # Border size
        border_size_label = ctk.CTkLabel(controls_frame, text=TEXT_BORDER_SIZE+":", anchor="e", width=120)
        border_size_label.grid(row=5, column=0, padx=(0,10), pady=5, sticky="e")
        
        self.border_size_var = ctk.IntVar(value=2)
        self.border_size_slider = ctk.CTkSlider(
            controls_frame,
            from_=0,
            to=5,
            number_of_steps=50,
            variable=self.border_size_var,
            command=self.on_config_change,
            width=280
        )
        self.border_size_slider.grid(row=5, column=1, pady=5, sticky="ew")
    
    def get_config(self):
        return {
            "language": self.language_var.get(),
            "color": self.color_var.get(),
            "font_size": self.fontsize_var.get(),
            "y_position": self.ypos_var.get(),
            "border_color": self.border_color_var.get(),
            "border_size": self.border_size_var.get()
        }

    def choose_color(self):
        color = colorchooser.askcolor(color=self.color_var.get(), title="Elegir color del subtítulo")
        if color[1]:  # color[1] contains the hex value
            self.color_var.set(color[1])
            self.color_button.configure(fg_color=color[1])
            self.on_config_change()

    def choose_border_color(self):
        color = colorchooser.askcolor(color=self.border_color_var.get(), title="Elegir color del borde")
        if color[1]:  # color[1] contains the hex value
            self.border_color_var.set(color[1])
            self.border_color_button.configure(fg_color=color[1])
            self.on_config_change()

    def on_config_change(self, *args):
        """Called when any configuration changes"""
        if self.master and hasattr(self.master, 'preview_window'):
            self.master.preview_window.update_preview()

class SubtitleGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sub Bridge - Generador de Subtítulos")
        self.geometry(f"{MAIN_WINDOW_WIDTH}x{MAIN_WINDOW_HEIGHT}")
        self.video_path = None  # Para almacenar el path del video
        self.video_resolution = None  # Para almacenar la resolución del video
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Diccionario para el selector de idiomas
        self.language_options = {
            "Español": 0,
            "English": 1,
            "中文": 2
        }
        
        # Available languages
        self.available_languages = {
            'Afrikaans': 'af',
            'Arabic': 'ar',
            'Armenian': 'hy',
            'Azerbaijani': 'az',
            'Belarusian': 'be',
            'Bosnian': 'bs',
            'Bulgarian': 'bg',
            'Catalan': 'ca',
            'Chinese': 'zh-cn',
            'Croatian': 'hr',
            'Czech': 'cs',
            'Danish': 'da',
            'Dutch': 'nl',
            'English': 'en',
            'Estonian': 'et',
            'Finnish': 'fi',
            'French': 'fr',
            'Galician': 'gl',
            'German': 'de',
            'Greek': 'el',
            'Hebrew': 'he',
            'Hindi': 'hi',
            'Hungarian': 'hu',
            'Icelandic': 'is',
            'Indonesian': 'id',
            'Italian': 'it',
            'Japanese': 'ja',
            'Kannada': 'kn',
            'Kazakh': 'kk',
            'Korean': 'ko',
            'Latvian': 'lv',
            'Lithuanian': 'lt',
            'Macedonian': 'mk',
            'Malay': 'ms',
            'Marathi': 'mr',
            'Maori': 'mi',
            'Nepali': 'ne',
            'Norwegian': 'no',
            'Persian': 'fa',
            'Polish': 'pl',
            'Portuguese': 'pt',
            'Romanian': 'ro',
            'Russian': 'ru',
            'Serbian': 'sr',
            'Slovak': 'sk',
            'Slovenian': 'sl',
            'Spanish': 'es',
            'Swahili': 'sw',
            'Swedish': 'sv',
            'Tagalog': 'tl',
            'Tamil': 'ta',
            'Thai': 'th',
            'Turkish': 'tr',
            'Ukrainian': 'uk',
            'Urdu': 'ur',
            'Vietnamese': 'vi',
            'Welsh': 'cy'
        }
        
        # Color options
        self.available_colors = {
            'Blanco': '#FFFFFF',
            'Amarillo': '#FFFF00',
            'Verde': '#00FF00',
            'Rojo': '#FF0000',
            'Azul': '#0000FF'
        }
        
        # Create widgets
        self.create_widgets()
        
        # Initialize subtitle configs
        self.subtitle_configs = []
        self.add_subtitle_config()  # Add initial config
        
        # Refresh workflows list
        self.refresh_workflows()
    
    def add_subtitle_config(self):
        config_frame = SubtitleConfigFrame(
            self.subtitle_container,
            list(self.available_languages.keys()),
            list(self.available_colors.keys()),
            len(self.subtitle_configs),
            self.delete_subtitle_config
        )
        config_frame.grid(row=len(self.subtitle_configs), column=0, padx=10, pady=5)
        self.subtitle_configs.append(config_frame)
    
    def delete_subtitle_config(self, index):
        if len(self.subtitle_configs) > 1:  # Mantener al menos un subtítulo
            self.subtitle_configs[index].destroy()
            self.subtitle_configs.pop(index)
            # Reordenar los índices
            for i, config in enumerate(self.subtitle_configs):
                config.index = i
                config.grid(row=i, column=0, padx=10, pady=5)
    
    def load_video(self):
        # Close preview window if it exists
        if hasattr(self, 'preview_window') and self.preview_window.winfo_exists():
            self.preview_window.destroy()
            delattr(self, 'preview_window')
        
        filetypes = (
            ('Archivos de video', '*.mp4 *.avi *.mkv *.mov'),
            ('Todos los archivos', '*.*')
        )
        
        video_path = filedialog.askopenfilename(
            title='Selecciona un video',
            filetypes=filetypes
        )
        
        if video_path:
            try:
                self.video_path = video_path
                # Load video to get dimensions
                clip = VideoFileClip(video_path)
                width, height = clip.size
                self.video_resolution = (width, height)
                
                # Mostrar información del video en consola
                print("\n=== Información del Video ===")
                print(f"Directorio: {os.path.dirname(video_path)}")
                print(f"Archivo: {os.path.basename(video_path)}")
                print(f"Resolución: {width}x{height}")
                print(f"Duración: {clip.duration:.2f} segundos")
                print("==========================\n")
                
                # Update video label with filename
                self.video_label.configure(text=f"Video: {os.path.basename(video_path)}")
                
                # Update video info labels
                self.resolution_label.configure(text=f"{TEXT_RESOLUTION_LABEL}{width}x{height}")
                self.size_label.configure(text=f"{TEXT_SIZE_LABEL}{os.path.getsize(video_path) / (1024 * 1024):.2f} MB")
                self.duration_label.configure(text=f"{TEXT_DURATION_LABEL}{datetime.timedelta(seconds=int(clip.duration))}")
                
                clip.close()
                
                # Update preview window resolution if it exists
                if hasattr(self, 'preview_window'):
                    print("Actualizando resolución del previsualizador")
                    self.preview_window.set_resolution(width, height)
                    self.preview_window.width_var.set(str(width))
                    self.preview_window.height_var.set(str(height))
                
                self.enable_controls()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el video: {str(e)}")
                self.video_path = None
                self.video_resolution = None
                self.disable_controls()
    
    def disable_controls(self):
        """Disable all controls when no video is loaded"""
        if hasattr(self, 'preview_btn'):
            self.preview_btn.configure(state="disabled")
        if hasattr(self, 'generate_btn'):
            self.generate_btn.configure(state="disabled")
        if hasattr(self, 'generate_video_btn'):
            self.generate_video_btn.configure(state="disabled")

    def enable_controls(self):
        """Enable all controls when a video is loaded"""
        if hasattr(self, 'preview_btn'):
            self.preview_btn.configure(state="normal")
        if hasattr(self, 'generate_btn'):
            self.generate_btn.configure(state="normal")
        if hasattr(self, 'generate_video_btn'):
            self.generate_video_btn.configure(state="normal")

    def refresh_workflows(self):
        workflow_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workflows")
        if not os.path.exists(workflow_dir):
            os.makedirs(workflow_dir)
        
        workflow_files = [os.path.splitext(f)[0] for f in os.listdir(workflow_dir) if f.endswith('.json')]
        
        if not workflow_files:
            self.workflow_menu.configure(values=["No hay workflows"])
            self.workflow_var.set("No hay workflows")
        else:
            self.workflow_menu.configure(values=workflow_files)
            self.workflow_var.set("Seleccionar Workflow")
    
    def on_workflow_selected(self, choice):
        if choice != "No hay workflows" and choice != "Seleccionar Workflow":
            self.load_workflow(f"{choice}.json")
    
    def load_workflow(self, workflow_file):
        try:
            workflow_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workflows", workflow_file)
            with open(workflow_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Limpiar configuraciones actuales
            for config in self.subtitle_configs:
                config.destroy()
            self.subtitle_configs.clear()
            
            # Cargar configuraciones del workflow
            for config_data in data['subtitle_configs']:
                self.add_subtitle_config()
                config = self.subtitle_configs[-1]
                config.language_var.set(config_data['language'])
                config.color_var.set(config_data['color'])
                config.color_button.configure(fg_color=config_data['color'])  # Update button color
                config.fontsize_var.set(config_data['font_size'])
                config.ypos_var.set(config_data['y_position'])
                config.border_color_var.set(config_data['border_color'])
                config.border_color_button.configure(fg_color=config_data['border_color'])  # Update button color
                config.border_size_var.set(config_data['border_size'])
            
            # Actualizar preview si existe
            if hasattr(self, 'preview_window'):
                self.preview_window.update_preview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar workflow: {str(e)}")
    
    def save_workflow(self):
        if not self.subtitle_configs:
            messagebox.showwarning("Advertencia", "No hay configuraciones para guardar")
            return
        
        # Pedir nombre del workflow
        workflow_name = simpledialog.askstring("Guardar Workflow", "Nombre del workflow:")
        if not workflow_name:
            return
        
        # Crear directorio de workflows si no existe
        workflow_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workflows")
        if not os.path.exists(workflow_dir):
            os.makedirs(workflow_dir)
        
        # Preparar datos
        workflow_data = {
            'subtitle_configs': []
        }
        
        for config in self.subtitle_configs:
            config_data = {
                'language': config.language_var.get(),
                'color': config.color_var.get(),
                'fontsize': config.fontsize_var.get(),
                'ypos': config.ypos_var.get(),
                'border_color': config.border_color_var.get(),
                'border_size': config.border_size_var.get()
            }
            workflow_data['subtitle_configs'].append(config_data)
        
        # Guardar workflow
        try:
            workflow_path = os.path.join(workflow_dir, f"{workflow_name}.json")
            with open(workflow_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=4, ensure_ascii=False)
            self.refresh_workflows()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar workflow: {str(e)}")
    
    def open_preview(self):
        if not hasattr(self, 'preview_window') or not self.preview_window.winfo_exists():
            print("Abriendo nuevo previsualizador")  # Debug
            if self.video_resolution:
                print(f"Video resolution: {self.video_resolution}")  # Debug
            else:
                print("No hay resolución de video guardada")  # Debug
                
            self.preview_window = PreviewWindow(self, self.subtitle_configs)
            
            # Si hay un video cargado, usar su resolución
            if self.video_resolution:
                print(f"Configurando resolución: {self.video_resolution}")  # Debug
                width, height = self.video_resolution
                self.preview_window.width_var.set(str(width))
                self.preview_window.height_var.set(str(height))
                self.preview_window.update_resolution()
            
            self.preview_window.focus()  # Bring window to front
    
    def get_output_filename(self):
        # Crear carpeta de exportación si no existe
        export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        # Obtener nombre base del video
        base_name = os.path.splitext(os.path.basename(self.video_path))[0]
        
        # Crear nombre de archivo en la carpeta export
        output_path = os.path.join(export_dir, f"{base_name}_subtitled.mp4")
        
        # Si el archivo ya existe, agregar número
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(export_dir, f"{base_name}_subtitled_{counter}.mp4")
            counter += 1
        
        return output_path

    def generate_subtitles_only(self, video_path):
        """
        Genera solo los subtítulos sin procesar el video
        Returns: Lista de subtítulos y sus configuraciones
        """
        try:
            print("\n=== Generando Subtítulos ===")
            print(f"Video origen: {video_path}")
            
            # Cargar el modelo de whisper
            model = whisper.load_model("base")
            
            # Transcribir el audio
            print("Transcribiendo audio...")
            result = model.transcribe(video_path)
            detected_language = result["language"]
            print(f"Idioma detectado: {detected_language}")
            
            # Mapeo de nombres de idiomas a códigos
            language_codes = {
                "English": "en",
                "Chinese": "zh-cn",
                "Spanish": "es",
                "Español": "es",
                "中文": "zh-cn"
            }
            
            # Preparar los subtítulos para cada configuración
            subtitles_data = []
            
            for config in self.subtitle_configs:
                target_lang = config.language_var.get()
                print(f"\nProcesando subtítulos para {target_lang}...")
                
                # Obtener el código de idioma correcto
                target_lang_code = language_codes.get(target_lang)
                if not target_lang_code:
                    raise ValueError(f"Código de idioma no encontrado para: {target_lang}")
                
                if target_lang_code != detected_language:
                    # Traducir si es necesario
                    translator = Translator()
                    segments = []
                    for segment in result["segments"]:
                        translated = translator.translate(
                            segment["text"], 
                            dest=target_lang_code
                        ).text
                        segments.append({
                            "text": translated,
                            "start": segment["start"],
                            "end": segment["end"]
                        })
                else:
                    segments = [
                        {
                            "text": segment["text"],
                            "start": segment["start"],
                            "end": segment["end"]
                        }
                        for segment in result["segments"]
                    ]
                
                subtitles_data.append({
                    "config": config,
                    "segments": segments
                })
                
                # Guardar SRT
                video_name = os.path.splitext(os.path.basename(video_path))[0]
                export_dir = "export"
                if not os.path.exists(export_dir):
                    os.makedirs(export_dir)
                
                srt_path = os.path.join(export_dir, f"{video_name}_{target_lang}.srt")
                with open(srt_path, 'w', encoding='utf-8') as f:
                    for i, segment in enumerate(segments, 1):
                        f.write(f"{i}\n")
                        f.write(f"{self.seconds_to_timecode(segment['start'])} --> {self.seconds_to_timecode(segment['end'])}\n")
                        f.write(f"{segment['text']}\n\n")
                
                print(f"Subtítulos guardados en: {srt_path}")
            
            print("=== Generación Completada ===\n")
            return subtitles_data, detected_language
            
        except Exception as e:
            print(f"Error generando subtítulos: {str(e)}")
            raise e

    def check_existing_subtitles(self, video_path):
        """
        Verifica si existen subtítulos para el video en la carpeta export
        Returns: 
            - None si no hay subtítulos o no corresponden
            - Lista de subtítulos y detected_language si existen y corresponden
        """
        try:
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            export_dir = "export"
            
            print("\n=== Buscando Subtítulos Existentes ===")
            print(f"Carpeta de búsqueda: {os.path.abspath(export_dir)}")
            print(f"Nombre base del video: {video_name}")
            
            if not os.path.exists(export_dir):
                print("La carpeta 'export' no existe")
                return None, None
            
            existing_subtitles = []
            
            # Verificar que existan todos los archivos SRT necesarios
            for config in self.subtitle_configs:
                target_lang = config.language_var.get()
                srt_filename = f"{video_name}_{target_lang}.srt"
                srt_path = os.path.join(export_dir, srt_filename)
                
                print(f"\nBuscando subtítulos en {target_lang}:")
                print(f"Archivo esperado: {srt_filename}")
                
                if not os.path.exists(srt_path):
                    print(f"❌ No encontrado: {srt_path}")
                    return None, None
                
                print(f"✓ Encontrado: {srt_path}")
                
                # Leer el archivo SRT
                segments = []
                with open(srt_path, 'r', encoding='utf-8') as srt_file:
                    lines = srt_file.readlines()
                    i = 0
                    while i < len(lines):
                        if lines[i].strip().isdigit():  # Número de subtítulo
                            if i + 2 < len(lines):  # Asegurar que hay suficientes líneas
                                # Parsear tiempo
                                times = lines[i + 1].strip().split(' --> ')
                                if len(times) == 2:
                                    start = self.timecode_to_seconds(times[0])
                                    end = self.timecode_to_seconds(times[1])
                                    
                                    # Obtener texto
                                    text = lines[i + 2].strip()
                                    segments.append({
                                        "text": text,
                                        "start": start,
                                        "end": end
                                    })
                            i += 4  # Saltar al siguiente grupo
                        else:
                            i += 1
                
                existing_subtitles.append({
                    "config": config,
                    "segments": segments
                })
            
            print("\n✓ Se encontraron todos los archivos de subtítulos necesarios")
            print("=== Búsqueda Completada ===\n")
            return existing_subtitles, "es"  # Asumimos español por defecto
            
        except Exception as e:
            print(f"\n❌ Error verificando subtítulos: {str(e)}")
            return None, None

    def generate_subtitles(self):
        if not self.video_path:
            messagebox.showerror("Error", "Por favor selecciona un video primero")
            return

        # Disable buttons during processing
        self.disable_controls()
        self.progress_bar.set(0)

        try:
            self.update_status("Generando subtítulos...")
            subtitles_data, detected_language = self.generate_subtitles_only(self.video_path)
            
            self.progress_bar.set(1.0)
            self.update_status("¡Subtítulos generados!")
            
            # Mostrar mensaje de éxito con las rutas de los archivos generados
            srt_paths = []
            for config_data in subtitles_data:
                config = config_data["config"]
                video_name = os.path.splitext(os.path.basename(self.video_path))[0]
                srt_path = os.path.join("export", f"{video_name}_{config.language_var.get()}.srt")
                srt_paths.append(srt_path)
            
            messagebox.showinfo("Éxito", 
                              f"Archivos SRT generados en:\n" + "\n".join(srt_paths))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar subtítulos: {str(e)}")
            self.update_status("Error en el proceso")
        
        finally:
            self.enable_controls()
            self.progress_bar.set(0)
            self.update_status("")

    def generate_video(self):
        if not self.video_path:
            messagebox.showerror("Error", "Por favor selecciona un video primero")
            return

        # Disable buttons during processing
        self.disable_controls()
        self.progress_bar.set(0)

        # Start processing in a separate thread
        thread = threading.Thread(target=self.process_video)
        thread.start()
    
    def process_video(self):
        try:
            self.update_status("Verificando subtítulos existentes...")
            self.progress_bar.set(0.1)
            
            # Verificar si existen subtítulos
            existing_subtitles, detected_language = self.check_existing_subtitles(self.video_path)
            
            if existing_subtitles:
                print("\nUsando subtítulos existentes de la carpeta 'export'")
                self.update_status("Usando subtítulos existentes...")
                subtitles_data = existing_subtitles
            else:
                print("\nNo se encontraron subtítulos existentes. Generando nuevos subtítulos...")
                self.update_status("Generando nuevos subtítulos...")
                subtitles_data, detected_language = self.generate_subtitles_only(self.video_path)
            
            self.progress_bar.set(0.3)
            
            # Load the video
            video = VideoFileClip(self.video_path)
            
            self.update_status(f"Procesando subtítulos...")
            self.progress_bar.set(0.4)
            
            # Process segments with timestamps
            subtitle_clips = []
            
            # Get system fonts directory
            system_fonts_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
            
            # Define font paths based on languages
            font_paths = {}
            for config_data in subtitles_data:
                config = config_data["config"]
                lang = config.language_var.get()
                language_name = lang.split(' (')[0]
                
                if language_name in ['Chinese', 'Japanese', 'Korean']:
                    possible_fonts = ['MSYH.TTC', 'SIMHEI.TTF', 'SIMSUN.TTC', 'MALGUN.TTF', 'MEIRYO.TTC']
                elif language_name in ['Arabic', 'Hebrew']:
                    possible_fonts = ['ARIAL.TTF']
                else:
                    possible_fonts = ['ARIAL.TTF', 'SEGOEUI.TTF']

                font_path = None
                for font in possible_fonts:
                    temp_path = os.path.join(system_fonts_dir, font)
                    if os.path.exists(temp_path):
                        font_path = temp_path
                        break
                if not font_path:
                    font_path = 'Arial'
                font_paths[lang] = font_path

            # Generate output filename
            output_path = self.get_output_filename()
            if not output_path:
                return

            # Si no existían los subtítulos, generarlos
            if not existing_subtitles:
                srt_paths = {}
                for config_data in subtitles_data:
                    config = config_data["config"]
                    segments = config_data["segments"]
                    
                    video_name = os.path.splitext(os.path.basename(self.video_path))[0]
                    export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export")
                    if not os.path.exists(export_dir):
                        os.makedirs(export_dir)
                    
                    srt_path = os.path.join(export_dir, f"{video_name}_{config.language_var.get()}.srt")
                    with open(srt_path, 'w', encoding='utf-8') as srt_file:
                        for j, segment in enumerate(segments, 1):
                            text = segment["text"]
                            start_time = segment["start"]
                            end_time = segment["end"]
                            
                            # Write to SRT file
                            srt_file.write(f"{j}\n")
                            srt_file.write(f"{self.seconds_to_timecode(start_time)} --> {self.seconds_to_timecode(end_time)}\n")
                            srt_file.write(f"{text}\n\n")
                    
                    srt_paths[config.language_var.get()] = srt_path

            # Crear clips de subtítulos
            for config_data in subtitles_data:
                config = config_data["config"]
                segments = config_data["segments"]
                
                for segment in segments:
                    frame = create_text_clip(
                        text=segment["text"],
                        size=(video.w, int(video.h * 0.3)),
                        duration=segment["end"] - segment["start"],
                        font_path=font_paths[config.language_var.get()],
                        font_size=int(config.fontsize_var.get() * VIDEO_FONT_SCALE),
                        color=config.color_var.get(),
                        border_color=config.border_color_var.get(),
                        border_size=config.border_size_var.get()
                    )
                    
                    # Calculate Y position (from bottom)
                    y_position = int((100 - config.ypos_var.get()) * video.h / 100)
                    
                    # Create subtitle clip
                    txt_clip = (ImageClip(frame, transparent=True)
                              .set_duration(segment["end"] - segment["start"])
                              .set_start(segment["start"])
                              .set_position(('center', y_position)))
                    
                    subtitle_clips.append(txt_clip)
            
            self.update_status("Generando video final...")
            self.progress_bar.set(0.8)
            
            # Combine video with all subtitle clips
            final_video = CompositeVideoClip([video] + subtitle_clips)
            
            # Write final video with higher quality settings
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=video.fps,
                bitrate="8000k"
            )
            
            # Clean up
            video.close()
            final_video.close()
            
            self.progress_bar.set(1.0)
            self.update_status("¡Proceso completado!")
            
            success_message = f"Video con subtítulos generado exitosamente:\n{output_path}"
            if not existing_subtitles:
                success_message += f"\n\nArchivos SRT generados en:\n" + "\n".join(srt_paths.values())
            
            messagebox.showinfo("Éxito", success_message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
            self.update_status("Error en el proceso")
        
        finally:
            # Re-enable buttons
            self.enable_controls()
            self.progress_bar.set(0)
            self.update_status("")
    
    def update_status(self, text):
        self.status_label.configure(text=text)
        self.update()

    def change_interface_language(self, choice):
        """Cambia el idioma de la interfaz"""
        global lenguajeSelect
        lenguajeSelect = self.language_options[choice]
        initialize_interface_texts()
        
        # Guardar el estado actual
        current_video = self.video_path
        current_workflow = self.workflow_menu.get() if hasattr(self, 'workflow_menu') else None
        current_video_resolution = self.video_resolution
        
        # Guardar configuración de subtítulos
        saved_subtitle_configs = []
        if hasattr(self, 'subtitle_configs'):
            for config in self.subtitle_configs:
                saved_config = {
                    'language': config.language_var.get(),
                    'color': config.color_var.get(),
                    'fontsize': config.fontsize_var.get(),
                    'ypos': config.ypos_var.get(),
                    'border_color': config.border_color_var.get(),
                    'border_size': config.border_size_var.get()
                }
                saved_subtitle_configs.append(saved_config)
        
        # Destruir todos los widgets actuales
        for widget in self.winfo_children():
            widget.destroy()
        
        # Limpiar la lista de configuraciones de subtítulos
        self.subtitle_configs = []
        
        # Recrear todos los widgets
        self.create_widgets()
        
        # Restaurar el estado
        if current_video:
            self.video_path = current_video
            self.video_resolution = current_video_resolution
            
            # Restaurar información del video
            if hasattr(self, 'video_label'):
                self.video_label.configure(text=f"Video: {os.path.basename(current_video)}")
            
            if hasattr(self, 'resolution_label') and current_video_resolution:
                width, height = current_video_resolution
                self.resolution_label.configure(text=f"{TEXT_RESOLUTION_LABEL}{width}x{height}")
            
            if hasattr(self, 'size_label') and current_video:
                size_mb = os.path.getsize(current_video) / (1024 * 1024)
                self.size_label.configure(text=f"{TEXT_SIZE_LABEL}{size_mb:.2f} MB")
            
            if hasattr(self, 'duration_label') and current_video:
                with VideoFileClip(current_video) as video:
                    duration = datetime.timedelta(seconds=int(video.duration))
                    self.duration_label.configure(text=f"{TEXT_DURATION_LABEL}{duration}")
            
            self.enable_controls()
        
        # Restaurar workflow
        if hasattr(self, 'workflow_menu'):
            self.refresh_workflows()  # Recargar lista de workflows
            if current_workflow:
                self.workflow_menu.set(current_workflow)
        
        # Restaurar configuraciones de subtítulos
        for config in saved_subtitle_configs:
            self.add_subtitle_config()  # Crear nuevo frame de subtítulo
            current_config = self.subtitle_configs[-1]  # Obtener el último config creado
            
            # Restaurar valores
            current_config.language_var.set(config['language'])
            current_config.color_var.set(config['color'])
            current_config.color_button.configure(fg_color=config['color'])  # Update button color
            current_config.fontsize_var.set(config['fontsize'])
            current_config.ypos_var.set(config['ypos'])
            current_config.border_color_var.set(config['border_color'])
            current_config.border_color_button.configure(fg_color=config['border_color'])  # Update button color
            current_config.border_size_var.set(config['border_size'])
            
            # Actualizar color del botón
            current_config.color_button.configure(fg_color=config['color'])
        
        # Forzar actualización
        self.update()
    
    def create_widgets(self):
        # Language selector - Top of the window
        language_frame = ctk.CTkFrame(self)
        language_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        language_frame.grid_columnconfigure(1, weight=1)  # Centrar el selector

        language_selector = ctk.CTkOptionMenu(
            language_frame,
            values=list(self.language_options.keys()),
            command=self.change_interface_language,
            width=120
        )
        language_selector.grid(row=0, column=1, padx=5, pady=5)
        # Establecer el valor inicial basado en lenguajeSelect
        for lang, value in self.language_options.items():
            if value == lenguajeSelect:
                language_selector.set(lang)
                break

        # Video controls - Row 1
        video_frame = ctk.CTkFrame(self)
        video_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        video_frame.grid_columnconfigure(1, weight=1)
        
        load_video_btn = ctk.CTkButton(
            video_frame,
            text=TEXT_LOAD_VIDEO,
            command=self.load_video,
            width=120
        )
        load_video_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Frame para la información del video
        video_info_frame = ctk.CTkFrame(video_frame)
        video_info_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        video_info_frame.grid_columnconfigure(1, weight=1)
        
        # Labels para la información del video
        self.video_label = ctk.CTkLabel(video_info_frame, text=TEXT_NO_VIDEO, anchor="w")
        self.video_label.grid(row=0, column=0, columnspan=2, padx=5, pady=2, sticky="w")
        
        self.resolution_label = ctk.CTkLabel(video_info_frame, text=TEXT_RESOLUTION_LABEL+"-", anchor="w")
        self.resolution_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        self.size_label = ctk.CTkLabel(video_info_frame, text=TEXT_SIZE_LABEL+"-", anchor="w")
        self.size_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")
        
        self.duration_label = ctk.CTkLabel(video_info_frame, text=TEXT_DURATION_LABEL+"-", anchor="w")
        self.duration_label.grid(row=3, column=0, padx=5, pady=2, sticky="w")
        
        # Workflow controls - Row 2
        workflow_frame = ctk.CTkFrame(self)
        workflow_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        workflow_frame.grid_columnconfigure(3, weight=1)
        
        save_workflow_btn = ctk.CTkButton(
            workflow_frame,
            text=TEXT_SAVE_WORKFLOW,
            command=self.save_workflow,
            width=120
        )
        save_workflow_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # Menú desplegable para workflows
        self.workflow_var = ctk.StringVar(value="Seleccionar Workflow")
        self.workflow_menu = ctk.CTkOptionMenu(
            workflow_frame,
            values=["No hay workflows"],
            variable=self.workflow_var,
            command=self.on_workflow_selected,
            width=200
        )
        self.workflow_menu.grid(row=0, column=1, padx=5, pady=5)
        
        refresh_btn = ctk.CTkButton(
            workflow_frame,
            text="↻",
            command=self.refresh_workflows,
            width=30
        )
        refresh_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Subtitle controls - Row 3
        subtitle_frame = ctk.CTkFrame(self)
        subtitle_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        subtitle_frame.grid_columnconfigure(0, weight=1)
        
        # Título centrado para la sección de subtítulos
        subtitle_title = ctk.CTkLabel(subtitle_frame, text=TEXT_SUBTITLE_CONFIG, 
                                     font=("Segoe UI", 14, "bold"))
        subtitle_title.grid(row=0, column=0, padx=5, pady=(10,5))
        
        self.add_btn = ctk.CTkButton(
            subtitle_frame,
            text=TEXT_ADD_SUBTITLE,
            command=self.add_subtitle_config,
            width=120
        )
        self.add_btn.grid(row=1, column=0, padx=5, pady=5)
        
        # Scrollable frame for subtitle configs - Row 4
        self.subtitle_container = ctk.CTkScrollableFrame(self)
        self.subtitle_container.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        self.subtitle_container.grid_columnconfigure(0, weight=1)  # Centrar contenido
        self.grid_rowconfigure(4, weight=1)  # Make this row expandable
        
        # Preview and Generate controls - Row 5
        control_frame = ctk.CTkFrame(self)
        control_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        control_frame.grid_columnconfigure((0,1,2), weight=1)
        
        button_width = 200
        button_height = 35
        button_font = ("Segoe UI", 12)
        
        self.preview_btn = ctk.CTkButton(
            control_frame,
            text=TEXT_OPEN_PREVIEW,
            command=self.open_preview,
            width=button_width,
            height=button_height,
            font=button_font
        )
        self.preview_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        generate_video_button = ctk.CTkButton(
            control_frame,
            text=TEXT_GENERATE_VIDEO,
            command=self.generate_video,
            width=button_width,
            height=button_height,
            font=button_font
        )
        generate_video_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.generate_btn = ctk.CTkButton(
            control_frame,
            text=TEXT_GENERATE_SUBTITLES,
            command=self.generate_subtitles,
            width=button_width,
            height=button_height,
            font=button_font
        )
        self.generate_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # Progress bar - Row 6
        progress_frame = ctk.CTkFrame(self)
        progress_frame.grid(row=6, column=0, padx=10, pady=(5,20), sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.grid(row=7, column=0, padx=10, pady=5)

    def timecode_to_seconds(self, timecode):
        """Convierte un timecode SRT (00:00:00,000) a segundos"""
        hours, minutes, seconds = timecode.replace(',', '.').split(':')
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    
    def seconds_to_timecode(self, seconds):
        """Convierte segundos a formato de timecode SRT (00:00:00,000)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace('.', ',')

if __name__ == "__main__":
    app = SubtitleGenerator()
    app.mainloop()
