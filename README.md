# SubBridge - Subtitle Generator

A desktop application for generating and customizing multilingual subtitles for your videos.

## Features

- User-friendly graphical interface
- Multiple interface languages (English, Español, 中文)
- AI-powered automatic subtitle generation
- Translation of subtitles into multiple languages
- Subtitle customization:
  - Color
  - Font size
  - Vertical position
- Real-time preview
- Save and load workflow configurations

## Prerequisites

1. Python 3.10 or higher
2. ImageMagick (required for video processing)
   - Windows: [Download ImageMagick](https://imagemagick.org/script/download.php#windows)
   - During installation, make sure to check "Install legacy utilities (e.g. convert)"

## Installation

### Easy Installation (Windows)

1. Download and install [Python 3.10 or higher](https://www.python.org/downloads/)
2. Download and install [ImageMagick](https://imagemagick.org/script/download.php#windows)
   - During installation, make sure to check "Install legacy utilities (e.g. convert)"
3. Double click on `install.bat`
4. Wait for the installation to complete

### Manual Installation

1. Clone or download this repository

2. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Easy Start (Windows)

1. Double click on `run.bat`
2. The application will start automatically

### Manual Start

1. Activate the virtual environment if you created one:
```bash
venv\Scripts\activate
```

2. Run the application:
```bash
python subtitle_generator.py
```

3. Basic steps:
   - Click "Load video" to select your video file
   - Add one or more subtitle languages using "Add subtitle"
   - Customize the color, size, and position of each subtitle
   - Use "Open preview" to see how the subtitles will look
   - Click "Generate subtitles" to create the video with subtitles

4. You can save your current configuration as a workflow to reuse it later

## Supported Languages

The application supports subtitle generation and translation in over 50 languages, including:
- English
- Español (Spanish)
- 中文 (Chinese)
- Français (French)
- Deutsch (German)
- 日本語 (Japanese)
- And many more...

## Notes

- The first time you use the application with a new language, the required speech recognition model will be automatically downloaded
- Processing time will depend on the video duration and number of selected languages
- It's recommended to use videos with clear audio for best results

## Troubleshooting

1. If you receive an error about ImageMagick:
   - Make sure you have installed ImageMagick correctly
   - Verify that the "Install legacy utilities" option is checked
   - Restart your computer after installing ImageMagick

2. If subtitles don't appear:
   - Verify that the video has audio
   - Make sure the video format is supported (MP4, AVI, MOV)
   - Check if the selected language model was downloaded correctly

## System Requirements

- Operating System: Windows 10 or higher
- RAM: Minimum 8GB (16GB recommended for better performance)
- Storage: At least 2GB free space for language models
- GPU: Optional but recommended for faster processing
