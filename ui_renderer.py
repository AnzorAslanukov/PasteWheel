from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QIcon, QGuiApplication
from PyQt5.QtCore import Qt, QPoint, QPointF, pyqtSignal, QSize, QTimer, QEvent
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


class RadialPreview(QWidget):
    """
    Lightweight preview widget used inside Settings > Buttons.
    Draws concentric ring outlines and a central preview button (green by default).
    """
    def __init__(self, parent=None, size: int = 300):
        super().__init__(parent)
        self.setFixedSize(size, size)
        # Ensure the preview and its children receive hover/mouse events immediately
        try:
            self.setAttribute(Qt.WA_Hover, True)
            self.setMouseTracking(True)
        except Exception:
            pass

        # Create a center preview button with green/grey icons that toggle on click
        try:
            # Use SettingsButton so tooltip timing/behavior and hover opacity are consistent with other corner buttons.
            self.center_btn = SettingsButton(self, tooltip_text="Clicking this button will add new buttons to the main PasteWheel UI.", tooltip_delay=0)
            btn_size = 30
            self.center_btn.setFixedSize(btn_size, btn_size)
            self.icon_green = QIcon("assets/add_new_button_green.svg")
            self.icon_grey = QIcon("assets/add_new_button_grey.svg")
            self.center_btn.setIcon(self.icon_green)
            self.center_btn.setIconSize(QSize(btn_size, btn_size))

            # Make the button visually icon-only (no outline) and transparent background; add hover background.
            # SettingsButton already provides an opacity effect on hover; additionally set a hover background color.
            try:
                self.center_btn.setFlat(True)
                self.center_btn.setStyleSheet(
                    "border: none; background: transparent;"
                    "QPushButton:hover { background-color: #f0f0f0; border-radius: 15px; }"
                )
            except Exception:
                pass

            # Ensure tooltips use white background + black text (global style for this process)
            try:
                from PyQt5.QtWidgets import QToolTip
                QToolTip.setStyleSheet("QToolTip { background-color: white; color: black; border: 1px solid #d0d0d0; padding: 5px; }")
            except Exception:
                pass

            # Position the button in the visual center of this preview widget
            cx = (self.width() - btn_size) // 2
            cy = (self.height() - btn_size) // 2
            self.center_btn.setGeometry(cx, cy, btn_size, btn_size)
            self._is_green = True
            self.center_btn.clicked.connect(self._toggle_center_icon)
            # Container for dynamically added preview layer-1 buttons
            self.layer1_buttons = []
            # Keep references to per-button settings windows so they are not GC'd
            self._button_settings_windows = {}

            # Load existing button config and render layer-1 buttons inside the preview:
            try:
                cfg = {}
                try:
                    with open('user_config.json', 'r', encoding='utf-8') as f:
                        cfg = json.load(f)
                except Exception:
                    cfg = {}
                buttons_cfg = cfg.get('buttons', [])
                # Helper to parse IDs like "B2L1" -> (2,1)
                def _parse_id(bid: str):
                    try:
                        if not isinstance(bid, str):
                            return None
                        if bid.startswith('B') and 'L' in bid:
                            parts = bid[1:].split('L')
                            num = int(parts[0])
                            layer = int(parts[1])
                            return num, layer
                    except Exception:
                        pass
                    return None

                # Create up to num_layer1 preview slots (use same layout as main UI layer1)
                preview_btn_size = 24
                center_pt = self.rect().center()
                cx = center_pt.x()
                cy = center_pt.y()
                radius = int((min(self.width(), self.height()) // 2 - 10) * 0.33)
                angle_step = 360 / max(1, self.num_layer1)

                # Build occupied mapping for layer-1 from config (slot_idx -> entry)
                occupied = {}
                for entry in buttons_cfg:
                    bid = entry.get('id')
                    parsed = _parse_id(bid)
                    if parsed is None:
                        continue
                    num, layer = parsed
                    if layer != 1:
                        continue
                    idx = max(0, min(self.num_layer1 - 1, num - 1))
                    occupied[idx] = entry

                # Render configured buttons equidistantly so positions match the main UI placement rules.
                try:
                    entries = sorted(occupied.items(), key=lambda t: t[0])  # list of (slot_idx, entry)
                    k = len(entries)
                    if k > 0:
                        start_angle = -90.0  # first at 12 o'clock
                        angle_step_cfg = 360.0 / float(k)
                        for j, (orig_idx, entry) in enumerate(entries):
                            theta = math.radians(start_angle + j * angle_step_cfg)
                            x = int(cx + radius * math.cos(theta) - preview_btn_size // 2)
                            y = int(cy + radius * math.sin(theta) - preview_btn_size // 2)
                            try:
                                gb = QPushButton(self)
                                gb.setFixedSize(preview_btn_size, preview_btn_size)
                                gb.setStyleSheet("background-color: lightgray; border-radius: 12px; border: none;")
                                gb.setGeometry(x, y, preview_btn_size, preview_btn_size)
                                # clicking does nothing for now
                                gb.clicked.connect(lambda _checked=False: None)
                                gb.show()
                                self.layer1_buttons.append(gb)
                            except Exception:
                                pass
                    # Do not render add-new placeholders here by default.
                    # The central preview toggle will create add-new preview buttons when activated.
                except Exception as e:
                    debug_write(f"RadialPreview initial layer1 render error (placement): {e}")
            except Exception as e:
                debug_write(f"RadialPreview initial layer1 render error: {e}")

            try:
                # Install an event filter so we can reliably show the tooltip and
                # toggle hover styling even if the widget hierarchy interferes.
                self.center_btn.installEventFilter(self)
            except Exception:
                pass
        except Exception as e:
            debug_write(f"RadialPreview init error: {e}")

    def _toggle_center_icon(self):
        try:
            self._is_green = not self._is_green
            if self._is_green:
                # Switch to green center icon and remove any preview layer-1 buttons
                self.center_btn.setIcon(self.icon_green)
                try:
                    for b in self.layer1_buttons:
                        try:
                            b.hide()
                            b.setParent(None)
                            b.deleteLater()
                        except Exception:
                            pass
                    self.layer1_buttons = []
                except Exception as e:
                    debug_write(f"Error removing layer1 preview buttons: {e}")
            else:
                # Switch to grey center icon and create 8 placeholder buttons in layer 1
                self.center_btn.setIcon(self.icon_grey)
                try:
                    # Clean any existing (defensive)
                    for b in self.layer1_buttons:
                        try:
                            b.hide()
                            b.setParent(None)
                            b.deleteLater()
                        except Exception:
                            pass
                    self.layer1_buttons = []

                    btn_size = 24
                    center = self.rect().center()
                    cx = center.x()
                    cy = center.y()
                    max_radius = min(self.width(), self.height()) // 2 - 10
                    r = int(max_radius * 0.33)
                    angle_step = 360 / 8

                    # Define a small PreviewButton subclass so enter/leave events reliably change background.
                    class PreviewButton(QPushButton):
                        def __init__(self, *a, **kw):
                            super().__init__(*a, **kw)
                            try:
                                self.setFlat(True)
                                # Default transparent background
                                self.setStyleSheet("border: none; background: transparent;")
                                # Ensure hover events are enabled
                                self.setAttribute(Qt.WA_Hover, True)
                                self.setMouseTracking(True)
                            except Exception:
                                pass

                        def enterEvent(self, ev):
                            try:
                                self.setStyleSheet("border: none; background: #e8e8e8; border-radius: 12px;")
                            except Exception:
                                pass
                            super().enterEvent(ev)

                        def leaveEvent(self, ev):
                            try:
                                self.setStyleSheet("border: none; background: transparent;")
                            except Exception:
                                pass
                            super().leaveEvent(ev)

                    for i in range(8):
                        theta = math.radians(angle_step * i)
                        x = int(cx + r * math.cos(theta) - btn_size // 2)
                        y = int(cy + r * math.sin(theta) - btn_size // 2)
                        b = PreviewButton(self)
                        b.setFixedSize(btn_size, btn_size)
                        try:
                            icon = QIcon("assets/add_new_button_green.svg")
                            b.setIcon(icon)
                            b.setIconSize(QSize(btn_size, btn_size))
                        except Exception:
                            pass
                        b.setGeometry(x, y, btn_size, btn_size)
                        # Open per-button settings window (creates a blank window for this preview button)
                        b.clicked.connect(lambda _checked=False, _idx=i: self._open_button_settings(_idx))
                        try:
                            # Install event filter so RadialPreview.eventFilter can also handle hover as a fallback
                            b.installEventFilter(self)
                        except Exception:
                            pass
                        b.show()
                        self.layer1_buttons.append(b)
                except Exception as e:
                    debug_write(f"Error creating layer1 preview buttons: {e}")
        except Exception as e:
            debug_write(f"RadialPreview toggle error: {e}")

    def eventFilter(self, obj, event):
        """
        Handle Enter/Leave events on the center button and layer-1 preview buttons to show/hide
        the tooltip and to apply the light-grey hover background reliably.
        """
        try:
            from PyQt5.QtWidgets import QToolTip

            # Center button handling (tooltip + hover background)
            if obj is self.center_btn:
                if event.type() == QEvent.Enter:
                    # Show tooltip at the button center
                    try:
                        pos = self.center_btn.mapToGlobal(self.center_btn.rect().center())
                        QToolTip.showText(pos, getattr(self.center_btn, "_tooltip_text", "") or "", self.center_btn)
                    except Exception:
                        pass
                    # Apply explicit hover background so stylesheet rules render
                    try:
                        self.center_btn.setStyleSheet("border: none; background: #f0f0f0; border-radius: 15px;")
                    except Exception:
                        pass
                    return True
                elif event.type() == QEvent.Leave:
                    try:
                        QToolTip.hideText()
                    except Exception:
                        pass
                    # Restore original transparent style while keeping hover rule
                    try:
                        self.center_btn.setStyleSheet(
                            "border: none; background: transparent;"
                            "QPushButton:hover { background-color: #f0f0f0; border-radius: 15px; }"
                        )
                    except Exception:
                        pass
                    return True

            # Layer-1 preview buttons: change background on hover (and leave)
            if hasattr(self, "layer1_buttons") and obj in self.layer1_buttons:
                try:
                    # Treat both Enter/HoverEnter as hover start, and Leave/HoverLeave as hover end.
                    if event.type() in (QEvent.Enter, QEvent.HoverEnter):
                        try:
                            obj.setStyleSheet("border: none; background: #e8e8e8; border-radius: 12px;")
                        except Exception:
                            pass
                        return True
                    elif event.type() in (QEvent.Leave, QEvent.HoverLeave):
                        try:
                            obj.setStyleSheet(
                                "border: none; background: transparent;"
                                "QPushButton:hover { background-color: #e8e8e8; border-radius: 12px; }"
                            )
                        except Exception:
                            pass
                        return True
                except Exception:
                    pass
        except Exception:
            pass

        # Provide a helper to open a blank settings window for a specific preview button.
        def _open_button_settings_inner(idx):
            try:
                win = self._button_settings_windows.get(idx)
                if win is None or not win.isVisible():
                    # Create the per-button settings window as a child/owned window of the main Settings window
                    # so closing it does NOT quit the application or close the main Settings window.
                    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
                    parent_window = self.window() if hasattr(self, "window") else None
                    try:
                        win = QWidget(parent_window, Qt.Window | Qt.WindowStaysOnTopHint)
                    except Exception:
                        # Fallback to no-parent top-level if something fails
                        win = QWidget()
                    # Prevent this per-button settings window from causing the whole application
                    # to quit when it is closed (don't trigger quitOnLastWindowClosed).
                    try:
                        win.setAttribute(Qt.WA_QuitOnClose, False)
                    except Exception:
                        pass
                    win.setWindowTitle(f"Button Settings — L1-{idx}")
                    win.setMinimumSize(300, 200)
                    # Add a small placeholder label so the window is not completely empty
                    try:
                        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QCheckBox, QPushButton
                        layout = QVBoxLayout(win)
                        layout.addWidget(QLabel(f"Settings for button L1-{idx}"))
                        # Two-way toggle (Parent <-> Child). Default checked = Parent.
                        try:
                            toggle = QCheckBox("Parent (checked) / Child (unchecked)")
                            toggle.setChecked(True)
                            layout.addWidget(toggle)
                        except Exception:
                            pass

                        # Save button: persists minimal config (id and state) into user_config.json
                        try:
                            save_btn = QPushButton("Save", win)
                            def _save_button_config():
                                try:
                                    btn_id = f"B{idx+1}L1"
                                    state = "parent" if toggle.isChecked() else "child"
                                    cfg = {}
                                    try:
                                        with open('user_config.json', 'r', encoding='utf-8') as f:
                                            cfg = json.load(f)
                                    except Exception:
                                        cfg = {}
                                    buttons = cfg.get('buttons', [])
                                    # Remove any existing entry with same id
                                    try:
                                        buttons = [b for b in buttons if b.get('id') != btn_id]
                                    except Exception:
                                        buttons = buttons or []
                                    # Append minimal config (keep other keys empty for now)
                                    buttons.append({
                                        "id": btn_id,
                                        "state": state,
                                        "parent": None
                                    })
                                    cfg['buttons'] = buttons
                                    with open('user_config.json', 'w', encoding='utf-8') as f:
                                        json.dump(cfg, f, ensure_ascii=False, indent=2)
                                    debug_write(f"Saved button config: {btn_id} state={state}")
                                except Exception as e:
                                    debug_write(f"Error saving button config for {idx}: {e}")
                            save_btn.clicked.connect(_save_button_config)
                            layout.addWidget(save_btn)
                        except Exception:
                            pass

                        win.setLayout(layout)
                    except Exception:
                        pass
                    self._button_settings_windows[idx] = win
                try:
                    win.show()
                    win.raise_()
                    win.activateWindow()
                except Exception:
                    pass
            except Exception as e:
                debug_write(f"Error opening button settings window for idx {idx}: {e}")

        # Bind the helper as an instance method so it can be called from button callbacks
        try:
            setattr(self, "_open_button_settings", _open_button_settings_inner)
        except Exception:
            pass

        return super().eventFilter(obj, event)

    def paintEvent(self, event):
        try:
            from PyQt5.QtGui import QPainter, QPen, QColor
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            # Subtle outline color and width to indicate rings without filling
            pen = QPen(QColor(160, 160, 160))
            pen.setWidth(2)
            painter.setPen(pen)

            rect = self.rect()
            center = rect.center()
            # Radii chosen to be visually similar to the main UI proportions
            max_radius = min(rect.width(), rect.height()) // 2 - 10
            # Use three concentric rings
            radii = [int(max_radius * 0.33), int(max_radius * 0.66), int(max_radius * 0.95)]
            for r in radii:
                painter.drawEllipse(center, r, r)

            painter.end()
        except Exception as e:
            debug_write(f"RadialPreview paint error: {e}")

class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        # Create a normal top-level window (with title bar) that stays on top.
        super().__init__(parent, Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 360)

        # Lazy/import inside ctor to avoid changing top-level imports
        from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QScrollArea, QWidget as QtWidget

        # Create a tab widget containing General + Layer tabs (Layer 1, Layer 2, Layer 3)
        self.tabs = QTabWidget(self)

        # General tab (left empty per user request)
        general_tab = QWidget()

        # Helper to build a layer tab containing N label+button rows.
        # Each "Configure" button opens a small per-button settings window (empty for now).
        def _build_layer_tab(count: int, layer_num: int):
            container = QtWidget()
            layout = QVBoxLayout(container)
            # Use a scroll area to keep the tab usable when there are many rows
            scroll = QScrollArea(container)
            scroll.setWidgetResizable(True)
            content = QtWidget()
            content_layout = QVBoxLayout(content)
            content.setLayout(content_layout)

            for i in range(1, count + 1):
                row = QHBoxLayout()
                lbl = QLabel(f"Button {i}")
                cfg_btn = QPushButton("Configure")

                # Create a per-button settings window when Configure is clicked.
                # Capture layer_num and i using a closure to avoid late-binding issues.
                def _make_open(layer_n, idx_n):
                    def _open(_checked=False):
                        try:
                            # Parent the new window to the SettingsWindow so closing it won't quit the app.
                            parent_window = self
                            try:
                                win = QWidget(parent_window, Qt.Window | Qt.WindowStaysOnTopHint)
                            except Exception:
                                win = QWidget()
                            # Prevent this per-button settings window from causing the whole application to quit
                            try:
                                win.setAttribute(Qt.WA_QuitOnClose, False)
                            except Exception:
                                pass
                            # Name the window after the button and layer number with "Settings"
                            win.setWindowTitle(f"Button L{layer_n}-{idx_n} Settings")
                            win.setMinimumSize(300, 200)
                            # Empty layout for now
                            try:
                                from PyQt5.QtWidgets import QVBoxLayout
                                win.setLayout(QVBoxLayout())
                            except Exception:
                                pass
                            try:
                                win.show()
                                win.raise_()
                                win.activateWindow()
                            except Exception:
                                pass
                        except Exception as e:
                            debug_write(f"Failed to open per-button settings window L{layer_n}-{idx_n}: {e}")
                    return _open

                cfg_btn.clicked.connect(_make_open(layer_num, i))

                row.addWidget(lbl)
                row.addStretch(1)
                row.addWidget(cfg_btn)
                content_layout.addLayout(row)

            # Add stretch so rows align to top
            content_layout.addStretch(1)
            scroll.setWidget(content)
            layout.addWidget(scroll)
            return container

        # Layer tabs with label-button pairs
        layer1_tab = _build_layer_tab(8, 1)
        layer2_tab = _build_layer_tab(16, 2)
        layer3_tab = _build_layer_tab(24, 3)

        # Add tabs in the desired order
        self.tabs.addTab(general_tab, "General")
        self.tabs.addTab(layer1_tab, "Layer 1")
        self.tabs.addTab(layer2_tab, "Layer 2")
        self.tabs.addTab(layer3_tab, "Layer 3")

        # Main layout for the settings window
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

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

    def _open_settings_window(self, default_tab=None):
        debug_write("Opening settings window")
        if self._settings_window is None:
            self._settings_window = SettingsWindow(self)

        # If a default tab name or index was provided, attempt to set it before showing.
        try:
            if default_tab is not None:
                try:
                    # Allow either an integer index or a tab text (e.g., "Buttons")
                    if isinstance(default_tab, int):
                        idx = int(default_tab)
                    else:
                        idx = None
                        for i in range(self._settings_window.tabs.count()):
                            try:
                                if self._settings_window.tabs.tabText(i) == str(default_tab):
                                    idx = i
                                    break
                            except Exception:
                                continue
                        # Fallback: try a case-insensitive partial match
                        if idx is None:
                            for i in range(self._settings_window.tabs.count()):
                                try:
                                    if str(default_tab).lower() in self._settings_window.tabs.tabText(i).lower():
                                        idx = i
                                        break
                                except Exception:
                                    continue
                    if idx is not None:
                        try:
                            self._settings_window.tabs.setCurrentIndex(idx)
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

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
            # For now clicking the add button opens the settings window and selects the Layer 1 tab
            self.add_first_button.clicked.connect(lambda _checked=False: self._open_settings_window("Layer 1"))
            debug_write("Added center 'add first button' (tooltip delay 1000ms)")
        except Exception as e:
            debug_write(f"Error creating center add button: {e}")

    def _load_user_buttons(self):
        # Load button configuration from user_config.json and build main UI layer buttons.
        # If no config exists, show the center add button (legacy behavior).
        try:
            cfg = {}
            try:
                with open('user_config.json', 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
            except Exception:
                cfg = {}
            buttons_cfg = cfg.get('buttons', [])

            # Helper to parse IDs like "B2L1" -> (2,1)
            def _parse_id(bid: str):
                try:
                    if not isinstance(bid, str):
                        return None
                    if bid.startswith('B') and 'L' in bid:
                        parts = bid[1:].split('L')
                        num = int(parts[0])
                        layer = int(parts[1])
                        return num, layer
                except Exception:
                    pass
                return None

            if not buttons_cfg:
                # No configured buttons: intentionally leave radial area empty and show a center add button
                try:
                    self._add_center_add_button()
                except Exception as e:
                    debug_write(f"Failed to add center add button: {e}")
                return

            # There is button config -> render layer 1 in the main UI as grey circles for configured entries
            try:
                # Clear any existing self.buttons if present
                try:
                    for b in getattr(self, 'buttons', []):
                        try:
                            b.hide()
                            b.setParent(None)
                            b.deleteLater()
                        except Exception:
                            pass
                except Exception:
                    pass
                self.buttons = []

                # Determine center used elsewhere in this widget (matches _init_radial_buttons layout)
                center_x = 175
                center_y = 175
                button_size = 30

                # Compute occupied indices for layer 1 from config
                occupied = {}
                for entry in buttons_cfg:
                    bid = entry.get('id')
                    parsed = _parse_id(bid)
                    if parsed is None:
                        continue
                    num, layer = parsed
                    if layer == 1:
                        idx = max(0, min(self.num_layer1 - 1, num - 1))
                        occupied[idx] = entry

                # Place configured layer-1 buttons around radius 50.
                # Buttons are positioned equidistantly based on how many configured entries exist
                # in the layer (so N buttons will be spaced by 360/N degrees, with the first at 12 o'clock).
                try:
                    radius = 50
                    # Build a stable ordered list of configured entries for this layer.
                    # occupied maps computed slot idx -> entry; sort by that computed idx so placement is deterministic.
                    entries = sorted(occupied.items(), key=lambda t: t[0])  # list of (slot_idx, entry)
                    k = len(entries)
                    if k == 0:
                        # Nothing to render for this layer
                        pass
                    else:
                        start_angle = -90.0  # place first button at 12 o'clock
                        angle_step = 360.0 / float(k)
                        for j, (orig_idx, entry) in enumerate(entries):
                            theta = math.radians(start_angle + j * angle_step)
                            x = int(center_x + radius * math.cos(theta) - button_size // 2)
                            y = int(center_y + radius * math.sin(theta) - button_size // 2)
                            try:
                                gb = QPushButton(self)
                                gb.setFixedSize(button_size, button_size)
                                gb.setStyleSheet("background-color: lightgray; border-radius: 15px; border: none;")
                                gb.setGeometry(x, y, button_size, button_size)
                                # no-op on click for now (placeholder)
                                gb.clicked.connect(lambda _checked=False: None)
                                gb.show()
                                self.buttons.append(gb)
                            except Exception as e:
                                debug_write(f"Error creating configured main UI button at slot {orig_idx}: {e}")
                except Exception as e:
                    debug_write(f"Error rendering configured layer-1 buttons: {e}")
            except Exception as e:
                debug_write(f"Failed to render main UI layer1 from config: {e}")

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
