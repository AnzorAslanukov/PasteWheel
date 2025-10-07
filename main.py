from pynput.mouse import Listener, Button
from PyQt5.QtWidgets import QApplication
import ui_renderer
import sys

def on_click(x, y, button, pressed):
    if button == Button.middle and pressed:
        print("Middle mouse button has been pressed.")
        ui.hide_window()  # Hide any previous
        ui.show_window(x, y, show_circles=True)

app = QApplication(sys.argv)
ui = ui_renderer.UIRenderer()

# Start listening for mouse events
listener = Listener(on_click=on_click)
listener.start()

# Run the PyQt5 application loop
app.exec_()

# Stop the listener
listener.stop()
