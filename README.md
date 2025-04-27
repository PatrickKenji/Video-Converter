# Video Converter

A modern, user-friendly video converter built with Python and Tkinter. Supports batch conversion, hardware acceleration (NVIDIA NVENC, Intel VAAPI), and maximum compatibility for MP4 output.

## Features
- Batch video conversion with queue management
- Output formats: MP4, AVI, MOV, MKV, WEBM
- Quality selection: Fast, Medium, High
- Automatic hardware acceleration detection and fallback to CPU if unavailable
- MP4 output optimized for maximum compatibility (profile high, level 4.1, yuv420p, keyframes)
- Progress bar and status for each file
- Modern dark-themed GUI

## Requirements
- Python 3.8+
- FFmpeg (must be installed and available in your PATH)
- NVIDIA GPU (optional, for NVENC acceleration)
- Intel GPU (optional, for VAAPI acceleration on Linux)

## Installation
1. Install Python 3.8 or newer.
2. Install FFmpeg and ensure it is in your system PATH.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```bash
   python conversor_video.py
   ```
2. Add videos to the queue.
3. Select output format and quality.
4. Choose the output folder.
5. Click "Start Conversion".

If hardware acceleration is not available, the converter will automatically use the CPU (libx264) for maximum compatibility.

## Notes
- For best compatibility, MP4 files are encoded with profile high, level 4.1, yuv420p pixel format, and regular keyframes.
- If you encounter issues with hardware acceleration, ensure your drivers and FFmpeg build support NVENC/VAAPI.

## Formatos suportados

- Entrada: MP4, AVI, MOV, MKV, WEBM
- Saída: MP4, AVI, MOV, MKV, WEBM 