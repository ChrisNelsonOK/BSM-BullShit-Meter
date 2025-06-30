"""
Regional screenshot selector widget.
"""

import sys
from PyQt6.QtWidgets import QWidget, QApplication, QLabel
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap, QCursor
from PIL import ImageGrab
import pyautogui

class ScreenshotSelector(QWidget):
    """Overlay widget for selecting screenshot region."""
    
    region_selected = pyqtSignal(int, int, int, int)  # x, y, width, height
    selection_cancelled = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.selecting = False
        self.selected_rect = QRect()
        self.screenshot = None
        
        self.init_ui()
        self.take_screenshot()
    
    def init_ui(self):
        """Initialize the overlay UI."""
        # Make window fullscreen and transparent with highest priority
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.BypassWindowManagerHint |
            Qt.WindowType.CustomizeWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips)
        
        # Set very high window level to appear above everything
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        
        # Get screen geometry instead of using WindowFullScreen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        self.setGeometry(geometry)
        
        self.setMouseTracking(True)
        
        # Set crosshair cursor
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        
        # Instructions
        self.instruction_label = QLabel(
            "Click and drag to select region • ESC to cancel • ENTER to confirm",
            self
        )
        self.instruction_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.instruction_label.adjustSize()
        self.instruction_label.move(20, 20)
    
    def take_screenshot(self):
        """Take a screenshot of the entire screen."""
        try:
            # Hide this window temporarily
            self.hide()
            QApplication.processEvents()
            
            # Take screenshot
            pil_image = ImageGrab.grab()
            
            # Convert to QPixmap
            self.screenshot = QPixmap()
            self.screenshot.loadFromData(pil_image.tobytes(), 'PNG')
            
            # Show window again
            self.show()
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            self.selection_cancelled.emit()
            self.close()
    
    def mousePressEvent(self, event):
        """Handle mouse press for starting selection."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.selecting = True
            self.selected_rect = QRect()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for updating selection."""
        if self.selecting:
            self.end_point = event.pos()
            self.selected_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release for finishing selection."""
        if event.button() == Qt.MouseButton.LeftButton and self.selecting:
            self.selecting = False
            self.end_point = event.pos()
            self.selected_rect = QRect(self.start_point, self.end_point).normalized()
            
            # Only emit if we have a meaningful selection
            if self.selected_rect.width() > 10 and self.selected_rect.height() > 10:
                self.confirm_selection()
    
    def keyPressEvent(self, event):
        """Handle keyboard input."""
        if event.key() == Qt.Key.Key_Escape:
            self.selection_cancelled.emit()
            self.close()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if not self.selected_rect.isEmpty():
                self.confirm_selection()
        else:
            super().keyPressEvent(event)
    
    def confirm_selection(self):
        """Confirm the current selection."""
        if not self.selected_rect.isEmpty():
            self.region_selected.emit(
                self.selected_rect.x(),
                self.selected_rect.y(),
                self.selected_rect.width(),
                self.selected_rect.height()
            )
        self.close()
    
    def paintEvent(self, event):
        """Paint the selection overlay."""
        painter = QPainter(self)
        
        # Draw dark overlay
        overlay_color = QColor(0, 0, 0, 100)
        painter.fillRect(self.rect(), overlay_color)
        
        # If we have a selection, clear that area and draw border
        if not self.selected_rect.isEmpty():
            # Clear the selected area
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self.selected_rect, Qt.GlobalColor.transparent)
            
            # Draw selection border
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 120, 215), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(self.selected_rect)
            
            # Draw selection info
            info_text = f"{self.selected_rect.width()} × {self.selected_rect.height()}"
            painter.setPen(QPen(Qt.GlobalColor.white))
            painter.drawText(
                self.selected_rect.bottomLeft() + QPoint(5, -5),
                info_text
            )

def select_screen_region():
    """Show screenshot selector and return selected region."""
    from PyQt6.QtCore import QEventLoop
    
    selector = ScreenshotSelector()
    
    selected_region = None
    cancelled = False
    
    # Use local event loop instead of app.exec()
    loop = QEventLoop()
    
    def on_region_selected(x, y, w, h):
        nonlocal selected_region
        selected_region = (x, y, w, h)
        loop.quit()
    
    def on_cancelled():
        nonlocal cancelled
        cancelled = True
        loop.quit()
    
    selector.region_selected.connect(on_region_selected)
    selector.selection_cancelled.connect(on_cancelled)
    
    selector.show()
    selector.raise_()
    selector.activateWindow()
    
    # Run local event loop
    loop.exec()
    
    # Clean up
    selector.close()
    
    if cancelled:
        return None
    return selected_region