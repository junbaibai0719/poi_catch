import QtQuick
import QtQuick.Controls

Row {
    property int pageSize: 10
    property int currentPage: 1
    property int total: 0
    property int totalPage: Math.ceil(totalPage / pageSize)

    spacing: 8
    padding: 8

    onPageSizeChanged: {
        currentPage = 1
    }

    Text {
        id: totalPageText
        height: decreaseBtn.height
        verticalAlignment: Text.AlignVCenter
        text: qsTr("共" + total + "条；" + totalPage + "页；每页10条")
    }

    RoundButton {
        id: decreaseBtn
        text: qsTr("<")
        onClicked: currentPage--
    }

    TextField {
        height: decreaseBtn.height
        width: 100
        placeholderText: qsTr("页码")
        text: currentPage
        verticalAlignment: Text.AlignVCenter
        onTextChanged: {
            currentPage = parseInt(text)
        }
    }

    RoundButton {
        text: qsTr(">")
        onClicked: currentPage++
    }
}
