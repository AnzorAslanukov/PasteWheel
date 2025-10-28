import json
import os


class PasteWheelConfig:
    """Configuration manager for PasteWheel application."""

    CONFIG_FILE = "pastewheel_config.json"
    DEFAULT_CONFIG = {
        "theme": "light",
        "buttons": [],
        "input_mode": "keyboard"
    }
    
    def __init__(self):
        """Initialize PasteWheelConfig and load existing configuration."""
        self.config = self.read()
    
    def read(self):
        """
        Read configuration from pastewheel_config.json file.
        If file doesn't exist, create it with default configuration.
        
        Returns:
            Dictionary containing configuration
        """
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as file:
                    config = json.load(file)
                    return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading config file: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.write(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def write(self, config=None):
        """
        Write configuration to pastewheel_config.json file.
        
        Args:
            config: Dictionary to write. If None, uses current self.config
        """
        if config is None:
            config = self.config
        
        try:
            with open(self.CONFIG_FILE, 'w') as file:
                json.dump(config, file, indent=4)
            self.config = config
        except IOError as e:
            print(f"Error writing config file: {e}")
    
    def get_theme(self):
        """
        Get current theme setting from configuration.
        
        Returns:
            String "light" or "dark"
        """
        return self.config.get("theme", "light")
    
    def set_theme(self, theme):
        """
        Set theme setting in configuration and write to file.

        Args:
            theme: String "light" or "dark"

        Raises:
            ValueError: If theme is not "light" or "dark"
        """
        if theme not in ["light", "dark"]:
            raise ValueError("Theme must be either 'light' or 'dark'")

        self.config["theme"] = theme
        self.write()

    def get_input_mode(self):
        """
        Get current input mode setting from configuration.

        Returns:
            String "keyboard" or "mouse"
        """
        return self.config.get("input_mode", "keyboard")

    def set_input_mode(self, input_mode):
        """
        Set input mode setting in configuration and write to file.

        Args:
            input_mode: String "keyboard" or "mouse"

        Raises:
            ValueError: If input_mode is not "keyboard" or "mouse"
        """
        if input_mode not in ["keyboard", "mouse"]:
            raise ValueError("Input mode must be either 'keyboard' or 'mouse'")

        self.config["input_mode"] = input_mode
        self.write()

    def get(self, key, default=None):
        """
        Get a configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """
        Set a configuration value by key and write to file.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        self.write()
    
    def get_button(self, button_id):
        """
        Get button data by button ID from configuration.
        
        Args:
            button_id: The ID of the button to retrieve
        
        Returns:
            Dictionary containing button data, or None if not found
        """
        buttons = self.config.get("buttons", [])
        for button in buttons:
            if button.get("id") == button_id:
                return button
        return None
    
    def get_all_buttons(self):
        """
        Get all buttons from configuration.
        
        Returns:
            List of button dictionaries
        """
        return self.config.get("buttons", [])
    
    def add_button(self, button_data):
        """
        Add a button to configuration and write to file.
        
        Args:
            button_data: Dictionary containing button data with at least 'id' key
        """
        if "id" not in button_data:
            raise ValueError("Button data must contain 'id' key")
        
        buttons = self.config.get("buttons", [])
        
        # Check if button with same ID already exists
        for i, button in enumerate(buttons):
            if button.get("id") == button_data.get("id"):
                # Update existing button
                buttons[i] = button_data
                self.config["buttons"] = buttons
                self.write()
                return
        
        # Add new button
        buttons.append(button_data)
        self.config["buttons"] = buttons
        self.write()
    
    def remove_button(self, button_id):
        """
        Remove a button from configuration by ID and write to file.
        
        Args:
            button_id: The ID of the button to remove
        
        Returns:
            True if button was removed, False if not found
        """
        buttons = self.config.get("buttons", [])
        initial_count = len(buttons)
        buttons = [b for b in buttons if b.get("id") != button_id]
        
        if len(buttons) < initial_count:
            self.config["buttons"] = buttons
            self.write()
            return True
        return False
    
    def get_buttons_by_layer(self, layer):
        """
        Get all buttons for a specific layer from configuration.
        
        Args:
            layer: Layer number (1, 2, or 3) to retrieve buttons for
        
        Returns:
            List of button dictionaries found in the layer, or None if no buttons found
        """
        all_buttons = self.config.get("buttons", [])
        
        # Filter buttons by layer
        layer_buttons = [b for b in all_buttons if b.get("layer") == layer]
        
        # Return list if buttons found, otherwise None
        if layer_buttons:
            return layer_buttons
        return None
    
    def has_any_buttons(self):
        """
        Check if any button data exists in configuration.
        
        Returns:
            True if any buttons with 'id' key exist, False otherwise
        """
        all_buttons = self.config.get("buttons", [])
        
        # Check if any button has an 'id' key with a value
        for button in all_buttons:
            if button.get("id") is not None:
                return True
        
        return False
