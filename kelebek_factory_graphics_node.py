
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from nodeeditor.node_node import Node

LEFT_TOP = 1        #:
LEFT_CENTER =2      #:
LEFT_BOTTOM = 3     #:
RIGHT_TOP = 4       #:
RIGHT_CENTER = 5    #:
RIGHT_BOTTOM = 6    #:


class ResizableNode(QGraphicsObject):

    size_changed = pyqtSignal(object)

    # TODO add min size
    def __init__(self, node: 'Node', parent: QWidget = None):
        super().__init__()
        self.node = node

        # init our flags
        self.hovered = False
        self._was_moved = False
        self._last_selected_state = False

        self.mousePressPos = None
        self.mousePressRect = None

        self.rect = QRect(0, 0, 240, 180)

        self.moving = False
        self.hovered = False
        self.origin = QPoint()

        self.initSizes()
        self.initAssets()
        self.initUI()

        self.size_changed.connect(self.move_sockets)

    def move_sockets(self, s):
        for output_socket in self.node.outputs:
            top_offset = self.title_height + 2 * self.title_vertical_padding + self.edge_padding
            available_height = s.height() - top_offset
            y = top_offset + available_height / 2.0 + (output_socket.index-0.5) * self.node.socket_spacing
            output_socket.grSocket.setPos(s.width()+1, y)
            # print(s.width()+1, y)

        for input_socket in self.node.inputs:

            if input_socket.position in (LEFT_BOTTOM, RIGHT_BOTTOM):
                y = s.height() - self.edge_roundness - self.title_vertical_padding - input_socket.index * self.node.socket_spacing
            elif input_socket.position in (LEFT_CENTER, RIGHT_CENTER):
                num_sockets = input_socket.count_on_this_node_side
                node_height = s.height()
                top_offset = self.title_height + 2 * self.title_vertical_padding + self.edge_padding
                available_height = node_height - top_offset
                y = top_offset + available_height / 2.0 + (input_socket.index - 0.5) * self.node.socket_spacing
                if num_sockets > 1:
                    y -= self.node.socket_spacing * (num_sockets - 1) / 2
            elif input_socket.position in (LEFT_TOP, RIGHT_TOP):

                y = self.title_height + self.title_vertical_padding + self.edge_roundness + input_socket.index * self.node.socket_spacing
            else:
                y = 0
            input_socket.grSocket.setPos(-1, y)

    def changeTitleColor(self, color):
        self.brush_title = str(color)
        self.update()

    @property
    def content(self):
        """Reference to `Node Content`"""
        return self.node.content if self.node else None

    @property
    def title(self):
        """title of this `Node`

        :getter: current Graphics Node title
        :setter: stores and make visible the new title
        :type: str
        """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    def setTitle(self, value):
        self._title = value
        self.node.title = value
        self.title_item.setPlainText(self._title)

    def initUI(self):
        """Set up this ``QGraphicsItem``"""
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)

        # init title
        self.initTitle()
        self.title = self.node.title

        self.initContent()

    # TODO initsizes, assets, content and title should be stored in a json file.
    def initSizes(self):
        """Set up internal attributes like `width`, `height`, etc."""
        self.width = self.rect.width()  # todo get rid of these when have a chance
        self.height = self.rect.height()
        self.edge_roundness = 10.0
        self.edge_padding = 0
        self.title_height = 24.0
        self.title_horizontal_padding = 4.0
        self.title_vertical_padding = 4.0

    def initAssets(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._title_color = Qt.white
        self._title_font = QFont("Ubuntu", 10)

        self._color = QColor("#7F000000")
        self._color_selected = QColor("#FFFFA637")
        self._color_hovered = QColor("#FF37A6FF")

        self._pen_default = QPen(self._color)
        self._pen_default.setWidthF(2.0)
        self._pen_selected = QPen(self._color_selected)
        self._pen_selected.setWidthF(2.0)
        self._pen_hovered = QPen(self._color_hovered)
        self._pen_hovered.setWidthF(3.0)

        self.brush_title = "#51CD47"
        self._brush_background = QBrush(QColor("#E3212121"))

    def initContent(self):
        """Set up the `grContent` - ``QGraphicsProxyWidget`` to have a container for `Graphics Content`"""
        if self.content is not None:
            self.content.setGeometry(self.edge_padding, self.title_height + self.edge_padding,
                                     self.width - 2 * self.edge_padding,
                                     self.height - 2 * self.edge_padding - self.title_height)

        # get the QGraphicsProxyWidget when inserted into the grScene
        self.grContent = self.node.scene.grScene.addWidget(self.content)
        self.grContent.node = self.node
        self.grContent.setParentItem(self)

    def initTitle(self):
        """Set up the title Graphics representation: font, color, position, etc."""
        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, 0)
        self.title_item.setTextWidth(
            self.rect.width()
            - 2 * self.title_horizontal_padding
        )


    def onSelected(self):
        """Our event handling when the node was selected"""
        self.node.scene.grScene.itemSelected.emit()

    def doSelect(self, new_state=True):
        """Safe version of selecting the `Graphics Node`. Takes care about the selection state flag used internally

        :param new_state: ``True`` to select, ``False`` to deselect
        :type new_state: ``bool``
        """
        self.setSelected(new_state)
        self._last_selected_state = new_state
        if new_state: self.onSelected()

    def corner_rect(self) -> QRect:
        """ Return corner rect geometry """
        return QRect(self.rect.right() - 10, self.rect.bottom() - 10, 10, 10)

    def boundingRect(self) -> QRectF:
        """ Override boundingRect """
        rectf = QRectF(self.rect).normalized()
        return rectf

    def paint(self, painter: QPainter, option, widget=None):
        """ OVerride paint  """

        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.rect.width(), self.title_height, self.edge_roundness, self.edge_roundness)
        path_title.addRect(0, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        path_title.addRect(self.rect.width() - self.edge_roundness, self.title_height - self.edge_roundness,
                           self.edge_roundness, self.edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(str(self.brush_title))))
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.rect.width(), self.rect.height() - self.title_height,
                                    self.edge_roundness, self.edge_roundness)
        path_content.addRect(0, self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(self.rect.width() - self.edge_roundness, self.title_height, self.edge_roundness,
                             self.edge_roundness)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(QRectF(self.rect), 10, 10)
        painter.setBrush(Qt.NoBrush)
        if self.hovered:
            painter.setPen(self._pen_hovered)
            painter.drawPath(path_outline.simplified())
            painter.setPen(self._pen_default)
            painter.drawPath(path_outline.simplified())
        else:
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
            painter.drawPath(path_outline.simplified())
        self.update()

    def hoverMoveEvent(self, event: QMouseEvent):
        """ Override hover move Event : Display cursor """
        if self.isSelected() & self.corner_rect().contains(event.pos().toPoint()):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        super().hoverMoveEvent(event)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        """Handle hover effect"""
        self.hovered = False
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """ override mouse Press Event """
        if self.isSelected() & self.corner_rect().contains(
                QPoint(event.pos().toPoint())
        ):
            self.moving = True
            self.origin = self.rect.topLeft()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """ Override mouse release event """
        self.moving = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """ Override mouse move event """
        if self.moving:
            self.prepareGeometryChange()

            pos = event.pos().toPoint()

            if pos.x() >= self.origin.x():
                self.rect.setRight(pos.x())
            else:
                self.rect.setLeft(pos.x())
            if pos.y() >= self.origin.y():
                self.rect.setBottom(pos.y())
            else:
                self.rect.setTop(pos.y())
            self.rect = self.rect.normalized()
            self.update()
            self.size_changed.emit(self.rect)  # emit size after resizing.
            if self.node.grNode.isSelected():
                self.node.updateConnectedEdges()
            return
        else:
            super().mouseMoveEvent(event)
