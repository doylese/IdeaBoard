# main_application.py
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QInputDialog, QMessageBox, QStackedWidget, QLineEdit, QComboBox, QAction, QMenu, QMenuBar, QHBoxLayout, QLabel)
from IdeaBoard import IdeaBoard

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Idea Boards')
        self.setGeometry(100, 100, 1200, 800)

        # Central widget and layout
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QVBoxLayout(self.centralWidget)

        # Board names
        self.boardNameLabel = QLabel("No board selected")
        self.mainLayout.addWidget(self.boardNameLabel)

        # Stacked widget to hold multiple idea boards
        self.boardWidgets = QStackedWidget()
        self.boardWidgets.currentChanged.connect(self.updateBoardNameLabel)
        self.mainLayout.addWidget(self.boardWidgets)

        # Dictionary to store idea boards by name
        self.boards = {}

        self.setupUI()

    def setupUI(self):
        # Horizontal layout for action buttons
        self.buttonsLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.buttonsLayout)  # Add buttonsLayout to the mainLayout

        # New Board Button
        self.newBoardButton = QPushButton('New Board')
        self.newBoardButton.clicked.connect(self.createNewBoard)
        self.buttonsLayout.addWidget(self.newBoardButton)

        # Switch Board Button - allows switching between existing boards
        self.switchBoardButton = QPushButton('Switch Board')
        self.switchBoardButton.clicked.connect(self.switchBoard)
        self.buttonsLayout.addWidget(self.switchBoardButton)

        # Delete Board Button - removes the current board
        self.deleteBoardButton = QPushButton('Delete Board')
        self.deleteBoardButton.clicked.connect(self.deleteCurrentBoard)
        self.buttonsLayout.addWidget(self.deleteBoardButton)

        # Menu Bar for additional actions, kept for extended functionality
        self.menuBar = self.createMenuBar()
        self.setMenuBar(self.menuBar)

    def createMenuBar(self):
        menuBar = QMenuBar(self)

        # File menu
        fileMenu = menuBar.addMenu('&File')

        # New board action
        newBoardAction = QAction('New Board', self)
        newBoardAction.triggered.connect(self.createNewBoard)
        fileMenu.addAction(newBoardAction)

        # Switch board action
        switchBoardAction = QAction('Switch Board', self)
        switchBoardAction.triggered.connect(self.switchBoard)
        fileMenu.addAction(switchBoardAction)

        # Delete board action
        deleteBoardAction = QAction('Delete Board', self)
        deleteBoardAction.triggered.connect(self.deleteCurrentBoard)
        fileMenu.addAction(deleteBoardAction)

        return menuBar

    def createNewBoard(self):
        boardName, ok = QInputDialog.getText(self, 'New Board', 'Enter board name:')
        if ok and boardName:
            if boardName in self.boards:
                QMessageBox.warning(self, "Error", "A board with this name already exists.")
                return
            newBoard = IdeaBoard(boardName)
            self.boards[boardName] = newBoard
            self.boardWidgets.addWidget(newBoard)
            self.boardWidgets.setCurrentWidget(newBoard)

    def switchBoard(self):
        boardNames = list(self.boards.keys())
        boardName, ok = QInputDialog.getItem(self, "Switch Board", "Select a board:", boardNames, 0, False)
        if ok and boardName:
            self.boardWidgets.setCurrentWidget(self.boards[boardName])

    def deleteCurrentBoard(self):
        currentBoard = self.boardWidgets.currentWidget()
        if currentBoard:
            reply = QMessageBox.question(self, 'Delete Board', f'Are you sure you want to delete "{currentBoard.name}"?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.boardWidgets.removeWidget(currentBoard)
                del self.boards[currentBoard.name]
                currentBoard.deleteLater()
                if self.boardWidgets.count() == 0:  # No more boards left
                    self.createNewBoard()  # Prompt to create a new board

    def updateBoardNameLabel(self):
        currentBoard = self.boardWidgets.currentWidget()
        if currentBoard:
            self.boardNameLabel.setText(f"Current Board: {currentBoard.name}")
        else:
            self.boardNameLabel.setText("No board selected")

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainApplication()
    mainWindow.show()
    sys.exit(app.exec_())
