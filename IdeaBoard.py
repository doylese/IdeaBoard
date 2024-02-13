import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTextEdit, QInputDialog, QHBoxLayout, QMenu, QAction, QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QSizePolicy)
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt

class Section(QWidget):
    def __init__(self, title):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

class IdeaBoard(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.sections = {}
        self.setupUI()

    def setupUI(self):
        self.addButton = QPushButton('Add New Idea')
        self.addButton.clicked.connect(self.addNewIdea)
        self.mainLayout.addWidget(self.addButton)

        self.addSectionButton = QPushButton('Add New Section')
        self.addSectionButton.clicked.connect(self.addNewSection)
        self.mainLayout.addWidget(self.addSectionButton)

    def addNewSection(self):
        sectionName, ok = QInputDialog.getText(self, 'New Section', 'Enter section name:')
        if ok and sectionName:
            if sectionName not in self.sections:
                section = Section(sectionName)
                self.sections[sectionName] = section
                self.mainLayout.addWidget(section)
            else:
                QMessageBox.warning(self, "Section Exists", "A section with this name already exists.")

    def addNewIdea(self):

        # Checks if there is a Section avaliable
        if not self.sections:
            self.addNewSection() # Creates new sections if none exist
            if not self.sections:
                return

        # User selects text or image to add
        ideaType, ok = QInputDialog.getItem(self, "Select Idea Type", "Choose the type of idea you want to add. This should take only a second to load: ", ["Text", "Image"], 0, False)
        if ok and ideaType:
            sectionName, ok = QInputDialog.getItem(self, "Select Section", "Choose the section:", list(self.sections.keys()), 0, False)
            if ok and sectionName:
                if ideaType == "Text":
                    self.addTextIdea(sectionName)
                elif ideaType == "Image":
                    self.addImageIdea(sectionName)
    
    def addTextIdea(self, sectionName):
        # User text input and display as a label in layout
        text, ok = QInputDialog.getText(self, 'Text', 'Enter your idea:')
        if ok and text != '':
            textWidget = QLabel(text)
            textWidget.setWordWrap(True)
            self.sections[sectionName].layout.addWidget(textWidget)
    
    def addImageIdea(self, sectionName):
        imagePath, _ = QFileDialog.getOpenFileName(self, "Select image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if imagePath:
            pixmap = QPixmap(imagePath)

        # Create a QGraphicsScene and add the pixmap
            scene = QGraphicsScene()
            pixmapItem = QGraphicsPixmapItem(pixmap)
            scene.addItem(pixmapItem)

        # Create a QGraphicsView for displaying the scene
            view = QGraphicsView(scene)
            view.setFixedSize(400, 400)  # Optional: Set an initial size for the view
            view.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)  # Allow resizing
            view.setRenderHint(QPainter.Antialiasing)  # Improve rendering quality
            view.fitInView(pixmapItem, Qt.KeepAspectRatio)  # Fit the image in the view while maintaining aspect ratio

        # Add the QGraphicsView to your layout
            self.sections[sectionName].layout.addWidget(view)

if __name__ == '__main__':
    app = QApplication(sys.argv)  # Initialize the application
    mainWin = IdeaBoard()  # Create an instance of the IdeaBoard
    mainWin.show()  # Show the main window
    sys.exit(app.exec_())  # Start the application's event loop