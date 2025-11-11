from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea
from PyQt5.QtCore import Qt
from theme import Theme
from radial_interface_button_settings.emoji_symbol_picker.esp_label import EspLabel
from radial_interface_button_settings.emoji_symbol_picker.esp_btn import EspBtn


class EmojiSymbolPicker(QWidget):
    """
    A widget for picking emojis and symbols with theme support.
    """

    def __init__(self, parent=None):
        """
        Initialize the EmojiSymbolPicker widget.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent, Qt.Window)
        self.setWindowTitle("Emoji / Symbol Picker")

        # Set default window size
        self.setFixedSize(400, 600)

        # Position the window offset from parent to make it visible
        if parent:
            parent_x = parent.x() if hasattr(parent, 'x') else 100
            parent_y = parent.y() if hasattr(parent, 'y') else 100
            offset_x = parent_x + 50  # Slight offset
            offset_y = parent_y + 50
        else:
            offset_x = 100
            offset_y = 100

        self.move(offset_x, offset_y)

        # Get theme colors
        self.theme = Theme()
        self.colors = self.theme.get_colors()

        # Initialize the UI
        self.initUI()

    def initUI(self):
        """Initialize the EmojiSymbolPicker UI."""
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create search row at the top
        search_layout = QHBoxLayout()

        # Search display label - set smaller padding to make it compact
        self.esp_search_disp_label = EspLabel("Search:", margin=0, padding=0, bordered=False)

        # Search input label
        self.esp_search_input_label = EspLabel("", label_type="input")

        # Add labels to search layout (left to right, close together)
        search_layout.addWidget(self.esp_search_disp_label)
        search_layout.addWidget(self.esp_search_input_label)
        search_layout.addStretch()  # Push widgets to the left

        # Add search row to main layout
        layout.addLayout(search_layout)

        # Create categories section
        self.esp_categories_section = QWidget()
        self.esp_categories_section.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors.get("section_background", "#F0F0F0")};
                border-radius: 8px;
            }}
        """)

        # Layout for categories section - use grid layout for table formation
        categories_layout = QGridLayout(self.esp_categories_section)

        # Categories section display label
        self.esp_categories_section_disp_label = EspLabel("Select emoji or symbol category")
        # Span the label across all 4 columns
        categories_layout.addWidget(self.esp_categories_section_disp_label, 0, 0, 1, 4, Qt.AlignCenter)

        # Create category buttons - Row 1
        self.esp_btn_cat_smiley = EspBtn(text="Smiley")
        self.esp_btn_cat_nature = EspBtn(text="Nature")
        self.esp_btn_cat_food = EspBtn(text="Food/Drink")
        self.esp_btn_cat_activity = EspBtn(text="Activities")

        # Create category buttons - Row 2
        self.esp_btn_cat_travel = EspBtn(text="Travel")
        self.esp_btn_cat_objects = EspBtn(text="Objects")
        self.esp_btn_cat_symbols = EspBtn(text="Symbols")
        self.esp_btn_cat_flags = EspBtn(text="Flags")

        # Position buttons in grid layout (row, column)
        # Row 1
        categories_layout.addWidget(self.esp_btn_cat_smiley, 1, 0)    # Row 1, Column 0
        categories_layout.addWidget(self.esp_btn_cat_nature, 1, 1)    # Row 1, Column 1
        categories_layout.addWidget(self.esp_btn_cat_food, 1, 2)      # Row 1, Column 2
        categories_layout.addWidget(self.esp_btn_cat_activity, 1, 3)  # Row 1, Column 3

        # Row 2
        categories_layout.addWidget(self.esp_btn_cat_travel, 2, 0)    # Row 2, Column 0
        categories_layout.addWidget(self.esp_btn_cat_objects, 2, 1)   # Row 2, Column 1
        categories_layout.addWidget(self.esp_btn_cat_symbols, 2, 2)   # Row 2, Column 2
        categories_layout.addWidget(self.esp_btn_cat_flags, 2, 3)     # Row 2, Column 3

        # Add categories section to main layout
        layout.addWidget(self.esp_categories_section)

        # Create emoji symbol selection widget with scroll area
        self.emoji_symbol_selection = self.EmojiSymbolSelection()

        # Add emoji symbol selection to main layout below categories
        layout.addWidget(self.emoji_symbol_selection)

        # Apply basic styling
        self.apply_styling()



    class EmojiSymbolSelection(QWidget):
        """
        A scrollable widget for displaying selected emoji/symbol results.
        """

        def __init__(self, parent=None):
            """
            Initialize the EmojiSymbolSelection widget.

            Args:
                parent: Parent widget (optional)
            """
            super().__init__(parent)


            # Get theme colors
            self.theme = Theme()
            self.colors = self.theme.get_colors()

            # Instantiate EspLabel objects for category headers
            self.ess_esp_label_smiley = EspLabel(text="----- Smileys -----", display_alignment="center", bordered=False)
            self.ess_esp_label_nature = EspLabel(text="----- Nature -----", display_alignment="center", bordered=False)
            self.ess_esp_label_food = EspLabel(text="----- Food/Drink -----", display_alignment="center", bordered=False)
            self.ess_esp_label_activities = EspLabel(text="----- Activities -----", display_alignment="center", bordered=False)
            self.ess_esp_label_travel = EspLabel(text="----- Travel -----", display_alignment="center", bordered=False)
            self.ess_esp_label_objects = EspLabel(text="----- Objects -----", display_alignment="center", bordered=False)
            self.ess_esp_label_symbols = EspLabel(text="----- Symbols -----", display_alignment="center", bordered=False)
            self.ess_esp_label_flags = EspLabel(text="----- Flags -----", display_alignment="center", bordered=False)


            # Initialize the UI
            self.initUI()

        def initUI(self):
            """Initialize the EmojiSymbolSelection UI."""
            # Create scroll area
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            # Create content widget for scroll area
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)

            # Add category header labels to content layout
            content_layout.addWidget(self.ess_esp_label_smiley)
            content_layout.addWidget(self.ess_esp_label_nature)
            content_layout.addWidget(self.ess_esp_label_food)
            content_layout.addWidget(self.ess_esp_label_activities)
            content_layout.addWidget(self.ess_esp_label_travel)
            content_layout.addWidget(self.ess_esp_label_objects)
            content_layout.addWidget(self.ess_esp_label_symbols)
            content_layout.addWidget(self.ess_esp_label_flags)

            # Set content widget in scroll area
            scroll_area.setWidget(content_widget)

            # Main layout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(scroll_area)

            # Apply theme styling
            self.apply_styling()

        def apply_styling(self):
            """Apply theme-based styling."""
            background_color = self.colors.get("section_background", "#F8F9FA")
            border_color = self.colors.get("border", "#CCCCCC")

            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {background_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                }}
            """)

    def apply_styling(self):
        """Apply theme-based styling to the EmojiSymbolPicker."""
        background_color = self.colors.get("background", "#FFFFFF")
        text_color = self.colors.get("text", "#000000")
        border_color = self.colors.get("border", "#CCCCCC")

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {background_color};
                color: {text_color};
                border: 1px solid {border_color};
            }}
        """)
