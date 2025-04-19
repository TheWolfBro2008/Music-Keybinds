import tkinter as tk
from pitch_listener import PitchListener
from gui import ClarinetGUI
from instrument import INSTRUMENTS


def main():
    root = tk.Tk()

    # Default instrument
    current_instrument = INSTRUMENTS["Bb Clarinet"]

    # Create pitch listener with transposition from instrument
    pitch_listener = PitchListener(
        callback=None,  # We'll set this after GUI is created
        transpose_semitones=current_instrument["transpose"]
    )

    gui = ClarinetGUI(root, pitch_listener)
    pitch_listener.callback = lambda pitch: gui.update_note(pitch)

    pitch_listener.start()
    root.mainloop()
    pitch_listener.stop()
    pitch_listener.close()


if __name__ == "__main__":
    main()
