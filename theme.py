from pastewheel_config import PasteWheelConfig


class Theme:
    # Initialize config manager
    _config = PasteWheelConfig()
    MODE = _config.get_theme()  # Class variable for theme mode - loaded from config
    
    def __init__(self):
        """Initialize Theme with the global mode setting."""
        pass

    def get_colors(self):
        """Return a dictionary of widget names and their corresponding hex color strings."""
        if Theme.MODE == "light":
            return {
                "background": "#FFFFFF",
                "foreground": "#000000",
                "button": "#F0F0F0",
                "button_hover": "#E0E0E0",
                "text": "#000000",
                "text_secondary": "#666666",
                "border": "#CCCCCC",
                "accent": "#007BFF",
                "success": "#28A745",
                "warning": "#FFC107",
                "error": "#DC3545",
                "section_background": "#F8F9FA",
                "circle_i": "#007AFF",
                "checked_button": "#4CAF50",
                # Table model specific colors
                "table_background": "#FFFFFF",
                "table_border": "#E0E0E0",
                "table_gridline": "#F0F0F0",
                "table_text": "#000000",
                "table_selection_background": "#007BFF",
                "table_selection_text": "#FFFFFF",
                "table_hover_background": "#E8F4F8",
                "table_alternate_background": "#FAFBFC"
            }
        else:  # dark mode
            return {
                "background": "#1E1E1E",
                "foreground": "#FFFFFF",
                "button": "#2D2D2D",
                "button_hover": "#3D3D3D",
                "text": "#FFFFFF",
                "text_secondary": "#B0B0B0",
                "border": "#404040",
                "accent": "#0D47A1",
                "success": "#4CAF50",
                "warning": "#FF9800",
                "error": "#F44336",
                "section_background": "#2A2A2A",
                "circle_i": "#87A8DC",
                "checked_button": "#15a866",
                # Table model specific colors
                "table_background": "#252525",
                "table_border": "#404040",
                "table_gridline": "#333333",
                "table_text": "#FFFFFF",
                "table_selection_background": "#0D47A1",
                "table_selection_text": "#FFFFFF",
                "table_hover_background": "#1E3A5F",
                "table_alternate_background": "#2A2A2A"
            }

    @classmethod
    def set_mode(cls, mode):
        """Set the theme mode to either 'light' or 'dark' globally and save to config."""
        if mode not in ["light", "dark"]:
            raise ValueError("Mode must be either 'light' or 'dark'")
        cls.MODE = mode
        # Save theme mode to configuration file
        cls._config.set_theme(mode)

    @classmethod
    def get_mode(cls):
        """Return the current theme mode."""
        return cls.MODE
