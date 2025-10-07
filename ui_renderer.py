from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPixmap, QFont, QPen, QGuiApplication
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal, QPoint
import math
import sys

def debug_write(msg, append=True):
    mode = 'a' if append else 'w'
    with open('debug.txt', mode, encoding='utf-8') as f:
        f.write(msg + '\n')

class UIRenderer(QWidget):
    buttonClicked = pyqtSignal(str)  # Signal for button clicks

    def __init__(self):
        super().__init__()
        self.layer_radii = {1: 50, 2: 100, 3: 150}
        self.buttons = []  # List of buttons to draw
        self.center = QPointF(0, 0)
        self.button_images = {}  # Cache for QPixmap
        self.show_circles = False
        self.circles_positions = []
        self.window_bounds = None

        # Window properties
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(300, 300)
        self.hide()


    def show_window(self, center_x, center_y, show_circles=False):
        debug_write(f"Showing window at ({center_x}, {center_y}), show_circles={show_circles}")
        app = QApplication.instance()
        point = QPoint(int(center_x), int(center_y))

        # Determine the screen that contains the click point
        screen = None
        try:
            screen = QGuiApplication.screenAt(point)
        except Exception as e:
            screen = None

        if screen is not None:
            # Prefer availableGeometry to avoid taskbars and right()/bottom() off-by-one behavior
            try:
                screen_geom = screen.availableGeometry()
                debug_write(f"ScreenAt({point}) -> {screen.name()} avail-geom={screen_geom}")
            except Exception as e:
                screen_geom = screen.geometry()
                debug_write(f"ScreenAt({point}) -> {screen.name()} geom={screen_geom} (fallback)")
        else:
            try:
                desktop = app.desktop()
                screen_idx = desktop.screenNumber(point)
                if screen_idx < 0:
                    s = app.primaryScreen()
                    screen_geom = s.availableGeometry() if s is not None else app.primaryScreen().geometry()
                    debug_write(f"screenAt None and screenNumber < 0; fallback to primary avail-geom: {screen_geom}")
                else:
                    # Use availableGeometry for the specific screen index
                    screen_geom = desktop.availableGeometry(screen_idx)
                    debug_write(f"Using desktop screen #{screen_idx} avail-geom: {screen_geom}")
            except Exception as e:
                s = app.primaryScreen()
                screen_geom = s.availableGeometry() if s is not None else app.primaryScreen().geometry()
                debug_write(f"Desktop API failed; fallback to primary avail-geom: {screen_geom}")

        # Clamp center within the target screen so the 300x300 window stays fully visible on that screen
        min_cx = screen_geom.x() + 150
        max_cx = screen_geom.x() + screen_geom.width() - 150
        min_cy = screen_geom.y() + 150
        max_cy = screen_geom.y() + screen_geom.height() - 150
        center_x = max(min_cx, min(max_cx, center_x))
        center_y = max(min_cy, min(max_cy, center_y))
        debug_write(f"Clamped center to target screen: ({center_x},{center_y}) [range x:{min_cx}-{max_cx}, y:{min_cy}-{max_cy}]")

        self.center = QPointF(center_x, center_y)

        # Will assign window to target screen after show()

        self.move(int(center_x - 150), int(center_y - 150))
        debug_write(f"Window moved to ({center_x - 150}, {center_y - 150})")
        if show_circles:
            self.show_circles = True
            self.circles_positions = []
            angles = [0, 90, 180, 270]
            radius = 50  # Distance from center
            for angle in angles:
                angle_rad = math.radians(angle)
                x = 150 + radius * math.cos(angle_rad)
                y = 150 + radius * math.sin(angle_rad)
                self.circles_positions.append((x, y))
            self.window_bounds = (center_x - 150, center_y - 150, center_x + 150, center_y + 150)
            debug_write(f"Bounds set: {self.window_bounds}")
        else:
            self.show_circles = False
            self.circles_positions.clear()
        try:
            self.update()
            self.show()
            # Associate native window with the target screen after show (ensures windowHandle exists)
            try:
                handle = self.windowHandle()
                if handle is not None and screen is not None:
                    handle.setScreen(screen)
                    debug_write(f"Assigned window to screen after show: {screen.name()}")
            except Exception as e:
                debug_write(f"Failed to assign window to screen after show: {e}")
            self.raise_()
            self.activateWindow()
        except Exception as e:
            debug_write(f"Error showing window: {e}")

    def hide_window(self):
        debug_write("Hiding window")
        self.hide()
        self.buttons.clear()
        self.button_images.clear()
        self.show_circles = False
        self.circles_positions.clear()
        self.window_bounds = None

    def set_buttons(self, buttons):
        self.buttons = buttons
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw concentric circles
        painter.setPen(QPen(Qt.gray, 1))
        painter.setBrush(Qt.NoBrush)
        for radius in self.layer_radii.values():
            painter.drawEllipse(150 - radius, 150 - radius, 2 * radius, 2 * radius)

        # Draw buttons
        for button in self.buttons:
            self._draw_button(painter, button)

        # Draw circles if enabled
        if self.show_circles:
            for x, y in self.circles_positions:
                painter.setPen(QPen(Qt.white, 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(int(x - 15), int(y - 15), 30, 30)

    def _draw_button(self, painter, button):
        if button.angle is None:
            return
        angle_rad = math.radians(button.angle)
        radius = self.layer_radii.get(button.layer, 50)
        x = 150 + radius * math.cos(angle_rad)
        y = 150 + radius * math.sin(angle_rad)
        button_size = 30
        rect = QRectF(x - button_size // 2, y - button_size // 2, button_size, button_size)

        if button.identifier_type == 'color':
            painter.setPen(QPen(Qt.white, 1))
            painter.setBrush(QColor(button.identifier_value))
            painter.drawEllipse(rect)
        elif button.identifier_type in ['string', 'emoji']:
            painter.setPen(QPen(Qt.white, 1))
            painter.setBrush(Qt.blue)
            painter.drawEllipse(rect)
            painter.setFont(QFont("Arial", 12))
            painter.drawText(rect, Qt.AlignCenter, button.identifier_value)
        elif button.identifier_type == 'image':
            # Load and cache QPixmap
            if button.identifier_value not in self.button_images:
                pixmap = QPixmap(button.identifier_value)
                if pixmap.isNull():
                    pixmap = QPixmap(button_size, button_size)
                    pixmap.fill(Qt.red)  # Fallback
                else:
                    pixmap = pixmap.scaled(button_size, button_size, Qt.KeepAspectRatio)
                self.button_images[button.identifier_value] = pixmap
            pixmap = self.button_images[button.identifier_value]
            painter.drawPixmap(rect.toRect(), pixmap)

        # Label with button id for debugging
        painter.setFont(QFont("Arial", 8))
        painter.drawText(rect.bottomLeft().x(), rect.bottomLeft().y() + 15, button.id)

    def mousePressEvent(self, event):
        # Simple hit detection: check distance to center
        click_pos = event.pos()
        for button in self.buttons:
            if button.angle is None:
                continue
            angle_rad = math.radians(button.angle)
            radius = self.layer_radii.get(button.layer, 50)
            expected_x = 150 + radius * math.cos(angle_rad)
            expected_y = 150 + radius * math.sin(angle_rad)
            distance = math.hypot(click_pos.x() - expected_x, click_pos.y() - expected_y)
            if distance < 15:  # Within button radius
                self.buttonClicked.emit(button.id)
                return

    def resizeEvent(self, event):
        # Ensure window is 300x300
        super().resizeEvent(event)
        if self.size() != event.oldSize():
            self.resize(300, 300)

if __name__ == "__main__":
    # Example usage
    app = QApplication(sys.argv)
    # ui = UIRenderer()
    # ui.show()
    # sys.exit(app.exec_())
    pass
