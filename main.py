import tkinter as tk
from pitch_listener import PitchListener
from gui import ClarinetGUI


def main():
    root = tk.Tk()

    # Create an instance of PitchListener, passing the update_note function
    pitch_listener = PitchListener(callback=lambda pitch: gui.update_note(pitch))

    # Create the GUI with the pitch_listener instance
    gui = ClarinetGUI(root, pitch_listener)

    # Start the pitch detection
    pitch_listener.start()

    # Run the Tkinter event loop
    root.mainloop()

    # Stop the pitch detection when the GUI closes
    pitch_listener.stop()
    pitch_listener.close()


if __name__ == "__main__":
    main()
