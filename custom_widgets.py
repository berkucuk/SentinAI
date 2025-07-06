from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QBrush

class SimpleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._off_color = QColor("#cccccc")
        self._on_color = QColor("#4c8be8")
        self._knob_color = QColor("#ffffff")

        self.stateChanged.connect(self.update)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        rect = QRectF(0, 0, self.width(), self.height())
        
        bg_color = self._on_color if self.isChecked() else self._off_color
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect, self.height() / 2, self.height() / 2)

        knob_radius = self.height() - 6
        if self.isChecked():
            knob_x = self.width() - knob_radius - 3
        else:
            knob_x = 3
        
        knob_rect = QRectF(knob_x, 3, knob_radius, knob_radius)
        painter.setBrush(QBrush(self._knob_color))
        painter.drawEllipse(knob_rect)

    def hitButton(self, pos: QPointF) -> bool:
        return self.contentsRect().contains(pos)