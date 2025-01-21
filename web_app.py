import os
import gradio as gr
import whisper
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from googletrans import Translator
import tempfile

# Configuraciones
SUPPORTED_LANGUAGES = {
    'English': 'en',
    'Spanish': 'es',
    'Chinese': 'zh-cn',
    'Japanese': 'ja',
    'Korean': 'ko',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Russian': 'ru'
}

def create_text_clip(text, size, duration, font_size=35, color='white', border_color='black', border_size=2):
    """Crear un clip de texto con soporte para CJK"""
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    
    # Crear imagen temporal para el texto
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Intentar usar una fuente que soporte CJK
    try:
        if os.name == 'nt':  # Windows
            font = ImageFont.truetype("MSGOTHIC.TTC", font_size)
        else:  # Linux/Mac
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Obtener tamaño del texto
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Centrar texto
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Dibujar borde
    for offset_x in range(-border_size, border_size + 1):
        for offset_y in range(-border_size, border_size + 1):
            draw.text((x + offset_x, y + offset_y), text, font=font, fill=border_color)
    
    # Dibujar texto principal
    draw.text((x, y), text, font=font, fill=color)
    
    return np.array(img)

def process_video(video_path, source_lang, target_lang, font_size, text_color, border_color, border_size, y_position):
    """Procesar video y generar subtítulos"""
    try:
        # Cargar modelo de Whisper
        model = whisper.load_model("base")
        
        # Transcribir audio
        result = model.transcribe(video_path)
        segments = result["segments"]
        
        # Traducir si es necesario
        if target_lang != source_lang:
            translator = Translator()
            translated_segments = []
            for segment in segments:
                translation = translator.translate(
                    segment["text"],
                    src=source_lang,
                    dest=target_lang
                )
                segment["text"] = translation.text
                translated_segments.append(segment)
            segments = translated_segments
        
        # Crear video con subtítulos
        video = VideoFileClip(video_path)
        subtitle_clips = []
        
        for segment in segments:
            start_time = segment["start"]
            end_time = segment["end"]
            duration = end_time - start_time
            
            # Crear clip de texto
            frame = create_text_clip(
                text=segment["text"],
                size=(video.w, int(video.h * 0.3)),
                duration=duration,
                font_size=font_size,
                color=text_color,
                border_color=border_color,
                border_size=border_size
            )
            
            # Calcular posición Y
            y_pos = int((100 - y_position) * video.h / 100)
            
            # Crear clip de subtítulo
            txt_clip = (TextClip(frame, transparent=True)
                      .set_duration(duration)
                      .set_start(start_time)
                      .set_position(('center', y_pos)))
            
            subtitle_clips.append(txt_clip)
        
        # Combinar video con subtítulos
        final_video = CompositeVideoClip([video] + subtitle_clips)
        
        # Crear archivo temporal para el output
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            output_path = tmp_file.name
        
        # Guardar video final
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=video.fps
        )
        
        # Limpiar
        video.close()
        final_video.close()
        
        return output_path
    
    except Exception as e:
        raise gr.Error(f"Error al procesar el video: {str(e)}")

# Crear interfaz de Gradio
with gr.Blocks(title="Sub Bridge Web - Generador de Subtítulos") as interface:
    gr.Markdown("# Sub Bridge Web")
    gr.Markdown("### Generador de Subtítulos Online")
    
    with gr.Row():
        with gr.Column():
            video_input = gr.Video(label="Subir Video")
            source_lang = gr.Dropdown(
                choices=list(SUPPORTED_LANGUAGES.keys()),
                value="English",
                label="Idioma Original"
            )
            target_lang = gr.Dropdown(
                choices=list(SUPPORTED_LANGUAGES.keys()),
                value="Spanish",
                label="Idioma de Subtítulos"
            )
        
        with gr.Column():
            font_size = gr.Slider(
                minimum=20,
                maximum=80,
                value=35,
                step=1,
                label="Tamaño de Fuente"
            )
            text_color = gr.ColorPicker(
                value="#FFFFFF",
                label="Color del Texto"
            )
            border_color = gr.ColorPicker(
                value="#000000",
                label="Color del Borde"
            )
            border_size = gr.Slider(
                minimum=0,
                maximum=5,
                value=2,
                step=1,
                label="Grosor del Borde"
            )
            y_position = gr.Slider(
                minimum=0,
                maximum=100,
                value=90,
                step=1,
                label="Posición Vertical (%)"
            )
    
    with gr.Row():
        process_btn = gr.Button("Generar Video con Subtítulos", variant="primary")
        
    video_output = gr.Video(label="Video con Subtítulos")
    
    process_btn.click(
        fn=process_video,
        inputs=[
            video_input,
            source_lang,
            target_lang,
            font_size,
            text_color,
            border_color,
            border_size,
            y_position
        ],
        outputs=video_output
    )

# Iniciar la aplicación
if __name__ == "__main__":
    interface.launch()
