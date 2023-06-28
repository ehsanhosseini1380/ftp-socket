import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QMessageBox

# Global variables
connected = False

# Function to handle button clicks
def button_clicked():
    global connected
    button = engine.rootObjects()[0].findChild(QObject, sender().objectName())
    if button.objectName() == "connectButton":
        if not connected:
            # TODO: Add code to connect to the server (using the conn script)
            connected = True
            button.setProperty("text", "Disconnect")
            show_message("Connected to server.")
        else:
            # TODO: Add code to disconnect from the server
            connected = False
            button.setProperty("text", "Connect")
            show_message("Disconnected from server.")
    elif button.objectName() == "exitButton":
        if connected:
            # TODO: Add code to disconnect from the server (if connected)
            connected = False
        sys.exit()

# Function to show a message box
def show_message(message):
    msg_box = QMessageBox()
    msg_box.setText(message)
    msg_box.exec()

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)

    # Create the QML engine
    engine = QQmlApplicationEngine()

    # Connect the button_clicked function to button clicks in QML
    engine.rootContext().setContextProperty("button_clicked", button_clicked)

    # Load the main QML file
    engine.load("main.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
