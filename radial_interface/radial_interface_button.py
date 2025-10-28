from pastewheel_config import PasteWheelConfig
from theme import Theme


class RadialInterfaceButton:
    def __init__(self, button_id):
        """
        Initialize RadialInterfaceButton by loading data from configuration.
        
        Args:
            button_id: The ID of the button to load from configuration
        """
        # Initialize config manager
        config = PasteWheelConfig()
        
        # Get button data from configuration
        button_data = config.get_button(button_id)
        
        if button_data is None:
            raise ValueError(f"Button with ID '{button_id}' not found in configuration")
        
        # Load button parameters from configuration
        self.id = button_data.get("id")
        self.layer = button_data.get("layer")
        self.label = button_data.get("label")
        self.clipboard = button_data.get("clipboard")
        self.button_type = button_data.get("button_type")
        
        # Load theme colors
        theme = Theme()
        colors = theme.get_colors()
        
        # Set color properties from theme
        self.color_button = colors.get("button", "#F0F0F0")
        self.color_button_hover = colors.get("button_hover", "#E0E0E0")
        self.color_text = colors.get("text", "#000000")
        self.color_text_secondary = colors.get("text_secondary", "#666666")
        self.color_border = colors.get("border", "#CCCCCC")
        self.color_accent = colors.get("accent", "#007BFF")
        self.color_background = colors.get("background", "#FFFFFF")
    
    @staticmethod
    def create_button(id, layer, label, clipboard, button_type):
        """
        Create a new button and save it to configuration.
        
        Args:
            id: Unique button identifier
            layer: Layer number (1, 2, or 3)
            label: Button label text
            clipboard: Clipboard content
            button_type: Type of button
        
        Returns:
            RadialInterfaceButton instance
        """
        config = PasteWheelConfig()
        
        button_data = {
            "id": id,
            "layer": layer,
            "label": label,
            "clipboard": clipboard,
            "button_type": button_type
        }
        
        config.add_button(button_data)
        
        # Return new instance by loading from config
        return RadialInterfaceButton(id)
    
    def update(self):
        """Update this button's data in configuration."""
        config = PasteWheelConfig()
        
        button_data = {
            "id": self.id,
            "layer": self.layer,
            "label": self.label,
            "clipboard": self.clipboard,
            "button_type": self.button_type
        }
        
        config.add_button(button_data)
    
    def delete(self):
        """Delete this button from configuration."""
        config = PasteWheelConfig()
        config.remove_button(self.id)
