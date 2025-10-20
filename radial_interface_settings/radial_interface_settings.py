from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from radial_interface_settings.tabs.general_tab import GeneralTab
from radial_interface_settings.tabs.button_tab import ButtonTab
from theme import Theme


class RadialInterfaceSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.width = 400
        self.height = 400
        
        # Get theme colors
        theme = Theme()
        self.colors = theme.get_colors()
        
        self.initUI()

    def initUI(self):
        """Initialize the RadialInterfaceSettings UI."""
        self.setWindowTitle('PasteWheel Settings')
        self.setGeometry(100, 100, self.width, self.height)
        
        # Apply theme colors to the window background and text
        background_color = self.colors.get("background", "#FFFFFF")
        foreground_color = self.colors.get("foreground", "#000000")
        button_color = self.colors.get("button", "#F0F0F0")
        button_hover_color = self.colors.get("button_hover", "#E0E0E0")
        text_color = self.colors.get("text", "#000000")
        
        # Apply stylesheet with theme colors
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {background_color};
                color: {text_color};
            }}
            QTabWidget {{
                background-color: {background_color};
                color: {text_color};
            }}
            QTabBar::tab {{
                background-color: {button_color};
                color: {text_color};
                padding: 5px 15px;
                border: 1px solid {foreground_color};
            }}
            QTabBar::tab:selected {{
                background-color: {foreground_color};
                color: {background_color};
            }}
            QTabBar::tab:hover {{
                background-color: {button_hover_color};
            }}
        """)
        
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
