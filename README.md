# MinimalVLC

A lightweight audio/video player built with **Python**, **Tkinter**, **python-vlc**, and **TkinterDnD2** that supports:

- Playing MP3, MP4 and most common video formats
- Drag-and-drop file loading
- Video display (when a video file is loaded)
- Progress slider with seeking
- Volume control
- **Markers** (timestamps + labels) that can be:
  - Added manually
  - Loaded automatically from a `.txt` file with the same base name as the media file
  - Double-clicked to jump to that position
- Automatic "Current track" display that updates as playback passes markers

Perfect for language learners, DJs, or anyone who needs quick timestamp navigation.

## Author

Original code by **Grok 4** – modified & improved by **Gemini 3.0**

## Requirements

- Python 3.8+
- VLC Media Player installed on your system (the `python-vlc` package needs the VLC libraries)

## Installation (using **uv** – the fast Python package manager)

```bash
# Clone or download the repository
git clone https://github.com/yourusername/simple-audio-player.git
cd simple-audio-player

# Recommended: create a virtual environment
uv venv

# Activate it (choose the one that matches your shell)
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies with uv
uv pip install pyvlc tkinterdnd2 chardet
