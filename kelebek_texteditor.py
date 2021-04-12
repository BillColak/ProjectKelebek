import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
# import sys


class MyHighlighter(QSyntaxHighlighter):

    def __init__(self, parent):
        QSyntaxHighlighter.__init__(self, parent)
        self.parent = parent
        # self.node_inputs = QTextCharFormat()
        keyword = QTextCharFormat()
        reservedClasses = QTextCharFormat()
        assignmentOperator = QTextCharFormat()
        delimiter = QTextCharFormat()
        specialConstant = QTextCharFormat()
        boolean = QTextCharFormat()
        number = QTextCharFormat()
        comment = QTextCharFormat()
        string = QTextCharFormat()
        singleQuotedString = QTextCharFormat()

        self.highlightingRules = []

        # keyword
        brush = QBrush(Qt.darkBlue, Qt.SolidPattern)
        keyword.setForeground(brush)
        keyword.setFontWeight(QFont.Bold)
        keywords = ["break", "else", "for", "if", "in",
                    "next", "repeat", "return", "switch",
                    "try", "while"]
        for word in keywords:
            pattern = QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, keyword)
            self.highlightingRules.append(rule)

        # reservedClasses
        reservedClasses.setForeground(brush)
        reservedClasses.setFontWeight(QFont.Bold)
        keywords = ["array", "character", "complex",
                    "data.frame", "double", "factor",
                    "function", "integer", "list",
                    "logical", "matrix", "numeric",
                    "vector"]
        for word in keywords:
            pattern = QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, reservedClasses)
            self.highlightingRules.append(rule)

        # assignmentOperator
        brush = QBrush(Qt.yellow, Qt.SolidPattern)
        pattern = QRegExp("(<){1,2}-")
        assignmentOperator.setForeground(brush)
        assignmentOperator.setFontWeight(QFont.Bold)
        rule = HighlightingRule(pattern, assignmentOperator)
        self.highlightingRules.append(rule)

        # delimiter
        pattern = QRegExp("[\)\(]+|[\{\}]+|[][]+")
        delimiter.setForeground(brush)
        delimiter.setFontWeight(QFont.Bold)
        rule = HighlightingRule(pattern, delimiter)
        self.highlightingRules.append(rule)

        # specialConstant
        brush = QBrush(Qt.green, Qt.SolidPattern)
        specialConstant.setForeground(brush)
        keywords = ["Inf", "NA", "NaN", "NULL"]
        for word in keywords:
            pattern = QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, specialConstant)
            self.highlightingRules.append(rule)

        # boolean
        boolean.setForeground(brush)
        keywords = ["TRUE", "FALSE"]
        for word in keywords:
            pattern = QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule(pattern, boolean)
            self.highlightingRules.append(rule)

        # number
        pattern = QRegExp("[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?")
        pattern.setMinimal(True)
        number.setForeground(brush)
        rule = HighlightingRule(pattern, number)
        self.highlightingRules.append(rule)

        # comment
        brush = QBrush(Qt.blue, Qt.SolidPattern)
        pattern = QRegExp("#[^\n]*")
        comment.setForeground(brush)
        rule = HighlightingRule(pattern, comment)
        self.highlightingRules.append(rule)

        # string
        brush = QBrush(Qt.red, Qt.SolidPattern)
        pattern = QRegExp("\".*\"")
        pattern.setMinimal(True)
        string.setForeground(brush)
        rule = HighlightingRule(pattern, string)
        self.highlightingRules.append(rule)

        # singleQuotedString
        pattern = QRegExp("\'.*\'")
        pattern.setMinimal(True)
        singleQuotedString.setForeground(brush)
        rule = HighlightingRule(pattern, singleQuotedString)
        self.highlightingRules.append(rule)

        # self.commentStartExpression = QRegExp("/\\*")
        # self.commentEndExpression = QRegExp("\\*/")

    def highlightBlock(self, text):  # todo
        # for pattern, format in self.highlightingRules:
        for rule in self.highlightingRules:
            expression = QRegExp(rule.pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, rule.format)
                index = expression.indexIn(text, index + length)
        self.setCurrentBlockState(0)

        #  #The code below is for making comments in c++
        # startIndex = 0
        # if self.previousBlockState() != 1:
        #     startIndex = self.commentStartExpression.indexIn(text)
        #
        # while startIndex >= 0:
        #     endIndex = self.commentEndExpression.indexIn(text, startIndex)
        #
        #     if endIndex == -1:
        #         self.setCurrentBlockState(1)
        #         commentLength = len(text) - startIndex
        #     else:
        #         commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()
        #
        #     self.setFormat(startIndex, commentLength,
        #             self.multiLineCommentFormat)
        #     startIndex = self.commentStartExpression.indexIn(text,
        #             startIndex + commentLength)

        #  #Alternative way
        # for rule in self.highlightingRules:
        #     expression = QRegExp(rule.pattern)
        #     index = expression.indexIn(text)
        #     while index >= 0:
        #         length = expression.matchedLength()
        #         self.setFormat(index, length, rule.format)
        #         # index = text.indexOf(expression, index + length)
        #         index = -1
        # self.setCurrentBlockState(0)


class HighlightingRule():
    def __init__(self, pattern, format):
        self.pattern = pattern
        self.format = format


class FactoryNodeOpTextEdit(QTextEdit):
    textEditor_clicked = pyqtSignal()

    def __init__(self, *args):
        super(FactoryNodeOpTextEdit, self).__init__(*args)

        self.highlighter = MyHighlighter(self)

    def s_highlight(self):
        return self.highlighter

    def mousePressEvent(self, e: QMouseEvent) -> None:
        super().mousePressEvent(e)
        self.textEditor_clicked.emit()


class KelebekSyntaxHighlighter(QWidget):

    save_signal = pyqtSignal(object)
    emit_eval = pyqtSignal(object)

    def __init__(self, socket_handler, parent: QWidget = None):
        super().__init__(parent)

        self.socket_handler = socket_handler
        self.setLayout(QVBoxLayout())
        self.textEdit = FactoryNodeOpTextEdit()
        self.textEdit.textEditor_clicked.connect(self.addSyntax)
        self.button = QPushButton("eval", clicked=self.evalText)

        self.add_socket = QPushButton(QIcon('icons/add.png'), "Add Socket", clicked=self.socket_handler.insertSocket)
        # self.add_socket.setStyleSheet("background-color: #00d100; color: #000000;")

        self.save_node = QPushButton("Save", clicked=self.saveNodeSignal)
        self.save_node.setStyleSheet("background-color: #00d100; color: #000000;")

        self.layout().addWidget(self.textEdit)
        btn_lay = QHBoxLayout()
        self.layout().addLayout(btn_lay)
        btn_lay.addWidget(self.button)
        btn_lay.addWidget(self.add_socket)
        btn_lay.addWidget(self.save_node)

    def addSyntax(self):
        for k, v in self.socket_handler.getSocketsNameType():
            keyword = QTextCharFormat()
            brush = QBrush(QColor(v), Qt.SolidPattern)
            keyword.setForeground(brush)
            keyword.setFontWeight(QFont.Bold)

            pattern = QRegExp("\\b" + k + "\\b")
            rule = HighlightingRule(pattern, keyword)
            highlighter = self.textEdit.s_highlight()
            highlighter.highlightingRules.append(rule)
            highlighter.rehighlight()

    def saveNodeSignal(self):
        text = self.textEdit.toPlainText()
        self.save_signal.emit(text)

    def evalText(self):
        text = self.textEdit.toPlainText()
        self.emit_eval.emit(text)

    # def evalText(self):
    #     # https://realpython.com/python-eval-function/#general-purpose-expressions
    #
    #     x = {'input1': 55, 'input2': 5}
    #     try:
    #         text = self.textEdit.toPlainText()
    #         evaluation = eval(text, x)
    #         print(evaluation)
    #     except Exception as e:
    #         print("Exception:", e)
    #
    #
