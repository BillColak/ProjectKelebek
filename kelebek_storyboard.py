# need some sort of graphics optimization as keeping a shit ton of story board in memory and displaying them will
# cause performance issues.. do this later...

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class StoryBoardScene(QGraphicsScene):
    def __init__(self, parent:QWidget=None):
        super().__init__(parent)

        self.setItemIndexMethod(QGraphicsScene.NoIndex)

        # settings
        self.gridSize = 20
        self.gridSquares = 5

        self.initAssets()
        self.setBackgroundBrush(self._color_background)

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._color_background = QColor("#A0A0A0")
        self._font_state = QFont("Ubuntu", 16)
        self._font_state.setStyleStrategy(QFont.PreferAntialias)

    # the drag events won't be allowed until dragMoveEvent is overriden
    def dragMoveEvent(self, event):
        """Overriden Qt's dragMoveEvent to enable Qt's Drag Events"""
        pass

    def setGrScene(self, width:int, height:int):
        """Set `width` and `height` of the `Graphics Scene`"""
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter:QPainter, rect:QRect):
        """Draw background scene grid"""
        super().drawBackground(painter, rect)
