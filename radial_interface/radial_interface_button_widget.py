from PyQt5.QtWidgets import QPushButton, QToolTip
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from theme import Theme


class RadialInterfaceButtonWidget(QPushButton):
    """
    Visual Qt widget representing a single radial interface button.
    Displays the button label (e.g. an emoji) as button text and supports
    hover/click animations. Positioned on the radial ring by RadialInterface.
    """

    BUTTON_SIZE = 36

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

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        # Opacity effect — stored as instance variable to avoid use-after-free
        self._opacity_effect = None

        # Click shrink animation timer
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

        # Styling
        bg_color = self.colors.get("button", "#F0F0F0")
        hover_color = self.colors.get("button_hover", "#E0E0E0")
        border_color = self.colors.get("border", "#CCCCCC")
        radius = size // 2

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {radius}px;
                font-size: {self._base_font_size}px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

        # Opacity effect
        if self._opacity_effect is None:
            self._opacity_effect = QGraphicsOpacityEffect()
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        # Connect click
        self.clicked.connect(self._on_clicked)

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
        """Briefly shrink the font on click for tactile feedback."""
        shrunk_size = int(self._base_font_size * 0.75)
        font = self.font()
        font.setPixelSize(shrunk_size)
        self.setFont(font)
        self._click_timer.start(100)

    def _restore_font_size(self):
        font = self.font()
        font.setPixelSize(self._base_font_size)
        self.setFont(font)