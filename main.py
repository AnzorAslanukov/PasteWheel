from pynput.mouse import Listener, Button
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
import ui_renderer
import sys

class UIThreadBridge(QObject):
    showRequest = pyqtSignal(int, int, bool)
    hideRequest = pyqtSignal()

def debug_write(msg, append=True):
    mode = 'a' if append else 'w'
    with open('debug.txt', mode, encoding='utf-8') as f:
        f.write(msg + '\n')

debug_write("Program started", append=False)

def on_click(x, y, button, pressed):
    try:
        debug_write(f"Mouse event: {button} {'pressed' if pressed else 'released'} at ({x}, {y})")
        if pressed:
            if button in [Button.left, Button.right] and ui.window_bounds is not None:
                x1, y1, x2, y2 = ui.window_bounds
                debug_write(f"UI shown, checking if outside bounds: click ({x},{y}) in ({x1},{y1})-({x2},{y2})")
                inside = x >= x1 and x <= x2 and y >= y1 and y <= y2
                debug_write(f"Inside UI: {inside}")
                if not inside:
                    debug_write("Hiding UI")
                    bridge.hideRequest.emit()
            elif button == Button.middle:
                debug_write("Middle button pressed, showing UI")
                print("Middle mouse button has been pressed.")
                try:
                    bridge.hideRequest.emit()
                    bridge.showRequest.emit(x, y, True)
                except Exception as e:
                    debug_write(f"Error in show_window emit: {e}")
                    import traceback
                    debug_write(traceback.format_exc())
    except Exception as e:
        debug_write(f"Error in on_click: {e}")
        import traceback
        debug_write(traceback.format_exc())

app = QApplication(sys.argv)
ui = ui_renderer.UIRenderer()

bridge = UIThreadBridge()
bridge.showRequest.connect(lambda x, y, sc: ui.show_window(x, y, show_circles=sc))
bridge.hideRequest.connect(ui.hide_window)

# Start listening for mouse events
listener = Listener(on_click=on_click)
listener.start()

# Run the PyQt5 application loop
app.exec_()

# Stop the listener
listener.stop()
