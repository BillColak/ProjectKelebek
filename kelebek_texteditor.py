
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
# import sys


class MyHighlighter(QSyntaxHighlighter):

    def __init__(self, parent, theme):
        QSyntaxHighlighter.__init__(self, parent)
        self.parent = parent
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

    def highlightBlock(self, text):  # todo
        for rule in self.highlightingRules:
            expression = QRegExp(rule.pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, rule.format)
                # index = text.indexOf(expression, index + length)
                index = -1
        self.setCurrentBlockState(0)


class HighlightingRule():
    def __init__(self, pattern, format):
        self.pattern = pattern
        self.format = format


class FactoryNodeOpTextEdit(QTextEdit):
    def __init__(self, *args):
        super(FactoryNodeOpTextEdit, self).__init__(*args)
        highlighter = MyHighlighter(self, "Classic")


class KelebekSyntaxHighlighter(QWidget):
    def __init__(self, socket_handler, parent: QWidget = None):
        super().__init__(parent)
        self.socket_handler = socket_handler
        self.setLayout(QVBoxLayout())
        self.textEdit = FactoryNodeOpTextEdit()
        self.button = QPushButton("eval", clicked=self.evalEditorText)

        self.add_socket = QPushButton(QIcon('icons/add.png'), "Add Socket", clicked=self.socket_handler.insertSocket)
        # self.add_socket.setStyleSheet("background-color: #00d100; color: #000000;")

        self.save_node = QPushButton(QIcon('icons/add.png'), "Save", clicked=self.socket_handler.insertSocket)
        self.save_node.setStyleSheet("background-color: #00d100; color: #000000;")

        self.layout().addWidget(self.textEdit)
        btn_lay = QHBoxLayout()
        self.layout().addLayout(btn_lay)
        btn_lay.addWidget(self.button)
        btn_lay.addWidget(self.add_socket)
        btn_lay.addWidget(self.save_node)

        # self.layout().addWidget(self.button)
        # self.layout().addWidget(self.add_socket)

    def evalEditorText(self):
        text = self.textEdit.toPlainText()  # capture the white spaces as well
        print(text)
        # eval(text)








# class App(QMainWindow):
#     def __init__(self):
#         QMainWindow.__init__(self)
#         font = QFont()
#         font.setFamily("Courier")
#         font.setFixedPitch(True)
#         font.setPointSize(10)
#         editor = QTextEdit()
#         editor.setFont(font)
#         highlighter = MyHighlighter(editor, "Classic")
#         self.setCentralWidget(editor)
#         self.setWindowTitle("Syntax Highlighter")
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = App()
#     window.show()
#     sys.exit(app.exec_())
