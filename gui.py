import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import keyboard
import pyautogui
from instrument import INSTRUMENTS

SPECIAL_KEYS = {
    "Shift": "shift",
    "Ctrl": "ctrl",
    "Alt": "alt",
    "Win": "windows",
    "Tab": "tab",
    "Backspace": "backspace",
    "Space": "space"
}

MOUSE_MOVEMENTS = {
    "MouseMove:Up",
    "MouseMove:Down",
    "MouseMove:Left",
    "MouseMove:Right"
}

INSTRUMENT_TRANSPOSITIONS = {
    "Bb Clarinet": 2,
    "C Flute": 0,
    "Bb Trumpet": 2,
    "Alto Sax": 9,
    "Tenor Sax": 14,
    "Bass Clarinet": 2,
    "Horn in F": 7
}


class ClarinetGUI:
    def __init__(self, root, pitch_listener, default_profile='profiles/default.json'):
        self.root = root
        self.root.title("🎵 Music-Keybinds 🎶")
        self.listener = pitch_listener
        self.profile = {}
        self.current_note = tk.StringVar()
        self.mapped_key = tk.StringVar()

        self._build_ui()
        self.load_profile(default_profile)

    def _build_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid()

        ttk.Label(frame, text="Detected Note:").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.current_note, font=("Arial", 14)).grid(row=0, column=1, sticky="w")

        self.visual_label = ttk.Label(frame, text="", font=("Consolas", 18))
        self.visual_label.grid(row=1, column=0, columnspan=2, pady=(5, 10))

        ttk.Label(frame, text="Mapped Key:").grid(row=2, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.mapped_key, font=("Arial", 14)).grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Instrument:").grid(row=3, column=0, sticky="w")
        self.instrument_combo = ttk.Combobox(frame, values=list(INSTRUMENT_TRANSPOSITIONS.keys()), state="readonly")
        self.instrument_combo.set("Bb Clarinet")
        self.instrument_combo.grid(row=3, column=1, sticky="ew")
        self.instrument_combo.bind("<<ComboboxSelected>>", self.change_instrument)

        # Treeview to list notes and their corresponding keys
        self.tree = ttk.Treeview(frame, columns=('Note', 'Key', 'Sustain'), show='headings', height=15)
        self.tree.heading('Note', text='Note')
        self.tree.heading('Key', text='Action')
        self.tree.heading('Sustain', text='Sustain')

        self.tree.grid(row=4, column=0, columnspan=2, pady=5)
        self.tree.bind("<Double-1>", self.edit_key)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Start", command=self.listener.start).grid(row=0, column=0)
        ttk.Button(button_frame, text="Stop", command=self.listener.stop).grid(row=0, column=1)
        ttk.Button(button_frame, text="Save Profile", command=self.save_profile).grid(row=0, column=2)
        ttk.Button(button_frame, text="Load Profile", command=self.load_profile_dialog).grid(row=0, column=3)

        ttk.Button(button_frame, text="Assign Mouse Click", command=self.assign_mouse_click).grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(button_frame, text="Assign Mouse Move", command=self.assign_mouse_movement).grid(row=1, column=2, columnspan=2, pady=5)

        # New Button for toggling sustain
        ttk.Button(button_frame, text="Toggle Sustain", command=self.toggle_sustain).grid(row=2, column=0, columnspan=4, pady=5)

    def toggle_sustain(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Note Selected", "Please select a note from the list first.")
            return

        selected_item = selected[0]
        note = self.tree.item(selected_item)['values'][0]

        # Toggle sustain value for the selected note
        if note in self.profile:
            current_sustain = self.profile[note].get('sustain', False)
            new_sustain = not current_sustain
            self.profile[note]['sustain'] = new_sustain
            self.refresh_table()


    def update_note(self, note):
        VALID_NOTES = [
            'E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3',
            'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4',
            'C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5',
            'C6', 'C#6', 'D6', 'D#6', 'E6', 'F6', 'F#6', 'G6', 'G#6', 'A6', 'A#6', 'B6',
            'C7'
        ]

        if not note or note not in VALID_NOTES:
            return

        self.current_note.set(note)
        self.visual_label.config(text=f"🎵 {note}")

        mapped_key_data = self.profile.get(note)
        if mapped_key_data:
            self.mapped_key.set(mapped_key_data['key'])
            self.trigger_action(mapped_key_data['key'], mapped_key_data['sustain'])
        else:
            self.mapped_key.set("---")

        self.refresh_table()

    def trigger_action(self, key, sustain=False):
        if key.startswith("Mouse:"):
            button = key.split(":")[1].lower()
            pyautogui.click(button=button)
        elif key.startswith("MouseMove:"):
            direction = key.split(":")[1]
            amount = 50  # pixels
            if direction == "Up":
                pyautogui.move(0, -amount)
            elif direction == "Down":
                pyautogui.move(0, amount)
            elif direction == "Left":
                pyautogui.move(-amount, 0)
            elif direction == "Right":
                pyautogui.move(amount, 0)
        else:
            if sustain:
                keyboard.press(key)
            else:
                keyboard.press(key)
                keyboard.release(key)

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for note in [
            'E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3',
            'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4',
            'C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5',
            'C6', 'C#6', 'D6', 'D#6', 'E6', 'F6', 'F#6', 'G6', 'G#6', 'A6', 'A#6', 'B6',
            'C7']:
            key_data = self.profile.get(note, {})
            sustain = key_data.get('sustain', False)
            key = key_data.get('key', '---')

            self.tree.insert("", "end", values=(note, key, sustain))

    def edit_key(self, event):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Note Selected", "Please select a note from the list first.")
            return  # Return early if no selection is made

        selected_item = selected[0]
        note = self.tree.item(selected_item)['values'][0]

        def on_key(event):
            key = event.keysym.lower()
            if key in SPECIAL_KEYS.values():
                self.profile[note] = {'key': key, 'sustain': False}
            else:
                self.profile[note] = {'key': event.char, 'sustain': False}
            popup.destroy()
            self.refresh_table()

        popup = tk.Toplevel(self.root)
        popup.title(f"Set key for {note}")
        ttk.Label(popup, text="Press a key or special key:").pack(padx=10, pady=10)
        popup.bind("<Key>", on_key)

    def assign_mouse_click(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Note Selected", "Please select a note from the list first.")
            return

        note = self.tree.item(selected[0])['values'][0]

        def set_click(button_type):
            self.profile[note] = {'key': f"Mouse:{button_type}", 'sustain': False}
            popup.destroy()
            self.refresh_table()

        popup = tk.Toplevel(self.root)
        popup.title(f"Assign Mouse Click for {note}")
        ttk.Button(popup, text="Left Click", command=lambda: set_click('left')).pack(padx=10, pady=5)
        ttk.Button(popup, text="Right Click", command=lambda: set_click('right')).pack(padx=10, pady=5)
        ttk.Button(popup, text="Middle Click", command=lambda: set_click('middle')).pack(padx=10, pady=5)

    def assign_mouse_movement(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Note Selected", "Please select a note from the list first.")
            return

        note = self.tree.item(selected[0])['values'][0]

        def set_move(direction):
            self.profile[note] = {'key': f"MouseMove:{direction}", 'sustain': False}
            popup.destroy()
            self.refresh_table()

        popup = tk.Toplevel(self.root)
        popup.title(f"Assign Mouse Move for {note}")
        ttk.Button(popup, text="Move Up", command=lambda: set_move('Up')).pack(padx=10, pady=5)
        ttk.Button(popup, text="Move Down", command=lambda: set_move('Down')).pack(padx=10, pady=5)
        ttk.Button(popup, text="Move Left", command=lambda: set_move('Left')).pack(padx=10, pady=5)
        ttk.Button(popup, text="Move Right", command=lambda: set_move('Right')).pack(padx=10, pady=5)

    def load_profile(self, filename=None):
        if not filename:
            filename = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
        if filename:
            try:
                with open(filename, "r") as f:
                    data = json.load(f)

                instrument = data.get("instrument")
                if not instrument:
                    messagebox.showerror("Error", "Invalid profile file: missing 'instrument'")
                    return

                # Set dropdown
                self.instrument_combo.set(instrument)

                # Store bindings
                self.profile = data.get("keybindings", {})

                # Set transposition
                trans = data.get("transposition", 0)
                self.listener.set_transposition(trans)

                self.refresh_table()
                messagebox.showinfo("Profile Loaded", f"Loaded profile for {instrument}")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading profile: {e}")

    def save_profile(self):
        instrument = self.instrument_combo.get()
        if not instrument:
            messagebox.showerror("Error", "Please select an instrument first.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"{instrument}_profile.json"
        )
        if filename:
            try:
                data = {
                    "instrument": instrument,
                    "transposition": INSTRUMENT_TRANSPOSITIONS.get(instrument, 0),
                    "keybindings": self.profile
                }

                with open(filename, "w") as f:
                    json.dump(data, f, indent=4)

                messagebox.showinfo("Profile Saved", f"Profile saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving profile: {e}")

    def load_profile_dialog(self):
        filename = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            self.load_profile(filename)

    def change_instrument(self, event):
        instrument = self.instrument_combo.get()
        transposition = INSTRUMENT_TRANSPOSITIONS.get(instrument, 0)
        self.listener.set_transposition(transposition)
        self.refresh_table()