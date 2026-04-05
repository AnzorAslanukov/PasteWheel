import pyperclip

from PyQt5.QtWidgets import QPushButton, QToolTip, QApplication
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint, pyqtSignal
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from theme import Theme


class RadialInterfaceButtonWidget(QPushButton):
    """
    Visual Qt widget representing a single radial interface button.

    **Clipboard buttons** (``button_type == "clip"``)
        - Rendered with a light-blue background (``#29B6F6``).
        - On click: writes the button's clipboard payload to the Windows OS
          clipboard via ``QApplication.clipboard().setText()``, then plays a
          brief font-shrink animation (100 ms) for tactile feedback.
        - Single-string buttons always write the same string.
        - Two-string buttons operate in *sequential paste mode*: clicking the
          button writes string 1 to the clipboard and registers a system-wide
          Ctrl+V hook.  Each subsequent Ctrl+V press cycles through the strings
          (string 1 → string 2 → string 1 → …) so the user can paste multiple
          times from a single button click.  ``_seq_index`` tracks which string
          will be written on the next Ctrl+V.  The hook is removed whenever any
          button is clicked.
        - External clipboard operations (e.g. the user copying text from a
          document) freely overwrite PasteWheel's content — the clipboard is
          never locked or monitored.

    **Expand buttons** (``button_type == "exp"``)
        - Rendered with a light-orange background (``#FFA726``).
        - Behave as toggles: clicking once turns them ON (revealing their child
          buttons on the next layer) and clicking again turns them OFF (hiding
          those children).
        - A 2 px accent-coloured border is applied when the button is ON.
        - The ``expand_toggled`` signal is emitted whenever the toggle state
          changes so that :class:`RadialInterface` can react (Rule 4 / Rule 5).
    """

    # ------------------------------------------------------------------
    # Class-level sequential-paste hook tracking.
    # Only one two-string button can be in sequential mode at a time.
    # ------------------------------------------------------------------
    _active_hook = None          # keyboard hotkey handle returned by kb.add_hotkey()
    _active_seq_widget = None    # the RadialInterfaceButtonWidget that owns the hook

    BUTTON_SIZE = 36

    # Emitted when an expand-type button is toggled on or off.
    # Signature: (button_id: str, is_on: bool)
    expand_toggled = pyqtSignal(str, bool)

    def __init__(self, button_data: dict, parent=None):
        """
        Args:
            button_data: Dict with keys: id, layer, label, clipboard,
                         button_type, tooltip (optional).
            parent:      Parent QWidget (the RadialInterface window).
        """
        super().__init__(parent)

        self.button_id = button_data.get("id", "")
        self.button_layer = button_data.get("layer", 1)
        self.button_label = button_data.get("label", "")
        self.button_clipboard = button_data.get("clipboard", [])
        self.button_type = button_data.get("button_type", "clip")
        self.tooltip_text = button_data.get("tooltip", "")

        # Toggle state — only meaningful for expand-type buttons.
        # True  → button is ON  (children are visible)
        # False → button is OFF (children are hidden)
        self.is_toggled = False

        # Sequential clipboard index — only meaningful for clipboard buttons
        # with two strings.  Tracks which string will be written on the next
        # Ctrl+V press (0 = string 1, 1 = string 2).  Reset to 0 on each click.
        self._seq_index = 0

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        # Opacity effect — stored as instance variable to avoid use-after-free
        self._opacity_effect = None

        # Click shrink animation timer (clipboard buttons only)
        self._click_timer = QTimer()
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._restore_font_size)

        self._base_font_size = 16  # px, for emoji rendering

        self._init_ui()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _init_ui(self):
        """Configure appearance and behaviour."""
        size = self.BUTTON_SIZE
        self.setFixedSize(size, size)

        # Display the label (emoji or text) as button text
        self.setText(self.button_label)

        # Font sized to fill the button
        font = QFont()
        font.setPixelSize(self._base_font_size)
        self.setFont(font)

        # Tooltip
        if self.tooltip_text:
            self.setToolTip(self.tooltip_text)

        # Apply initial stylesheet
        self._apply_style()

        # Opacity effect
        if self._opacity_effect is None:
            self._opacity_effect = QGraphicsOpacityEffect()
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        # Connect click
        self.clicked.connect(self._on_clicked)

    def _apply_style(self):
        """
        Apply the button stylesheet based on button type and current toggle state.

        Clipboard buttons are rendered in light blue (#29B6F6) and expand buttons
        in light orange (#FFA726) so the two types are immediately distinguishable
        at a glance.  Expand buttons additionally receive a 2px accent border when
        toggled ON.
        """
        size = self.BUTTON_SIZE
        border_color = self.colors.get("border", "#CCCCCC")
        radius = size // 2

        # Type-specific background / hover colors (Material Design palette)
        if self.button_type == "clip":
            bg_color = "#29B6F6"      # Material Light Blue 400
            hover_color = "#0288D1"   # Material Light Blue 700
        else:  # "exp"
            bg_color = "#FFA726"      # Material Orange 400
            hover_color = "#FB8C00"   # Material Orange 600

        # Expand buttons get a distinct accent border when toggled on
        if self.button_type == "exp" and self.is_toggled:
            accent_color = self.colors.get("accent", "#007BFF")
            border_decl = f"2px solid {accent_color}"
        else:
            border_decl = f"1px solid {border_color}"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: {border_decl};
                border-radius: {radius}px;
                font-size: {self._base_font_size}px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_toggled(self, state: bool):
        """
        Programmatically set the toggle state **without** emitting
        ``expand_toggled``.  Used by :class:`RadialInterface` to turn off
        expand buttons from outside (e.g. when another expand button in the
        same layer is turned on).
        """
        self.is_toggled = state
        self._apply_style()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def enterEvent(self, event):
        self._opacity_effect.setOpacity(0.75)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        if self.tooltip_text:
            global_pos = self.mapToGlobal(event.pos())
            tooltip_pos = QPoint(global_pos.x() + 15, global_pos.y() - 20)
            QToolTip.showText(tooltip_pos, self.tooltip_text, self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._opacity_effect.setOpacity(1.0)
        self.setCursor(QCursor(Qt.ArrowCursor))
        QToolTip.hideText()
        super().leaveEvent(event)

    def _on_clicked(self):
        """
        Handle button click.

        * Expand buttons: toggle ON/OFF state and emit ``expand_toggled``.
        * Clipboard buttons: write clipboard data to the OS clipboard, then
          play a brief font-shrink animation for tactile feedback.
        """
        if self.button_type == "exp":
            self.is_toggled = not self.is_toggled
            self._apply_style()
            self.expand_toggled.emit(self.button_id, self.is_toggled)
        else:
            # Write to the OS clipboard before the animation
            self._write_to_clipboard()
            # Shrink font briefly for tactile feedback
            shrunk_size = int(self._base_font_size * 0.75)
            font = self.font()
            font.setPixelSize(shrunk_size)
            self.setFont(font)
            self._click_timer.start(100)

    def _write_to_clipboard(self):
        """
        Write the button's clipboard payload to the Windows clipboard and,
        for two-string buttons, register a system-wide Ctrl+V hook that cycles
        through the strings on each paste.

        * 0 items  → no-op.
        * 1 item   → always writes that single string (no hook needed).
        * 2 items  → sequential paste mode:
                       1. Remove any previously registered sequential hook.
                       2. Reset ``_seq_index`` to 0.
                       3. Write string 1 to the clipboard immediately so the
                          very first Ctrl+V pastes string 1.
                       4. Register a suppressing Ctrl+V hotkey via the
                          ``keyboard`` library (imported lazily to avoid
                          blocking on module load in headless environments).
                          Each time the hotkey fires it calls
                          ``_advance_seq_clipboard()`` (which writes the
                          current string via pyperclip and advances the index)
                          then simulates the actual paste via
                          ``kb.press_and_release('ctrl+v')``.
                     The hook is removed whenever any button is clicked (by the
                     next call to ``_write_to_clipboard``).
        """
        # Always cancel any active sequential hook before doing anything else.
        RadialInterfaceButtonWidget._remove_active_hook()

        if not self.button_clipboard:
            return

        if len(self.button_clipboard) == 1:
            QApplication.clipboard().setText(self.button_clipboard[0])
        else:
            # Sequential paste mode ----------------------------------------
            # Reset sequence and write string 1 immediately.
            self._seq_index = 0
            QApplication.clipboard().setText(self.button_clipboard[0])

            # Register the Ctrl+V hook.  The keyboard library is imported
            # lazily here so that merely importing this module does not
            # install a global hook (which would block in headless / test
            # environments).  The handler runs in a background thread, so
            # clipboard writes use pyperclip (thread-safe) rather than
            # QApplication.clipboard().
            try:
                import keyboard as kb  # noqa: PLC0415
                RadialInterfaceButtonWidget._active_seq_widget = self

                def _seq_handler():
                    widget = RadialInterfaceButtonWidget._active_seq_widget
                    if widget is None:
                        return
                    widget._advance_seq_clipboard()
                    kb.press_and_release("ctrl+v")

                RadialInterfaceButtonWidget._active_hook = kb.add_hotkey(
                    "ctrl+v", _seq_handler, suppress=True
                )
            except Exception:
                # If keyboard hooks are unavailable (e.g. headless environment,
                # insufficient privileges), sequential paste degrades gracefully:
                # the clipboard already holds string 1 from the write above, and
                # _advance_seq_clipboard() still works correctly when called
                # directly (e.g. in unit tests).
                pass

    def _advance_seq_clipboard(self):
        """
        Write ``button_clipboard[_seq_index]`` to the clipboard and advance
        the index (0 → 1 → 0 → …).

        Uses ``pyperclip.copy()`` so it is safe to call from any thread
        (including the ``keyboard`` library's background hook thread).

        This method is also called directly in unit tests to simulate
        sequential Ctrl+V presses without needing real key events.
        """
        if len(self.button_clipboard) < 2:
            return
        pyperclip.copy(self.button_clipboard[self._seq_index])
        self._seq_index = 1 - self._seq_index

    @classmethod
    def _remove_active_hook(cls):
        """
        Remove the currently registered sequential Ctrl+V hook, if any.
        Safe to call even when no hook is active.
        """
        if cls._active_hook is not None:
            try:
                import keyboard as kb  # noqa: PLC0415
                kb.remove_hotkey(cls._active_hook)
            except Exception:
                pass
            cls._active_hook = None
            cls._active_seq_widget = None

    def _restore_font_size(self):
        font = self.font()
        font.setPixelSize(self._base_font_size)
        self.setFont(font)