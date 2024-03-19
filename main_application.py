from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QInputDialog, QMessageBox,
                             QStackedWidget, QAction, QMenu, QMenuBar, QHBoxLayout, QLabel, QGraphicsView)
from IdeaBoard import IdeaBoard
from BackupClient import BackupClient
import sys
import json
import os


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Idea Boards')
        self.setGeometry(100, 100, 1200, 800)

        # Central widget and layout
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QVBoxLayout(self.centralWidget)

        self.boardNameLabel = QLabel("No board selected")
        self.mainLayout.addWidget(self.boardNameLabel)

        self.boardWidgets = QStackedWidget()
        self.boardWidgets.currentChanged.connect(self.updateBoardNameLabel)
        self.mainLayout.addWidget(self.boardWidgets)

        self.boards = {}

        self.setupUI()

        # Initialize the BackupClient (adjust src_dir and interval as needed)
        self.backupClient = BackupClient(
            src_dir=r"C:\Users\hamme\Desktop\Software Enginnering 1\Idea Board Project\Backups\ideaboard_backup.json",
            interval=60)

        # Start the backup microservice
        self.backupClient.start_microservice()

    def setupUI(self):
        self.buttonsLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.buttonsLayout)

        self.newBoardButton = QPushButton('New Board')
        self.newBoardButton.clicked.connect(self.createNewBoard)
        self.buttonsLayout.addWidget(self.newBoardButton)

        self.switchBoardButton = QPushButton('Switch Board')
        self.switchBoardButton.clicked.connect(self.switchBoard)
        self.buttonsLayout.addWidget(self.switchBoardButton)

        self.deleteBoardButton = QPushButton('Delete Board')
        self.deleteBoardButton.clicked.connect(self.deleteCurrentBoard)
        self.buttonsLayout.addWidget(self.deleteBoardButton)

        self.menuBar = self.createMenuBar()
        self.setMenuBar(self.menuBar)

        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.saveData)
        self.mainLayout.addWidget(self.saveButton)

        self.backupButton = QPushButton('Backup')
        self.backupButton.clicked.connect(self.backupData)
        self.mainLayout.addWidget(self.backupButton)

        self.restoreButton = QPushButton('Restore')
        self.restoreButton.clicked.connect(self.restoreData)
        self.mainLayout.addWidget(self.restoreButton)

    def createMenuBar(self):
        menuBar = QMenuBar(self)
        fileMenu = menuBar.addMenu('&File')

        newBoardAction = QAction('New Board', self)
        newBoardAction.triggered.connect(self.createNewBoard)
        fileMenu.addAction(newBoardAction)

        switchBoardAction = QAction('Switch Board', self)
        switchBoardAction.triggered.connect(self.switchBoard)
        fileMenu.addAction(switchBoardAction)

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
            reply = QMessageBox.question(self, 'Delete Board',
                                         f'Are you sure you want to delete "{currentBoard.name}"?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.boardWidgets.removeWidget(currentBoard)
                del self.boards[currentBoard.name]
                currentBoard.deleteLater()
                if self.boardWidgets.count() == 0:
                    self.createNewBoard()

    def updateBoardNameLabel(self):
        currentBoard = self.boardWidgets.currentWidget()
        if currentBoard:
            self.boardNameLabel.setText(f"Current Board: {currentBoard.name}")
        else:
            self.boardNameLabel.setText("No board selected")

    def saveData(self):
        """Saves the current state of all IdeaBoards to a JSON file."""
        data_to_save = {}
        for board_name, board_widget in self.boards.items():
            data_to_save[board_name] = board_widget.serialize()  # Serialize each board

        save_path = r"C:\Users\hamme\Desktop\Software Enginnering 1\Idea Board Project\Backups\ideaboard_backup.json"
        try:
            with open(save_path, 'w') as file:
                json.dump(data_to_save, file, indent=4)
            QMessageBox.information(self, "Success", "Data saved successfully.")
            self.backupClient.src_dir = save_path  # Update the source directory for the backup client
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {e}")

    def backupData(self):
        """Backs up the saved JSON file using the microservice."""
        self.backupClient.send_command("Backup")
        response = self.backupClient.receive_response()
        if response:
            QMessageBox.information(self, "Backup", "Backup initiated successfully.")

    def restoreData(self):
        """Restores the IdeaBoard from the latest backup."""
        self.backupClient.send_command("Revert")
        response = self.backupClient.receive_response()
        if response:
            try:
                with open(response, 'r') as file:  # Assuming response is the path to the restored file
                    data = json.load(file)
                self.clearIdeaBoards()
                self.repopulateIdeaBoards(data)
                QMessageBox.information(self, "Restore", "Data restored successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Restore Error", f"Failed to restore data: {e}")

    def clearIdeaBoards(self):
        """Clears the current state of the IdeaBoards."""
        for board_name in list(self.boards.keys()):
            self.deleteCurrentBoard()  # Assuming deleteBoard is implemented

    def repopulateIdeaBoards(self, data):
        """Repopulates the IdeaBoards based on the provided data."""
        for board_name, board_data in data.items():
            new_board = IdeaBoard(board_name)
            self.boards[board_name] = new_board
            self.boardWidgets.addWidget(new_board)
            # You will need to implement functionality in IdeaBoard to accept serialized data
            new_board.deserialize(board_data)  # This is a new method you'll need to implement

    # Ensure proper shutdown
    def closeEvent(self, event):
        self.backupClient.stop_microservice()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainApplication()
    mainWindow.show()
    sys.exit(app.exec_())
