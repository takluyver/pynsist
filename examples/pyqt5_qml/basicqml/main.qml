import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.0

import "main.js" as App

ApplicationWindow {
    id: appWindow
    objectName: "appWindow"
    visible: true
    width: 800;
    height: 600;

    ColumnLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        anchors.margins: 3
        spacing: 3
        Column {
            Text {
                id: mainText
                objectName: "mainText"
                text: "Hello from QML"
            }
        }
        Column {
            Text {
                id: jsText
                objectName: "jsText"
            }
        }
    }
    Component.onCompleted: {
        App.onLoad();
    }
}
