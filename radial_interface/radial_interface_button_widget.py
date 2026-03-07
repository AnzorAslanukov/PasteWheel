from PyQt5.QtWidgets import QPushButton, QToolTip
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint, pyqtSignal
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from theme import Theme


class RadialInterfaceButtonWidget(QPushButton):
    """
    Visual Qt widget representing a single radial interface button.

    Clipboard buttons display their label and provide a brief shrink animation
    on click for tactile feedback.

    Expand buttons behave as toggles: clicking once turns them ON (revealing
    their child buttons on the next layer) and clicking again turns them OFF
    (hiding those children).  The ``expand_toggled`` signal is emitted whenever
    the toggle state changes so that :class:`RadialInterface` can react.
    """

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

        Expand buttons receive a highlighted border when toggled ON so the user
        can tell at a glance which expand button is active.
        """
        size = self.BUTTON_SIZE
        bg_color = self.colors.get("button", "#F0F0F0")
        hover_color = self.colors.get("button_hover", "#E0E0E0")
        border_color = self.colors.get("border", "#CCCCCC")
        radius = size // 2

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
        * Clipboard buttons: brief font-shrink animation for tactile feedback.
        """
        if self.button_type == "exp":
            self.is_toggled = not self.is_toggled
            self._apply_style()
            self.expand_toggled.emit(self.button_id, self.is_toggled)
        else:
            # Clipboard button — shrink font briefly for tactile feedback
            shrunk_size = int(self._base_font_size * 0.75)
            font = self.font()
            font.setPixelSize(shrunk_size)
            self.setFont(font)
            self._click_timer.start(100)

    def _restore_font_size(self):
        font = self.font()
        font.setPixelSize(self._base_font_size)
        self.setFont(font)