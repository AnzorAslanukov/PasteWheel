from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QIcon, QGuiApplication
from PyQt5.QtCore import Qt, QPoint, QPointF, pyqtSignal, QSize, QTimer, QEvent
import math
import json
import time

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
                            # Build a minimal layout: Label input (max 3 chars), Parent/Child toggle + Save button (no-op for now)
                            try:
                                from PyQt5.QtWidgets import QVBoxLayout, QCheckBox, QPushButton, QSpacerItem, QSizePolicy, QLineEdit, QLabel
                                layout = QVBoxLayout()

                                # Label input (max 3 chars)
                                try:
                                    label_row = QLineEdit()
                                    label_row.setMaxLength(3)
                                    label_row.setPlaceholderText("Label (max 3 chars)")
                                    # Wrap with a small QLabel above the input for clarity
                                    layout.addWidget(QLabel("Label:"))
                                    layout.addWidget(label_row)
                                    # Alternative input: emoji/emoticon button
                                    try:
                                        layout.addWidget(QLabel("or"))
                                        emoji_btn = QPushButton("😀 Emoji/Emoticon")
                                        # Emoji display label (will show the selected emoji)
                                        try:
                                            emoji_display = QLabel("")
                                            emoji_display.setAlignment(Qt.AlignCenter)
                                        except Exception:
                                            emoji_display = QLabel("")
                                        layout.addWidget(emoji_btn)
                                        layout.addWidget(emoji_display)

                                        # Open an emoji picker window when emoji_btn is clicked
                                        try:
                                            def _open_emoji_picker():
                                                try:
                                                    from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
                                                    import unicodedata as _unicodedata
                                                    # Try to import the optional 'emoji' library; if not present we'll fall back to a small curated set
                                                    try:
                                                        import emoji as _emoji_lib
                                                        has_emoji_lib = True
                                                    except Exception:
                                                        _emoji_lib = None
                                                        has_emoji_lib = False

                                                    picker = QWidget(None, Qt.Window | Qt.WindowStaysOnTopHint)
                                                    picker.setWindowTitle("Emoji Picker")
                                                    picker.setMinimumSize(300, 400)
                                                    try:
                                                        picker.setAttribute(Qt.WA_QuitOnClose, False)
                                                    except Exception:
                                                        pass
                                                    # Ensure closing the picker via the titlebar X does not propagate closes to other windows.
                                                    # Intercept the closeEvent to hide + schedule deletion instead of allowing a default close.
                                                    try:
                                                        def _picker_close_event(event):
                                                            try:
                                                                picker.hide()
                                                            except Exception:
                                                                pass
                                                            try:
                                                                picker.deleteLater()
                                                            except Exception:
                                                                pass
                                                            try:
                                                                event.ignore()
                                                            except Exception:
                                                                pass
                                                        picker.closeEvent = _picker_close_event
                                                    except Exception:
                                                        pass

                                                    main_layout = QVBoxLayout(picker)

                                                    # Search bar
                                                    search = QLineEdit(picker)
                                                    search.setPlaceholderText("Search emoji by keyword...")
                                                    main_layout.addWidget(search)

                                                    # Category toggle buttons - stacked into two rows of five.
                                                    # When toggled, these will filter which emojis are shown.
                                                    cat_buttons = []
                                                    try:
                                                        from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
                                                        cat_container = QWidget(picker)
                                                        v_cat_layout = QVBoxLayout(cat_container)
                                                        v_cat_layout.setContentsMargins(0, 0, 0, 0)
                                                        v_cat_layout.setSpacing(6)
                                                        categories = [
                                                            "Smileys & Emotion",
                                                            "People & Body",
                                                            "Animals & Nature",
                                                            "Food & Drink",
                                                            "Travel & Places",
                                                            "Activities",
                                                            "Objects",
                                                            "Symbols",
                                                            "Flags",
                                                            "Kaomoji / Emoticons"
                                                        ]
                                                        row1 = QHBoxLayout()
                                                        row1.setContentsMargins(0, 0, 0, 0)
                                                        row1.setSpacing(6)
                                                        row2 = QHBoxLayout()
                                                        row2.setContentsMargins(0, 0, 0, 0)
                                                        row2.setSpacing(6)
                                                        for idx, cname in enumerate(categories):
                                                            try:
                                                                btn = QPushButton(cname)
                                                                btn.setCheckable(True)
                                                                btn.setFixedHeight(26)
                                                                # placeholder handler; real filtering wired below
                                                                cat_buttons.append((cname, btn))
                                                                if idx < 5:
                                                                    row1.addWidget(btn)
                                                                else:
                                                                    row2.addWidget(btn)
                                                            except Exception:
                                                                pass
                                                        v_cat_layout.addLayout(row1)
                                                        v_cat_layout.addLayout(row2)
                                                        main_layout.addWidget(cat_container)
                                                    except Exception:
                                                        # If anything goes wrong adding category buttons, continue without them
                                                        cat_buttons = []

                                                    # List of emoji results
                                                    list_w = QListWidget(picker)
                                                    list_w.setUniformItemSizes(True)
                                                    main_layout.addWidget(list_w)

                                                    # Build emoji list (try library -> fallback curated list)
                                                    if has_emoji_lib:
                                                        try:
                                                            all_emojis = list(_emoji_lib.EMOJI_DATA.keys())
                                                        except Exception:
                                                            all_emojis = []
                                                    else:
                                                        # Curated fallback emoji list (common emojis)
                                                        all_emojis = [
                                                            "😀","😃","😄","😁","😆","😉","😊","🙂","🙃","😍",
                                                            "😘","😜","🤪","🤔","😴","😎","🤩","😇","🤖","👍",
                                                            "👎","🙌","👏","🙏","🔥","⭐","💡","🎉","💯","✔️"
                                                        ]

                                                    # Simple categorizer based on emoji names / unicode name keywords
                                                    def categorize_emoji(ch: str, name: str):
                                                        name_l = (name or "").lower()
                                                        cats = []
                                                        # Smileys & Emotion
                                                        if any(k in name_l for k in ("face", "smile", "grin", "sad", "cry", "angry", "laugh", "love", "blush", "smiling")):
                                                            cats.append("Smileys & Emotion")
                                                        # People & Body
                                                        if any(k in name_l for k in ("person", "man", "woman", "boy", "girl", "hand", "people", "person")):
                                                            cats.append("People & Body")
                                                        # Animals & Nature
                                                        if any(k in name_l for k in ("cat", "dog", "animal", "rabbit", "bird", "fish", "cow", "horse", "paw", "bear", "monkey")):
                                                            cats.append("Animals & Nature")
                                                        # Food & Drink
                                                        if any(k in name_l for k in ("food", "drink", "beverage", "apple", "pizza", "burger", "coffee", "tea", "cake", "wine", "fork", "spoon")):
                                                            cats.append("Food & Drink")
                                                        # Travel & Places
                                                        if any(k in name_l for k in ("car", "plane", "airplane", "train", "ship", "house", "building", "mountain", "beach", "hotel", "road")):
                                                            cats.append("Travel & Places")
                                                        # Activities
                                                        if any(k in name_l for k in ("ball", "sport", "guitar", "music", "trophy", "game", "medal")):
                                                            cats.append("Activities")
                                                        # Objects
                                                        if any(k in name_l for k in ("phone", "computer", "light", "tool", "book", "key", "lock", "camera", "envelope")):
                                                            cats.append("Objects")
                                                        # Symbols
                                                        if any(k in name_l for k in ("heart", "star", "symbol", "arrow", "warning", "sign", "check", "cross")):
                                                            cats.append("Symbols")
                                                        # Flags - detect regional indicator symbols or the word 'flag'
                                                        try:
                                                            import unicodedata as _ud
                                                            if "flag" in name_l:
                                                                cats.append("Flags")
                                                            else:
                                                                # Regional indicator letters are used for flags (skip detailed check here)
                                                                pass
                                                        except Exception:
                                                            pass
                                                        # Kaomoji / Emoticons - not typical for unicode emoji, leave empty
                                                        return cats

                                                    # Helper to get a readable name for an emoji
                                                    def emoji_name(ch: str) -> str:
                                                        name = ""
                                                        if has_emoji_lib and _emoji_lib is not None:
                                                            try:
                                                                name = _emoji_lib.demojize(ch, language='en')
                                                            except Exception:
                                                                try:
                                                                    name = _emoji_lib.demojize(ch)
                                                                except Exception:
                                                                    name = ""
                                                            # Normalize demojized name: remove surrounding colons and replace underscores
                                                            if name:
                                                                try:
                                                                    name = name.strip(':')
                                                                except Exception:
                                                                    pass
                                                                try:
                                                                    name = name.replace('_', ' ')
                                                                except Exception:
                                                                    pass
                                                        else:
                                                            try:
                                                                name = _unicodedata.name(ch)
                                                                name = name.lower()
                                                                name = name.replace('_', ' ')
                                                            except Exception:
                                                                name = ""
                                                        return name

                                                    # Build category -> set(mapping) for quick lookup
                                                    category_map = {c: set() for c, _ in cat_buttons} if cat_buttons else {}
                                                    for ch in all_emojis:
                                                        try:
                                                            nm = emoji_name(ch)
                                                        except Exception:
                                                            nm = ""
                                                        cats = categorize_emoji(ch, nm)
                                                        for c in cats:
                                                            if c in category_map:
                                                                category_map[c].add(ch)

                                                    # Helper to populate list based on filter text and selected categories
                                                    def populate(filter_text: str):
                                                        list_w.clear()
                                                        ft = (filter_text or "").strip().lower()
                                                        added = 0
                                                        # Determine active categories
                                                        active_cats = [name for name, btn in cat_buttons if btn.isChecked()] if cat_buttons else []
                                                        for ch in all_emojis:
                                                            try:
                                                                name = emoji_name(ch)
                                                            except Exception:
                                                                name = ""
                                                            # If categories are active, skip emojis not in any active category
                                                            if active_cats:
                                                                # If emoji belongs to any active category, allow it; otherwise skip
                                                                allowed = False
                                                                for ac in active_cats:
                                                                    if ch in category_map.get(ac, set()):
                                                                        allowed = True
                                                                        break
                                                                if not allowed:
                                                                    continue
                                                            if not ft or ft in (name or "").lower():
                                                                display_name = name or ""
                                                                item = QListWidgetItem(f"{ch}  {display_name}")
                                                                list_w.addItem(item)
                                                                added += 1
                                                                # Cap results to 300 for performance
                                                                if added >= 300:
                                                                    break

                                                    # Initial population
                                                    populate("")

                                                    # Update on search change (debounce not necessary for small lists)
                                                    def on_search(text):
                                                        try:
                                                            populate(text)
                                                        except Exception:
                                                            pass
                                                    search.textChanged.connect(on_search)

                                                    # Wire category buttons to update the list when toggled
                                                    try:
                                                        for _, btn in cat_buttons:
                                                            try:
                                                                btn.clicked.connect(lambda _checked=False: populate(search.text()))
                                                            except Exception:
                                                                pass
                                                    except Exception:
                                                        pass

                                                    # When an emoji is selected, set it into emoji_display and close picker
                                                    def on_item_clicked(item):
                                                        try:
                                                            txt = item.text()
                                                            sel = txt.split()[0] if txt else ""
                                                            try:
                                                                emoji_display.setText(sel)
                                                            except Exception:
                                                                pass
                                                            try:
                                                                # Hide and schedule deletion instead of close() to avoid
                                                                # triggering unwanted window close propagation in some environments.
                                                                try:
                                                                    picker.hide()
                                                                except Exception:
                                                                    pass
                                                                try:
                                                                    picker.deleteLater()
                                                                except Exception:
                                                                    pass
                                                            except Exception:
                                                                pass
                                                        except Exception:
                                                            pass
                                                    list_w.itemClicked.connect(on_item_clicked)

                                                    try:
                                                        # Register picker as a transient window on the top-level UI so
                                                        # clicks inside the picker are considered "inside" the UI area.
                                                        try:
                                                            top = win
                                                            # Walk up parent chain to find the UIRenderer/top-level object that owns SettingsWindow
                                                            while top is not None:
                                                                # Heuristic: UIRenderer has attribute 'window_bounds'
                                                                if hasattr(top, 'window_bounds'):
                                                                    try:
                                                                        if not hasattr(top, '_transient_windows'):
                                                                            top._transient_windows = []
                                                                        if picker not in top._transient_windows:
                                                                            top._transient_windows.append(picker)
                                                                        # Clean up registry when picker is destroyed
                                                                        try:
                                                                            picker.destroyed.connect(lambda _=None, owner=top, w=picker: owner._transient_windows.remove(w) if (hasattr(owner, '_transient_windows') and w in owner._transient_windows) else None)
                                                                        except Exception:
                                                                            pass
                                                                    except Exception:
                                                                        pass
                                                                    break
                                                                try:
                                                                    top = top.parent()
                                                                except Exception:
                                                                    break
                                                        except Exception:
                                                            pass
                                                        picker.show()
                                                        picker.raise_()
                                                        picker.activateWindow()
                                                    except Exception:
                                                        pass
                                                except Exception as e:
                                                    debug_write(f"Error opening emoji picker: {e}")

                                            # Connect the button directly to the picker function (no lambda) so exceptions are easier to trace
                                            try:
                                                emoji_btn.clicked.connect(_open_emoji_picker)
                                            except Exception:
                                                # Fallback: no-op if connection fails
                                                try:
                                                    emoji_btn.clicked.connect(lambda _checked=False: None)
                                                except Exception:
                                                    pass
                                        except Exception:
                                            # Fallback: no-op if emoji picker can't be created or connected
                                            try:
                                                emoji_btn.clicked.connect(lambda _checked=False: None)
                                            except Exception:
                                                pass
                                    except Exception:
                                        pass
                                except Exception:
                                    pass

                                # Two-way toggle: Parent (checked) / Child (unchecked)
                                try:
                                    toggle = QCheckBox("Parent (checked) / Child (unchecked)")
                                    toggle.setChecked(True)
                                    layout.addWidget(toggle)
                                except Exception:
                                    pass

                                # Spacer to push the Save button to the bottom
                                try:
                                    layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
                                except Exception:
                                    pass

                                # Save button (no-op for now)
                                try:
                                    save_btn = QPushButton("Save")
                                    save_btn.clicked.connect(lambda _checked=False: None)
                                    layout.addWidget(save_btn)
                                except Exception:
                                    pass

                                win.setLayout(layout)
                            except Exception:
                                # Fallback to empty layout if anything goes wrong
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
        # Transient popup windows (emoji pickers, helpers) that should be treated as part of the UI
        self._transient_windows = []

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
            # Check main UI bounds first
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

            # Check any registered transient windows (emoji picker, helpers, etc.)
            try:
                tw = getattr(self, '_transient_windows', None)
                if tw:
                    for w in list(tw):
                        try:
                            if w is None:
                                continue
                            if not getattr(w, 'isVisible', lambda: False)():
                                continue
                            try:
                                g = w.frameGeometry()
                            except Exception:
                                g = w.geometry()
                            if g is None:
                                continue
                            gx, gy, gw, gh = g.x(), g.y(), g.width(), g.height()
                            if gx <= x <= gx + gw and gy <= y <= gy + gh:
                                return True
                        except Exception:
                            continue
            except Exception:
                pass

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
