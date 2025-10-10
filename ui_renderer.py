from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QIcon, QGuiApplication
from PyQt5.QtCore import Qt, QPoint, QPointF, pyqtSignal, QSize, QTimer
import math
import json

def debug_write(msg, append=True):
    mode = 'a' if append else 'w'
    with open('debug.txt', mode, encoding='utf-8') as f:
        f.write(msg + '\n')


class SettingsButton(QPushButton):
    def __init__(self, *args, tooltip_text: str = None, tooltip_delay: int = 0):
        """
        tooltip_text: optional tooltip text to show on hover
        tooltip_delay: delay in milliseconds before showing tooltip (0 -> show immediately)
        """
        super().__init__(*args)
        from PyQt5.QtWidgets import QGraphicsOpacityEffect
        self.effect = QGraphicsOpacityEffect()
        self.effect.setOpacity(0.5)
        self.setGraphicsEffect(self.effect)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(200, 200, 200, 0);
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(200, 200, 200, 255);
            }
        """)
        # Tooltip handling
        self._tooltip_text = tooltip_text
        self._tooltip_delay = int(tooltip_delay or 0)
        self._tooltip_timer = QTimer(self)
        self._tooltip_timer.setSingleShot(True)
        self._tooltip_timer.timeout.connect(self._show_tooltip_now)

    def enterEvent(self, event):
        self.effect.setOpacity(1.0)
        # Show tooltip immediately or after configured delay
        try:
            if self._tooltip_text:
                if self._tooltip_delay and self._tooltip_delay > 0:
                    self._tooltip_timer.start(self._tooltip_delay)
                else:
                    self._show_tooltip_now()
        except Exception:
            pass
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.effect.setOpacity(0.5)
        try:
            if self._tooltip_timer.isActive():
                self._tooltip_timer.stop()
            # Hide tooltip immediately when leaving
            try:
                from PyQt5.QtWidgets import QToolTip
                QToolTip.hideText()
            except Exception:
                pass
        except Exception:
            pass
        super().leaveEvent(event)

    def _show_tooltip_now(self):
        try:
            if not self._tooltip_text:
                return
            from PyQt5.QtWidgets import QToolTip
            # Show tooltip at the center of the widget
            pos = self.mapToGlobal(self.rect().center())
            QToolTip.showText(pos, self._tooltip_text, self)
        except Exception:
            pass

    def set_tooltip(self, text: str, delay: int = 0):
        """Update tooltip text and optional delay (ms)."""
        self._tooltip_text = text
        self._tooltip_delay = int(delay or 0)
        # If a timer exists, update nothing else; the new delay will be used on next hover.


class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        # Create a normal top-level window (with title bar) that stays on top.
        super().__init__(parent, Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Settings")
        # Leave blank for now per requirements
        self.setMinimumSize(400, 300)

class ToggleIconButton(SettingsButton):
    def __init__(self, *args):
        # Inherit visual and tooltip behavior from SettingsButton
        # Default tooltip will be set by the creator (UIRenderer)
        super().__init__(*args, tooltip_text=None, tooltip_delay=0)
        self.icon1 = QIcon("assets/swap_middle_mouse_button.svg")
        self.icon2 = QIcon("assets/swap_alt_plus_apostrophe.svg")
        self.current = 1
        # Keep the same style as SettingsButton; no extra styling needed here

    def toggle_icon(self):
        if self.current == 1:
            self.setIcon(self.icon2)
            self.current = 2
        else:
            self.setIcon(self.icon1)
            self.current = 1


class UIRenderer(QWidget):
    buttonClicked = pyqtSignal(str)  # Emits an id string for clicked radial buttons
    activationModeChanged = pyqtSignal(str)  # Emits 'mouse' or 'alt_backtick' when toggle changes
    closeAppRequested = pyqtSignal()  # Emits when the user clicks the close button in the UI

    def __init__(self):
        super().__init__()

        # Window properties
        # Keep frameless, on-top, translucent tool window like previous implementation
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Use 350x350 like the test.py widget to provide padding around rings
        self.setFixedSize(350, 350)
        self.hide()

        # State
        self.center = QPointF(0, 0)
        self.window_bounds = None
        self.show_circles = False  # accepted but not used (test UI draws real buttons)
        self._settings_window = None
        # Container for configured radial buttons (may be empty if no config present)
        self.buttons = []

        # Button layout configuration from test.py
        # Layer 1: min 4, max 8 (using 8 here)
        # Layer 2: min 0, max 16 (using 16 here)
        # Layer 3: min 0, max 24 (using 24 here)
        self.num_layer1 = 8
        self.num_layer2 = 16
        self.num_layer3 = 24

        # Load user button configuration and build UI accordingly
        # If no button config exists in user_config.json, the UI will be empty except for corner
        # buttons and a central "add first button".
        self._load_user_buttons()
        self._add_settings_button()
        self._add_toggle_button()
        self._add_close_button()

    # ============== UI FROM test.py (adapted to class) ==============
    def _init_radial_buttons(self):
        self.buttons = []
        button_size = 30
        button_style = "background-color: lightgray; border-radius: 15px;"
        # Center inside this 350x350 widget
        center_x = 175
        center_y = 175

        def mkbtn(x, y, layer, idx):
            btn = QPushButton(self)
            btn.setFixedSize(button_size, button_size)
            btn.setStyleSheet(button_style)
            btn.setGeometry(int(x), int(y), button_size, button_size)
            btn_id = f"L{layer}-{idx}"
            # Connect to emit our standard signal for external handling
            btn.clicked.connect(lambda _checked=False, _id=btn_id: self.buttonClicked.emit(_id))
            self.buttons.append(btn)

        # Layer 1 (radius 50)
        if self.num_layer1 > 0:
            angle_step = 360 / self.num_layer1
            for i in range(self.num_layer1):
                theta = math.radians(angle_step * i)
                x = center_x + 50 * math.cos(theta) - button_size // 2
                y = center_y + 50 * math.sin(theta) - button_size // 2
                mkbtn(x, y, 1, i)

        # Layer 2 (radius 100)
        if self.num_layer2 > 0:
            angle_step = 360 / self.num_layer2
            for i in range(self.num_layer2):
                theta = math.radians(angle_step * i)
                x = center_x + 100 * math.cos(theta) - button_size // 2
                y = center_y + 100 * math.sin(theta) - button_size // 2
                mkbtn(x, y, 2, i)

        # Layer 3 (radius 150)
        if self.num_layer3 > 0:
            angle_step = 360 / self.num_layer3
            for i in range(self.num_layer3):
                theta = math.radians(angle_step * i)
                x = center_x + 150 * math.cos(theta) - button_size // 2
                y = center_y + 150 * math.sin(theta) - button_size // 2
                mkbtn(x, y, 3, i)

    def _add_settings_button(self):
        # Settings button with immediate tooltip
        self.settings_button = SettingsButton(self, tooltip_text="Settings — open to add or configure buttons", tooltip_delay=0)
        self.settings_button.setFixedSize(30, 30)
        icon = QIcon("assets/settings_icon.svg")
        self.settings_button.setIcon(icon)
        self.settings_button.setIconSize(QSize(30, 30))
        # Top-right inside the widget with some padding
        self.settings_button.setGeometry(350 - 30 - 10, 10, 30, 30)
        self.settings_button.clicked.connect(self._open_settings_window)

    def _open_settings_window(self):
        debug_write("Opening settings window")
        if self._settings_window is None:
            self._settings_window = SettingsWindow(self)
        # Show and focus the settings window
        try:
            self._settings_window.show()
            self._settings_window.raise_()
            self._settings_window.activateWindow()
        except Exception as e:
            debug_write(f"Failed to open settings window: {e}")

    def is_point_in_ui_or_settings(self, x: int, y: int) -> bool:
        try:
            # Check main UI bounds
            if self.window_bounds is not None:
                x1, y1, x2, y2 = self.window_bounds
                if x1 <= x <= x2 and y1 <= y <= y2:
                    return True
            # Check settings window bounds (if visible)
            if self._settings_window is not None and self._settings_window.isVisible():
                try:
                    geom = self._settings_window.frameGeometry()
                except Exception:
                    geom = self._settings_window.geometry()
                if geom is not None:
                    gx, gy, gw, gh = geom.x(), geom.y(), geom.width(), geom.height()
                    if gx <= x <= gx + gw and gy <= y <= gy + gh:
                        return True
        except Exception:
            pass
        return False

    def _add_toggle_button(self):
        # Toggle button (top-left). Tooltip will be kept in sync with activation mode.
        self.toggle_button = ToggleIconButton(self)
        self.toggle_button.setFixedSize(30, 30)
        self.toggle_button.setIcon(self.toggle_button.icon1)
        self.toggle_button.setIconSize(QSize(30, 30))
        # Top-left inside the widget with some padding
        self.toggle_button.setGeometry(10, 10, 30, 30)
        self.toggle_button.clicked.connect(self._handle_toggle_clicked)
        # Default tooltip (may be updated by set_activation_mode)
        try:
            self.toggle_button.set_tooltip("Open UI with middle mouse button", 0)
        except Exception:
            pass

    def _add_close_button(self):
        # Close button placed in the lower-left corner with the same visual style as other corner buttons.
        # When clicked it will emit closeAppRequested so the main thread can stop listeners and exit.
        self.close_button = SettingsButton(self, tooltip_text="Shutdown the entire PasteWheel program", tooltip_delay=0)
        self.close_button.setFixedSize(30, 30)
        icon = QIcon("assets/close_pastewheel.svg")
        self.close_button.setIcon(icon)
        self.close_button.setIconSize(QSize(30, 30))
        # Bottom-left inside the widget with some padding
        self.close_button.setGeometry(10, 350 - 30 - 10, 30, 30)
        self.close_button.clicked.connect(self._handle_close_clicked)

    def _handle_close_clicked(self):
        debug_write("Close button clicked, emitting closeAppRequested")
        try:
            self.closeAppRequested.emit()
        except Exception as e:
            debug_write(f"Error emitting closeAppRequested: {e}")
        try:
            self.hide()
        except Exception as e:
            debug_write(f"Error hiding UI after close click: {e}")

    def _add_center_add_button(self):
        # Add a centered "add first button" when no button config exists. Uses same style as corner buttons.
        try:
            # Add a center button with a 1 second tooltip delay
            self.add_first_button = SettingsButton(self, tooltip_text="Add your first button to the UI", tooltip_delay=1000)
            self.add_first_button.setFixedSize(30, 30)
            icon = QIcon("assets/add_first_button.svg")
            self.add_first_button.setIcon(icon)
            self.add_first_button.setIconSize(QSize(30, 30))
            # Center the button inside the 350x350 widget
            cx = (self.width() - 30) // 2
            cy = (self.height() - 30) // 2
            self.add_first_button.setGeometry(cx, cy, 30, 30)
            # For now clicking the add button opens the settings window
            self.add_first_button.clicked.connect(self._open_settings_window)
            debug_write("Added center 'add first button' (tooltip delay 1000ms)")
        except Exception as e:
            debug_write(f"Error creating center add button: {e}")

    def _load_user_buttons(self):
        # Load button configuration from user_config.json. If no buttons configured, add center add button.
        try:
            cfg = {}
            try:
                with open('user_config.json', 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
            except Exception:
                cfg = {}
            buttons_cfg = cfg.get('buttons', [])
            if not buttons_cfg:
                # No configured buttons: intentionally leave radial area empty and show a center add button
                try:
                    self._add_center_add_button()
                except Exception as e:
                    debug_write(f"Failed to add center add button: {e}")
            else:
                # There is button config; build radial buttons (existing behavior)
                # For now, fallback to the standard radial initialization which creates placeholders.
                # A full mapping from config -> buttons will be implemented later.
                try:
                    self._init_radial_buttons()
                except Exception as e:
                    debug_write(f"Failed to initialize radial buttons from config: {e}")
        except Exception as e:
            debug_write(f"Error loading user buttons: {e}")

    # Mode control for toggle button / activation behavior
    def set_activation_mode(self, mode: str):
        # mode: 'mouse' or 'alt_backtick'
        if mode not in ('mouse', 'alt_backtick'):
            mode = 'mouse'
        self.activation_mode = mode
        # Set icon and internal toggle state without flipping
        if mode == 'mouse':
            self.toggle_button.setIcon(self.toggle_button.icon1)
            self.toggle_button.current = 1
            try:
                self.toggle_button.set_tooltip("Open UI with middle mouse button", 0)
            except Exception:
                pass
        else:
            self.toggle_button.setIcon(self.toggle_button.icon2)
            self.toggle_button.current = 2
            try:
                self.toggle_button.set_tooltip("Open UI with Alt+` (Alt + backtick)", 0)
            except Exception:
                pass

    def _handle_toggle_clicked(self):
        # Flip icon then emit the logical mode
        self.toggle_button.toggle_icon()
        self.activation_mode = 'mouse' if self.toggle_button.current == 1 else 'alt_backtick'
        # Update tooltip to reflect new mode
        if self.activation_mode == 'mouse':
            try:
                self.toggle_button.set_tooltip("Open UI with middle mouse button", 0)
            except Exception:
                pass
        else:
            try:
                self.toggle_button.set_tooltip("Open UI with Alt+` (Alt + backtick)", 0)
            except Exception:
                pass
        debug_write(f"Activation mode toggled to: {self.activation_mode}")
        self.activationModeChanged.emit(self.activation_mode)

    # ============== Public API (compatible with previous implementation) ==============
    def show_window(self, center_x, center_y, show_circles=False):
        # Keep the parameter for compatibility; the new UI uses physical buttons instead of drawn circles
        self.show_circles = show_circles

        debug_write(f"Showing window at ({center_x}, {center_y}), show_circles={show_circles}")
        app = QApplication.instance()
        point = QPoint(int(center_x), int(center_y))

        # Determine the screen under the click
        screen = None
        try:
            screen = QGuiApplication.screenAt(point)
        except Exception:
            screen = None

        if screen is not None:
            # Prefer available geometry to avoid taskbars
            try:
                screen_geom = screen.availableGeometry()
                debug_write(f"ScreenAt({point}) -> {screen.name()} avail-geom={screen_geom}")
            except Exception:
                screen_geom = screen.geometry()
                debug_write(f"ScreenAt({point}) -> {screen.name()} geom={screen_geom} (fallback)")
        else:
            # Fallback for older Qt APIs
            try:
                desktop = app.desktop()
                screen_idx = desktop.screenNumber(point)
                if screen_idx < 0:
                    s = app.primaryScreen()
                    screen_geom = s.availableGeometry() if s is not None else app.primaryScreen().geometry()
                    debug_write(f"screenAt None and screenNumber < 0; fallback to primary avail-geom: {screen_geom}")
                else:
                    screen_geom = desktop.availableGeometry(screen_idx)
                    debug_write(f"Using desktop screen #{screen_idx} avail-geom: {screen_geom}")
            except Exception:
                s = app.primaryScreen()
                screen_geom = s.availableGeometry() if s is not None else app.primaryScreen().geometry()
                debug_write(f"Desktop API failed; fallback to primary avail-geom: {screen_geom}")

        # Clamp center within target screen so 350x350 stays visible on that screen
        half_w = self.width() // 2  # 175
        half_h = self.height() // 2  # 175
        min_cx = screen_geom.x() + half_w
        max_cx = screen_geom.x() + screen_geom.width() - half_w
        min_cy = screen_geom.y() + half_h
        max_cy = screen_geom.y() + screen_geom.height() - half_h
        center_x = max(min_cx, min(max_cx, center_x))
        center_y = max(min_cy, min(max_cy, center_y))
        debug_write(f"Clamped center to target screen: ({center_x},{center_y}) [range x:{min_cx}-{max_cx}, y:{min_cy}-{max_cy}]")

        self.center = QPointF(center_x, center_y)
        self.window_bounds = (center_x - half_w, center_y - half_h, center_x + half_w, center_y + half_h)

        # Move and show
        self.move(int(center_x - half_w), int(center_y - half_h))
        debug_write(f"Window moved to ({center_x - half_w}, {center_y - half_h})")
        debug_write(f"Bounds set: {self.window_bounds}")
        try:
            self.update()
            self.show()
            # Ensure the native window is associated with the correct screen after show
            try:
                handle = self.windowHandle()
                if handle is not None and screen is not None:
                    handle.setScreen(screen)
                    debug_write(f"Assigned window to screen after show: {screen.name()}")
            except Exception as e:
                debug_write(f"Failed to assign window to screen after show: {e}")
            self.raise_()
            self.activateWindow()
        except Exception as e:
            debug_write(f"Error showing window: {e}")

    def hide_window(self):
        debug_write("Hiding window and settings (if open)")
        # Hide the settings window if it's visible so a click outside closes both windows
        try:
            if self._settings_window is not None and self._settings_window.isVisible():
                try:
                    self._settings_window.hide()
                    debug_write("Settings window hidden")
                except Exception as e:
                    debug_write(f"Error hiding settings window: {e}")
        except Exception:
            pass
        # Hide main UI
        try:
            self.hide()
        except Exception as e:
            debug_write(f"Error hiding main UI: {e}")
        # Keep buttons persistent; just reset transient state
        self.show_circles = False

    # Backwards-compat shim (not actively used by test UI).
    def set_buttons(self, buttons):
        # This UI builds its own QPushButtons; keeping the method for compatibility.
        debug_write("set_buttons called, but the current UI ignores external button definitions.")
