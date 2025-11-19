import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
import vlc
import os
import chardet
from tkinterdnd2 import DND_FILES, TkinterDnD

class AudioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Audio Player")
        
        # Create a VLC instance with no video output
        self.instance = vlc.Instance("--no-video")
        self.player = self.instance.media_player_new()

        # Status label for loaded file
        self.status = tk.Label(root, text="Drop MP3/MP4 file here")
        self.status.pack(pady=10)

        # Create a progress frame that holds the progress slider
        self.progress_frame = tk.Frame(root)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create the progress slider
        self.progress_slider = tk.Scale(
            self.progress_frame, from_=0, to=100,
            orient=tk.HORIZONTAL, showvalue=0, length=600
        )
        self.progress_slider.pack(fill=tk.X)
        self.progress_slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.progress_slider.bind("<ButtonRelease-1>", self.on_slider_release)
        self.slider_dragging = False

        # Time label for current / total time
        self.time_label = tk.Label(root, text="00:00:00 / 00:00:00")
        self.time_label.pack(pady=5)

        # Current track label
        self.current_track_label = tk.Label(root, text="Current track: —", fg="blue", font=("TkDefaultFont", 10, "bold"))
        self.current_track_label.pack(pady=5)

        # Create the control panel with playback buttons and volume control
        self.controls = tk.Frame(root)
        self.controls.pack(fill=tk.X, padx=10, pady=5)

        # Play button
        self.play_button = tk.Button(self.controls, text="Play", command=self.play_audio)
        self.play_button.pack(side=tk.LEFT, padx=5)

        # Stop button
        self.stop_button = tk.Button(self.controls, text="Stop", command=self.stop_audio)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Volume control slider
        self.volume_slider = tk.Scale(
            self.controls, from_=0, to=100,
            orient=tk.HORIZONTAL, label="Volume",
            command=self.set_volume
        )
        self.volume_slider.set(50)  # Set the default volume to 50%
        self.volume_slider.pack(side=tk.LEFT, padx=5)

        # Markers section
        self.markers_frame = tk.Frame(root)
        self.markers_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Buttons frame for add, load, and clear
        self.buttons_frame = tk.Frame(self.markers_frame)
        self.buttons_frame.pack(pady=5)

        # Add marker button
        self.add_button = tk.Button(self.buttons_frame, text="Add Marker", command=self.add_marker)
        self.add_button.pack(side=tk.LEFT, padx=5)

        # Load markers button
        self.load_button = tk.Button(self.buttons_frame, text="Load Markers", command=self.load_markers)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Clear markers button
        self.clear_button = tk.Button(self.buttons_frame, text="Clear Markers", command=self.clear_markers)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Treeview for markers list
        self.tree = ttk.Treeview(self.markers_frame, columns=('time', 'label'), show='headings')
        self.tree.heading('time', text='Time')
        self.tree.heading('label', text='Label')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind double-click to seek to marker
        self.tree.bind("<Double-1>", self.on_marker_click)

        # Enable drag and drop on the root window
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.on_drop)

        # Begin updating the progress slider and time label periodically
        self.update_progress()

    def on_drop(self, event):
        # Handle dropped file path (strip braces if present)
        file_path = event.data.strip("{}")
        if file_path:
            self.file_path = file_path
            media = self.instance.media_new(file_path)
            self.player.set_media(media)
            self.status.config(text=f"Loaded: {file_path}")

    def play_audio(self):
        self.player.play()

    def stop_audio(self):
        self.player.stop()

    def set_volume(self, value):
        self.player.audio_set_volume(int(value))

    def on_slider_press(self, event):
        self.slider_dragging = True

    def on_slider_release(self, event):
        self.slider_dragging = False
        self.seek_audio()

    def seek_audio(self):
        slider_value = self.progress_slider.get()
        self.player.set_time(int(slider_value))

    def update_progress(self):
        current_ms = self.player.get_time()
        duration_ms = self.player.get_length()

        if duration_ms > 0:
            if not self.slider_dragging:
                self.progress_slider.config(to=duration_ms)
                self.progress_slider.set(current_ms)

            current_fmt = self.format_time(current_ms)
            duration_fmt = self.format_time(duration_ms)
            self.time_label.config(text=f"{current_fmt} / {duration_fmt}")

            # Update current track label
            self.update_current_track_label(current_ms)

        self.root.after(500, self.update_progress)

    def format_time(self, ms):
        if ms < 0:
            ms = 0
        seconds = ms // 1000
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds %= 60
        if hours == 0:
            return f"{minutes:02d}:{seconds:02d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def parse_time(self, time_str):
        parts = time_str.split(':')
        try:
            if len(parts) == 2:
                m, s = map(int, parts)
                return (m * 60 + s) * 1000
            elif len(parts) == 3:
                h, m, s = map(int, parts)
                return (h * 3600 + m * 60 + s) * 1000
            else:
                return 0
        except:
            return 0

    def add_marker(self):
        time_str = simpledialog.askstring("Timestamp", "Enter timestamp (HH:MM:SS or MM:SS), leave blank for current:")
        if time_str == "":
            ms = self.player.get_time()
            time_str = self.format_time(ms)
        else:
            ms = self.parse_time(time_str)
            time_str = self.format_time(ms)

        label = simpledialog.askstring("Label", "Enter label:")
        if label:
            self.tree.insert('', 'end', values=(time_str, label))

    def load_markers(self):
        if not hasattr(self, 'file_path') or not self.file_path:
            messagebox.showerror("Error", "No audio file loaded.")
            return

        txt_path = os.path.splitext(self.file_path)[0] + '.txt'
        if not os.path.exists(txt_path):
            messagebox.showinfo("Info", "No corresponding TXT file found.")
            return

        with open(txt_path, 'rb') as f:
            raw_data = f.read()

        result = chardet.detect(raw_data)
        encoding = result['encoding']
        if encoding is None:
            encoding = 'utf-8'  # Fallback to UTF-8

        try:
            text = raw_data.decode(encoding)
        except UnicodeDecodeError:
            messagebox.showerror("Error", f"Failed to decode file with detected encoding '{encoding}'. Trying UTF-8.")
            text = raw_data.decode('utf-8', errors='replace')

        lines = text.splitlines()

        self.tree.delete(*self.tree.get_children())

        for line in lines:
            line = line.strip()
            if line:
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    time_str, label = parts
                    ms = self.parse_time(time_str)
                    time_str = self.format_time(ms)
                    self.tree.insert('', 'end', values=(time_str, label))

    def clear_markers(self):
        """Clear all markers from the Treeview (does NOT affect the .txt file)."""
        self.tree.delete(*self.tree.get_children())

    def on_marker_click(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            time_str, label = self.tree.item(item, 'values')
            ms = self.parse_time(time_str)
            self.player.set_time(ms)

    def update_current_track_label(self, current_ms):
        # Clear any existing selection
        self.tree.selection_remove(self.tree.selection())

        best_item = None
        best_time = -1
        best_label = "—"

        # Iterate through all markers to find the latest one <= current time
        for child in self.tree.get_children():
            time_str, label = self.tree.item(child, 'values')
            ms = self.parse_time(time_str)
            if ms <= current_ms and ms > best_time:
                best_time = ms
                best_label = label
                best_item = child

        self.current_track_label.config(text=f"Current track: {best_label}")

        # Highlight and scroll to the matching item if found
        if best_item:
            self.tree.selection_set(best_item)
            self.tree.see(best_item)

    def update_current_track_label_old(self, current_ms):
        # Get all markers sorted by time (they should already be in order, but we'll sort to be safe)
        markers = []
        for child in self.tree.get_children():
            time_str, label = self.tree.item(child, 'values')
            ms = self.parse_time(time_str)
            markers.append((ms, label))
        
        # Sort by time just in case
        markers.sort(key=lambda x: x[0])

        # Find the latest marker with time <= current_ms
        current_label = "—"
        for ms, label in markers:
            if ms <= current_ms:
                current_label = label
            else:
                break  # since sorted, no need to check further

        self.current_track_label.config(text=f"Current track: {current_label}")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    root.geometry("800x450")  # Slightly taller to accommodate new label
    player = AudioPlayer(root)
    root.mainloop()