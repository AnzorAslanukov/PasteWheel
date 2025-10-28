from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from theme import Theme
from pastewheel_config import PasteWheelConfig
from radial_interface_settings.radial_interface_settings_button import RadialInterfaceSettingsButton


class ButtonTab(QWidget):
    def __init__(self, parent=None, layer=None, enabled=True, settings_window=None):
        """
        Initialize the Button tab.
        
        Args:
            parent: Parent widget
            layer: Layer number (1, 2, or 3) to identify the tab
            enabled: Boolean indicating whether tab should be visible and clickable (default: True)
            settings_window: Reference to parent RadialInterfaceSettings window
        """
        super().__init__(parent)
        self.layer = layer
        self.settings_window = settings_window
        
        # Get theme colors
        theme = Theme()
        colors = theme.get_colors()
        
        # Set color properties from theme
        self.color_background = colors.get("background", "#FFFFFF")
        self.color_foreground = colors.get("foreground", "#000000")
        self.color_button = colors.get("button", "#F0F0F0")
        self.color_button_hover = colors.get("button_hover", "#E0E0E0")
        self.color_text = colors.get("text", "#000000")
        self.color_text_secondary = colors.get("text_secondary", "#666666")
        self.color_border = colors.get("border", "#CCCCCC")
        self.color_accent = colors.get("accent", "#007BFF")
        
        self.is_enabled = enabled
        self.initUI()
        self.set_enabled(enabled)

    def initUI(self):
        """Initialize the Button tab UI."""
        # Create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        
        # Check for button presence and display placeholder if needed
        self._show_placeholder_if_empty()
    
    def _show_placeholder_if_empty(self):
        """
        Check if buttons exist in configuration.
        If not, display a placeholder button to add the first button.
        """
        config = PasteWheelConfig()
        
        if not config.has_any_buttons():
            # Create the "Add first button" button with newline for two-line label
            add_button = RadialInterfaceSettingsButton("Add first\nclipboard button", parent=self)
            
            # Connect button click to handler method
            add_button.clicked.connect(self.on_add_button_clicked)
            
            # Get the layout
            layout = self.layout()
            if layout is not None:
                layout.addWidget(add_button)
    
    def on_add_button_clicked(self):
        """
        Handle the add button click event.
        Opens the RadialInterfaceButtonSettings window.
        """
        print("DEBUG: on_add_button_clicked called")
        print(f"DEBUG: self.settings_window = {self.settings_window}")
        if self.settings_window:
            print("DEBUG: Calling open_button_settings()")
            self.settings_window.open_button_settings()
        else:
            print("DEBUG: settings_window is None!")
    
    def set_enabled(self, enabled):
        """
        Set whether the tab is enabled (visible and clickable).
        
        Args:
            enabled: Boolean indicating tab visibility and interaction state
        """
        self.is_enabled = enabled
        self.setEnabled(enabled)
        
        if enabled:
            self.show()
        else:
            self.hide()
    
    def is_tab_enabled(self):
        """
        Get whether the tab is currently enabled.
        
        Returns:
            Boolean indicating if tab is enabled
        """
        return self.is_enabled
