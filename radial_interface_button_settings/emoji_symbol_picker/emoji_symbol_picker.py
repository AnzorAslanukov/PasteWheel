from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QTableView
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QColor, QFont
from theme import Theme
from radial_interface_button_settings.emoji_symbol_picker.esp_label import EspLabel
from radial_interface_button_settings.emoji_symbol_picker.esp_btn import EspBtn
from pastewheel_config import PasteWheelConfig
import emoji as emoji_lib  # type: ignore


# Global variables for emoji cell sizing - modify these to change all table cell dimensions
EMOJI_CELL_WIDTH = 80      # Width of each emoji cell in pixels
EMOJI_CELL_HEIGHT = 48     # Height of each emoji cell in pixels
EMOJI_FONT_SIZE = 30       # Font size for emoji display in pixels
EMOJI_CELL_PADDING = 0     # Padding inside each emoji cell in pixels
EMOJI_TABLE_PADDING = 8    # Padding around the table in pixels


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



    class EmojiCategoryTableModel(QAbstractTableModel):
        """
        Table model for displaying emoji/symbol data in a category.
        Optimized to display emojis in a 6-column grid for proper width fitting.
        """

        def __init__(self, emoji_data=None, parent=None):
            """
            Initialize the table model.

            Args:
                emoji_data: Dictionary of emoji records for this category
                parent: Parent widget (optional)
            """
            super().__init__(parent)
            self.emoji_data = emoji_data or {}
            # Convert to sorted list once at initialization for efficiency
            self.emoji_list = sorted(self.emoji_data.items(), key=lambda x: x[0]) if self.emoji_data else []
            # Pre-calculate row count for efficiency (4 columns per row)
            self._row_count = (len(self.emoji_list) + 3) // 4
            self.theme = Theme()
            self.colors = self.theme.get_colors()

        def rowCount(self, parent=QModelIndex()):
            """Return the number of rows in the model."""
            return self._row_count

        def columnCount(self, parent=QModelIndex()):
            """Return the number of columns in the model (fixed to 4 for larger emoji size)."""
            return 4

        def data(self, index, role=Qt.DisplayRole):
            """Return the data for the given role and section in the model."""
            if not index.isValid():
                return None

            total_emojis = len(self.emoji_list)
            emoji_index = (index.row() * 4) + index.column()

            if emoji_index >= total_emojis:
                return None

            if role == Qt.DisplayRole:
                code, info = self.emoji_list[emoji_index]
                try:
                    return emoji_lib.emojize(code)
                except Exception:
                    return code

            if role == Qt.ToolTipRole:
                code, info = self.emoji_list[emoji_index]
                return info.get("description", "")

            if role == Qt.BackgroundRole:
                # Let the view handle alternating colors through stylesheet
                return None

            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter

            if role == Qt.FontRole:
                font = QFont()
                font.setPixelSize(EMOJI_FONT_SIZE)  # Font size using global variable
                return font

            return None

        def headerData(self, section, orientation, role=Qt.DisplayRole):
            """Return the header data for the given role and section."""
            if role == Qt.DisplayRole and orientation == Qt.Horizontal:
                return f"Col {section + 1}"
            return None

    class EmojiSymbolSelection(QWidget):
        """
        A scrollable widget for displaying selected emoji/symbol results.
        Manages global selection state across all table views.
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

            # Store all table views for global selection management
            self.all_table_views = []

            # Instantiate EspLabel objects for category headers
            self.ess_esp_label_smiley = EspLabel(text="----- Smileys -----", display_alignment="center", bordered=False)
            self.ess_esp_label_nature = EspLabel(text="----- Nature -----", display_alignment="center", bordered=False)
            self.ess_esp_label_food = EspLabel(text="----- Food/Drink -----", display_alignment="center", bordered=False)
            self.ess_esp_label_activities = EspLabel(text="----- Activities -----", display_alignment="center", bordered=False)
            self.ess_esp_label_travel = EspLabel(text="----- Travel -----", display_alignment="center", bordered=False)
            self.ess_esp_label_objects = EspLabel(text="----- Objects -----", display_alignment="center", bordered=False)
            self.ess_esp_label_symbols = EspLabel(text="----- Symbols -----", display_alignment="center", bordered=False)
            self.ess_esp_label_flags = EspLabel(text="----- Flags -----", display_alignment="center", bordered=False)

            # Instantiate QTableView models for category headers following naming convention
            self.ess_qtableview_model_smiley = EmojiSymbolPicker.EmojiCategoryTableModel()
            self.ess_qtableview_model_nature = EmojiSymbolPicker.EmojiCategoryTableModel()
            self.ess_qtableview_model_food = EmojiSymbolPicker.EmojiCategoryTableModel()
            self.ess_qtableview_model_activities = EmojiSymbolPicker.EmojiCategoryTableModel()
            self.ess_qtableview_model_travel = EmojiSymbolPicker.EmojiCategoryTableModel()
            self.ess_qtableview_model_objects = EmojiSymbolPicker.EmojiCategoryTableModel()
            self.ess_qtableview_model_symbols = EmojiSymbolPicker.EmojiCategoryTableModel()
            self.ess_qtableview_model_flags = EmojiSymbolPicker.EmojiCategoryTableModel()

            # Populate models with emoji data by category
            self.populate_models()

            # Initialize the UI
            self.initUI()

        def clear_all_selections(self):
            """Clear selections in all table views."""
            for table_view in self.all_table_views:
                table_view.selectionModel().clearSelection()

        def populate_models(self):
            """Populate all table models with categorized emoji data efficiently."""
            emoji_data = PasteWheelConfig.get_all_emojis()
            if not isinstance(emoji_data, dict):
                return

            # Category mapping
            category_map = {
                "smiley": self.ess_qtableview_model_smiley,
                "nature": self.ess_qtableview_model_nature,
                "food": self.ess_qtableview_model_food,
                "activities": self.ess_qtableview_model_activities,
                "travel": self.ess_qtableview_model_travel,
                "objects": self.ess_qtableview_model_objects,
                "symbols": self.ess_qtableview_model_symbols,
                "flags": self.ess_qtableview_model_flags,
            }

            # Group by category once - optimization to avoid repeated categorization
            category_data = {}
            for code, info in emoji_data.items():
                cat = (info.get("category") or "").strip().lower()
                if cat:
                    if cat not in category_data:
                        category_data[cat] = {}
                    category_data[cat][code] = info

            # Set categorized data in each model efficiently
            for cat, model in category_map.items():
                model.emoji_data = category_data.get(cat, {})
                model.emoji_list = sorted(model.emoji_data.items(), key=lambda x: x[0])
                # Pre-calculate row count for efficiency (4 columns per row)
                model._row_count = (len(model.emoji_list) + 3) // 4
                model.layoutChanged.emit()

        def populate_models(self):
            """Populate all table models with categorized emoji data efficiently."""
            emoji_data = PasteWheelConfig.get_all_emojis()
            if not isinstance(emoji_data, dict):
                return

            # Category mapping
            category_map = {
                "smiley": self.ess_qtableview_model_smiley,
                "nature": self.ess_qtableview_model_nature,
                "food": self.ess_qtableview_model_food,
                "activities": self.ess_qtableview_model_activities,
                "travel": self.ess_qtableview_model_travel,
                "objects": self.ess_qtableview_model_objects,
                "symbols": self.ess_qtableview_model_symbols,
                "flags": self.ess_qtableview_model_flags,
            }

            # Group by category once - optimization to avoid repeated categorization
            category_data = {}
            for code, info in emoji_data.items():
                cat = (info.get("category") or "").strip().lower()
                if cat:
                    if cat not in category_data:
                        category_data[cat] = {}
                    category_data[cat][code] = info

            # Set categorized data in each model efficiently
            for cat, model in category_map.items():
                model.emoji_data = category_data.get(cat, {})
                model.emoji_list = sorted(model.emoji_data.items(), key=lambda x: x[0])
                # Pre-calculate row count for efficiency (4 columns per row)
                model._row_count = (len(model.emoji_list) + 3) // 4
                model.layoutChanged.emit()

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

            # Add category header labels and table views to content layout
            content_layout.addWidget(self.ess_esp_label_smiley)
            smiley_table = self.create_table_view(self.ess_qtableview_model_smiley)
            self.all_table_views.append(smiley_table)
            content_layout.addWidget(smiley_table)

            content_layout.addWidget(self.ess_esp_label_nature)
            nature_table = self.create_table_view(self.ess_qtableview_model_nature)
            self.all_table_views.append(nature_table)
            content_layout.addWidget(nature_table)

            content_layout.addWidget(self.ess_esp_label_food)
            food_table = self.create_table_view(self.ess_qtableview_model_food)
            self.all_table_views.append(food_table)
            content_layout.addWidget(food_table)

            content_layout.addWidget(self.ess_esp_label_activities)
            activities_table = self.create_table_view(self.ess_qtableview_model_activities)
            self.all_table_views.append(activities_table)
            content_layout.addWidget(activities_table)

            content_layout.addWidget(self.ess_esp_label_travel)
            travel_table = self.create_table_view(self.ess_qtableview_model_travel)
            self.all_table_views.append(travel_table)
            content_layout.addWidget(travel_table)

            content_layout.addWidget(self.ess_esp_label_objects)
            objects_table = self.create_table_view(self.ess_qtableview_model_objects)
            self.all_table_views.append(objects_table)
            content_layout.addWidget(objects_table)

            content_layout.addWidget(self.ess_esp_label_symbols)
            symbols_table = self.create_table_view(self.ess_qtableview_model_symbols)
            self.all_table_views.append(symbols_table)
            content_layout.addWidget(symbols_table)

            content_layout.addWidget(self.ess_esp_label_flags)
            flags_table = self.create_table_view(self.ess_qtableview_model_flags)
            self.all_table_views.append(flags_table)
            content_layout.addWidget(flags_table)

            # Set content widget in scroll area
            scroll_area.setWidget(content_widget)

            # Main layout
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(scroll_area)

            # Apply theme styling
            self.apply_styling()

        def create_table_view(self, model):
            """Create and configure a QTableView for the given model."""
            table_view = QTableView()
            table_view.setModel(model)

            # Get theme colors for styling
            theme = Theme()
            colors = theme.get_colors()

            # Configure table view for emoji display
            table_view.setGridStyle(Qt.DotLine)
            table_view.setAlternatingRowColors(False)  # Disable alternating colors to use stylesheet
            table_view.setSelectionMode(QTableView.SingleSelection)  # Allow only one selection at a time
            table_view.setSelectionBehavior(QTableView.SelectItems)

            # Hide headers
            table_view.verticalHeader().setVisible(False)
            table_view.horizontalHeader().setVisible(False)

            # Set row height for consistent emoji display using global variable
            table_view.verticalHeader().setDefaultSectionSize(EMOJI_CELL_HEIGHT)
            # Set column width for 4-column layout using global variable
            table_view.horizontalHeader().setDefaultSectionSize(EMOJI_CELL_WIDTH)

            # Set fixed table size to ensure all columns are visible using global variables
            table_view.setFixedWidth(4 * EMOJI_CELL_WIDTH + EMOJI_TABLE_PADDING)  # 4 columns * width + padding
            table_view.setFixedHeight(model.rowCount() * EMOJI_CELL_HEIGHT + EMOJI_TABLE_PADDING)  # rows * height + padding

            # Disable editing
            table_view.setEditTriggers(QTableView.NoEditTriggers)

            # Disable horizontal scrolling since we want to fit all columns
            table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            # Override mouse press event to implement exclusive selection behavior
            original_mouse_press = table_view.mousePressEvent

            def custom_mouse_press_event(event):
                index = table_view.indexAt(event.pos())
                if index.isValid():
                    # Clear all selections across ALL table views first, then select the new cell
                    self.clear_all_selections()
                    table_view.selectionModel().select(index, table_view.selectionModel().Select)
                    event.accept()
                else:
                    original_mouse_press(event)

            table_view.mousePressEvent = custom_mouse_press_event

            # Apply theme styling to the table view
            table_style = f"""
                QTableView {{
                    background-color: {colors.get("table_background", "#FFFFFF")};
                    border: 1px solid {colors.get("table_border", "#E0E0E0")};
                    border-radius: 4px;
                    gridline-color: {colors.get("table_gridline", "#F0F0F0")};
                    color: {colors.get("table_text", "#000000")};
                    selection-background-color: {colors.get("table_selection_background", "#007BFF")};
                    selection-color: {colors.get("table_selection_text", "#FFFFFF")};
                }}
                QTableView::item {{
                    padding: {EMOJI_CELL_PADDING}px;
                    border-bottom: 1px solid {colors.get("table_gridline", "#F0F0F0")};
                }}
                QTableView::item:selected {{
                    background-color: {colors.get("table_selection_background", "#007BFF")};
                    color: {colors.get("table_selection_text", "#FFFFFF")};
                }}
                QTableView::item:hover {{
                    background-color: {colors.get("table_hover_background", "#E8F4F8")};
                }}
                QTableView::item:alternate {{
                    background-color: {colors.get("table_background", "#FFFFFF")};
                }}
            """
            table_view.setStyleSheet(table_style)

            return table_view

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
