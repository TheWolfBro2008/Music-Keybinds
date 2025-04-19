import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import keyboard  # For simulating key presses
import pyautogui  # For mouse click simulation


class ClarinetGUI:
    def __init__(self, root, pitch_listener, default_profile='profiles/default.json'):
        self.root = root
        self.root.title("Clarinet Input Mapper")
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
        self.visual_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        ttk.Label(frame, text="Mapped Key:").grid(row=1, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.mapped_key, font=("Arial", 14)).grid(row=1, column=1, sticky="w")

        self.tree = ttk.Treeview(frame, columns=('Note', 'Key'), show='headings')
        self.tree.heading('Note', text='Note')
        self.tree.heading('Key', text='Key')
        self.tree.grid(row=2, column=0, columnspan=2)

        self.tree.bind("<Double-1>", self.edit_key)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Start", command=self.listener.start).grid(row=0, column=0)
        ttk.Button(button_frame, text="Stop", command=self.listener.stop).grid(row=0, column=1)
        ttk.Button(button_frame, text="Save Profile", command=self.save_profile).grid(row=0, column=2)
        ttk.Button(button_frame, text="Load Profile", command=self.load_profile_dialog).grid(row=0, column=3)
        ttk.Button(button_frame, text="Assign Mouse Click", command=self.assign_mouse_click).grid(row=1, column=0, columnspan=4)

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

        mapped_key = self.profile.get(note)
        if mapped_key:
            self.mapped_key.set(mapped_key)
            self.trigger_action(mapped_key)
        else:
            self.mapped_key.set("---")

        self.refresh_table()

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for note in ['E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3',
                     'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4',
                     'C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5',
                     'C6', 'C#6', 'D6', 'D#6', 'E6', 'F6', 'F#6', 'G6', 'G#6', 'A6', 'A#6', 'B6',
                     'C7']:
            key = self.profile.get(note, '')
            self.tree.insert("", "end", values=(note, key))

    def trigger_action(self, key):
        if key.startswith("Mouse"):
            button = key.split(":")[1].lower()
            pyautogui.click(button=button)
        else:
            keyboard.press(key)
            keyboard.release(key)

    def edit_key(self, event):
        selected = self.tree.selection()[0]
        note = self.tree.item(selected)['values'][0]

        def set_key(event):
            self.profile[note] = event.char
            popup.destroy()
            self.refresh_table()

        popup = tk.Toplevel(self.root)
        popup.title(f"Set key for {note}")
        ttk.Label(popup, text=f"Press a key to assign for {note}:").pack(padx=10, pady=10)
        popup.bind("<Key>", set_key)

    def assign_mouse_click(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Note Selected", "Please select a note from the list first.")
            return

        note = self.tree.item(selected[0])['values'][0]

        def set_click(button_type):
            self.profile[note] = f"Mouse:{button_type}"
            popup.destroy()
            self.refresh_table()

        popup = tk.Toplevel(self.root)
        popup.title("Assign Mouse Click")

        ttk.Label(popup, text=f"Assign mouse click for {note}").pack(padx=10, pady=10)
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Left Click", command=lambda: set_click("Left")).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Right Click", command=lambda: set_click("Right")).grid(row=0, column=1, padx=5)

    def save_profile(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        with open(path, 'w') as f:
            json.dump(self.profile, f, indent=4)
        messagebox.showinfo("Saved", f"Profile saved to {path}")

    def load_profile_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            self.load_profile(path)

    def load_profile(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.profile = json.load(f)
        else:
            self.profile = {}
        self.refresh_table()
