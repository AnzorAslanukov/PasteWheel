from pynput.mouse import Listener, Button
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
import ui_renderer
import sys
from pynput import keyboard
from pynput.mouse import Controller
import json

class UIThreadBridge(QObject):
    showRequest = pyqtSignal(int, int, bool)
    hideRequest = pyqtSignal()

def debug_write(msg, append=True):
    mode = 'a' if append else 'w'
    with open('debug.txt', mode, encoding='utf-8') as f:
        f.write(msg + '\n')

debug_write("Program started", append=False)

# Load activation mode from user_config.json
CONFIG_PATH = 'user_config.json'
def load_config():
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(cfg):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        debug_write(f"Error saving config: {e}")

cfg = load_config()
activation_mode = cfg.get('activation_mode', 'mouse')
debug_write(f"Loaded activation_mode: {activation_mode}")

# Hotkey state for ALT+` chord
alt_down = False
backtick_down = False
chord_triggered = False

def on_click(x, y, button, pressed):
    try:
        debug_write(f"Mouse event: {button} {'pressed' if pressed else 'released'} at ({x}, {y})")
        if pressed:
            if button in [Button.left, Button.right] and ui.window_bounds is not None:
                inside = False
                try:
                    inside = ui.is_point_in_ui_or_settings(x, y)
                except Exception as e:
                    debug_write(f"Error checking point in ui/settings: {e}")
                    # Fallback to simple bounds check
                    try:
                        x1, y1, x2, y2 = ui.window_bounds
                        inside = x1 <= x <= x2 and y1 <= y <= y2
                    except Exception:
                        inside = False
                debug_write(f"Inside main UI or settings: {inside}")

                # Extra safeguard: if the click falls inside any top-level Qt widget (picker, other windows),
                # treat it as inside so we don't erroneously hide the main UI when user interacts with popups.
                try:
                    from PyQt5.QtWidgets import QApplication
                    app = QApplication.instance()
                    if app is not None:
                        for w in app.topLevelWidgets():
                            try:
                                # Skip the main UI widget itself if already detected
                                if w is ui:
                                    continue
                                try:
                                    g = w.frameGeometry()
                                except Exception:
                                    g = w.geometry()
                                if g is None:
                                    continue
                                if g.x() <= x <= g.x() + g.width() and g.y() <= y <= g.y() + g.height():
                                    debug_write(f"Click is inside top-level widget: {getattr(w, 'windowTitle', lambda: '')()}")
                                    inside = True
                                    break
                            except Exception:
                                continue
                except Exception:
                    pass

                if not inside:
                    debug_write("Hiding UI")
                    bridge.hideRequest.emit()
            elif button == Button.middle:
                if get_current_activation_mode() != 'mouse':
                    debug_write("Middle button pressed but activation_mode != 'mouse'; ignoring")
                else:
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

def on_key_press(key):
    # Only handle in alt_backtick mode
    global alt_down, backtick_down, chord_triggered
    try:
        if get_current_activation_mode() != 'alt_backtick':
            return
        if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
            alt_down = True
        elif isinstance(key, keyboard.KeyCode) and key.char == '`':
            backtick_down = True
        elif key == keyboard.Key.grave:
            backtick_down = True

        if alt_down and backtick_down and not chord_triggered:
            chord_triggered = True
            try:
                x, y = Controller().position
                debug_write("Alt+` chord detected, showing UI")
                bridge.hideRequest.emit()
                bridge.showRequest.emit(int(x), int(y), True)
            except Exception as e:
                debug_write(f"Error in show via hotkey: {e}")
    except Exception as e:
        debug_write(f"Error in on_key_press: {e}")

def on_key_release(key):
    global alt_down, backtick_down, chord_triggered
    try:
        if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
            alt_down = False
        elif isinstance(key, keyboard.KeyCode) and key.char == '`':
            backtick_down = False
        elif key == keyboard.Key.grave:
            backtick_down = False
        if not alt_down or not backtick_down:
            chord_triggered = False
    except Exception as e:
        debug_write(f"Error in on_key_release: {e}")

app = QApplication(sys.argv)
ui = ui_renderer.UIRenderer()

bridge = UIThreadBridge()
bridge.showRequest.connect(lambda x, y, sc: ui.show_window(x, y, show_circles=sc))
bridge.hideRequest.connect(ui.hide_window)

# Helper to retrieve the current activation mode from UI if available. This ensures listeners
# always consult the live UI state (the toggle) rather than relying only on the module-level
# variable which can become stale across threads.
def get_current_activation_mode():
    try:
        return ui.activation_mode
    except Exception:
        return activation_mode

# Initialize UI activation mode from config and persist changes on toggle
try:
    ui.set_activation_mode(activation_mode)
except Exception as e:
    debug_write(f"Failed to set UI activation mode: {e}")

def on_activation_mode_changed(mode):
    global activation_mode, alt_down, backtick_down, chord_triggered
    activation_mode = mode
    c = load_config()
    c['activation_mode'] = activation_mode
    save_config(c)
    chord_triggered = False  # reset gating so a held key doesn't retrigger
    debug_write(f"Persisted activation_mode: {activation_mode}")

ui.activationModeChanged.connect(on_activation_mode_changed)

def on_close_requested():
    # Stop background listeners and terminate the application when UI requests close.
    # Use globals so the handler can access the listener objects created later.
    global listener, kb_listener
    debug_write("Close requested from UI; stopping listeners and exiting")
    try:
        if 'listener' in globals() and listener is not None:
            listener.stop()
            debug_write("Mouse listener stopped")
    except Exception as e:
        debug_write(f"Error stopping mouse listener: {e}")
    try:
        if 'kb_listener' in globals() and kb_listener is not None:
            kb_listener.stop()
            debug_write("Keyboard listener stopped")
    except Exception as e:
        debug_write(f"Error stopping keyboard listener: {e}")
    try:
        bridge.hideRequest.emit()
    except Exception as e:
        debug_write(f"Error emitting hideRequest during close: {e}")
    try:
        app.quit()
        debug_write("QApplication quit called")
    except Exception as e:
        debug_write(f"Error quitting QApplication: {e}")
    try:
        sys.exit(0)
    except SystemExit:
        pass
    except Exception as e:
        debug_write(f"Error calling sys.exit: {e}")

ui.closeAppRequested.connect(on_close_requested)

# Start global keyboard listener for ALT+` mode
kb_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
kb_listener.start()

# Start listening for mouse events
listener = Listener(on_click=on_click)
listener.start()

# Run the PyQt5 application loop
app.exec_()

# Stop the listener
listener.stop()
kb_listener.stop()
