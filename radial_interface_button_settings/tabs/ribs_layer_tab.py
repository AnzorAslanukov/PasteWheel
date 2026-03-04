from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from theme import Theme


class RibsLayerTab(QWidget):
    def __init__(self, parent=None, layer=None):
        """
        Initialize the RibsLayerTab.

        Represents a single layer tab page inside the RadialInterfaceButtonSettings
        QTabWidget. Each instance corresponds to one layer (1, 2, or 3) and serves
        as the tab page container for that layer selection.

        Args:
            parent: Parent widget
            layer: Layer number (1, 2, or 3) this tab represents
        """
        super().__init__(parent)
        self.layer = layer

        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()

        self.initUI()

    def initUI(self):
        """Initialize the RibsLayerTab UI."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)