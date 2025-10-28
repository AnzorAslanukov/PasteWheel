from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from radial_interface_settings.tabs.general_tab import GeneralTab
from radial_interface_settings.tabs.button_tab import ButtonTab
from theme import Theme
from pastewheel_config import PasteWheelConfig
from radial_interface_button_settings.radial_interface_button_settings import RadialInterfaceButtonSettings


class RadialInterfaceSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.width = 400
        self.height = 400
        self.button_settings_windows = []  # List to keep references to windows
        
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
        
        # Get config to determine layer visibility
        config = PasteWheelConfig()
        
        # Determine which layers have buttons
        layer_1_enabled = config.get_buttons_by_layer(1) is not None
        layer_2_enabled = config.get_buttons_by_layer(2) is not None
        layer_3_enabled = config.get_buttons_by_layer(3) is not None
        
        # Create and add tabs
        general_tab = GeneralTab()
        tab_widget.addTab(general_tab, "General")
        
        # Layer 1 is always visible (even if empty)
        self.layer_1_buttons = ButtonTab(layer=1, enabled=True, settings_window=self)
        tab_widget.addTab(self.layer_1_buttons, "Layer 1")
        
        # Store references to layer tabs for potential future use
        self.layer_2_buttons = None
        self.layer_3_buttons = None
        
        # Only add layer 2 if it has buttons
        if layer_2_enabled:
            self.layer_2_buttons = ButtonTab(layer=2, enabled=True, settings_window=self)
            tab_widget.addTab(self.layer_2_buttons, "Layer 2")
        
        # Only add layer 3 if it has buttons
        if layer_3_enabled:
            self.layer_3_buttons = ButtonTab(layer=3, enabled=True, settings_window=self)
            tab_widget.addTab(self.layer_3_buttons, "Layer 3")
        
        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(tab_widget)
        self.setLayout(layout)
    
    def open_button_settings(self, button_id=None):
        """
        Open the RadialInterfaceButtonSettings window.
        
        Args:
            button_id: ID of the button to configure (optional)
        """
        # Create a new instance and keep reference to prevent garbage collection
        print("DEBUG: RadialInterfaceSettings.open_button_settings() called")
        print(f"DEBUG: button_id = {button_id}")
        button_settings = RadialInterfaceButtonSettings(button_id=button_id, parent=self)
        print(f"DEBUG: RadialInterfaceButtonSettings created: {button_settings}")
        self.button_settings_windows.append(button_settings)
        print(f"DEBUG: Window added to list, total windows: {len(self.button_settings_windows)}")
        button_settings.show()
        print(f"DEBUG: Window shown, geometry: {button_settings.geometry()}")
