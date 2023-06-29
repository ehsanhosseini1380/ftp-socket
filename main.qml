import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 400
    height: 300
    title: "My Application"
    // Set the application icon
    // You need to provide the path to your icon file
    // icon: "path/to/icon.png"

    StackView {
        id: stackView
        initialItem: loginPage

        LoginPage {
            id: loginPage
            onLoginSuccess: {
                // Navigate to the options page on successful login
                stackView.push(optionsPage)
            }
        }

        OptionsPage {
            id: optionsPage
            onDisconnect: {
                // Implement disconnect logic here
            }
        }
    }
}

Page {
    id: loginPage
    signal loginSuccess

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 10

        TextField {
            id: usernameField
            placeholderText: "Username"
        }

        TextField {
            id: passwordField
            placeholderText: "Password"
            echoMode: TextInput.Password
        }

        Button {
            text: "Login"
            onClicked: {
                // Implement authentication logic here
                var username = usernameField.text
                var password = passwordField.text

                if (username === "your_username" && password === "your_password") {
                    loginSuccess()
                } else {
                    // Failed login, show error message
                    // You can display an error message label or show a message box here
                }
            }
        }
    }
}

Page {
    id: optionsPage
    signal disconnect

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 10

        // Add your desired options widgets (e.g., list, download buttons, etc.)

        Button {
            text: "Disconnect"
            onClicked: {
                disconnect()
            }
        }
    }
}
