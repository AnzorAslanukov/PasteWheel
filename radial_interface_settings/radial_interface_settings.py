from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from radial_interface_settings.tabs.general_tab import GeneralTab
from radial_interface_settings.tabs.button_tab import ButtonTab


class RadialInterfaceSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.width = 400
        self.height = 400
        self.initUI()

    def initUI(self):
        """Initialize the RadialInterfaceSettings UI."""
        self.setWindowTitle('PasteWheel Settings')
        self.setGeometry(100, 100, self.width, self.height)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Create and add tabs
        general_tab = GeneralTab()
        button_tab = ButtonTab()
        
        tab_widget.addTab(general_tab, "General")
        tab_widget.addTab(button_tab, "Buttons")
        
        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(tab_widget)
        self.setLayout(layout)
