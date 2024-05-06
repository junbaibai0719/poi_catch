import QtQuick
import QtQuick.Controls

Column {
    property alias key: keyField.text
    property alias sk: skField.text

    TextField {
        id: keyField
        implicitWidth: 320
        placeholderText: qsTr("key")
    }
    TextField {
        id: skField
        implicitWidth: 320
        placeholderText: qsTr("SK")
    }
}
