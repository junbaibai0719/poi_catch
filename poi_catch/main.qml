import QtQuick
import QtQuick.Controls
import QtQuick.Window
import Qt.labs.qmlmodels

import poi

Window {
    id: window
    width: 1024
    height: 768
    visible: true
    title: qsTr("POI抓取工具")
    Component.onCompleted: {

    }
    Row {
        id: searchInfoRow
        topPadding: 10
        TextField {
            id: cityField
            placeholderText: qsTr("城市")
            onTextEdited: {
                poiModel.city = text
            }
        }
        TextField {
            id: keywordField
            placeholderText: qsTr("关键字")
            onTextEdited: {
                poiModel.keyword = text
            }
        }
        ButtonGroup {
            id: buttonGroup
            buttons: radioRow.children
            onCheckedButtonChanged: {
                poiModel.apiName = checkedButton.text
            }
        }
        Row {
            id: radioRow
            spacing: 4
            RadioButton {
                checked: true
                text: qsTr("百度")
            }
            RadioButton {
                text: qsTr("360")
            }
            RadioButton {
                text: qsTr("高德")
            }
            RadioButton {
                text: qsTr("腾讯")
            }
        }
        Button{
            highlighted: true
            text: qsTr("开始采集")
            onClicked: poiModel.fetchPoiData()
        }
    }
    Item {
        anchors.fill: parent
        anchors.topMargin: searchInfoRow.height
        HorizontalHeaderView {
            id: header
            model: ["名称", "城市", "地址", "电话", "经度", "纬度", "分类"]
            syncView: poiTable
            clip: true
        }

        TableView {
            id: poiTable
            anchors.fill: parent
            anchors.topMargin: header.height
            anchors.bottomMargin: pagination.height
            columnSpacing: 1
            rowSpacing: 1
            boundsBehavior: Flickable.StopAtBounds
            resizableColumns: true
            clip: true
            columnWidthProvider:function(column){
                return (poiTable.width - poiTableScrollBar.width - 16) / 7
            }
            ScrollBar.vertical: ScrollBar { id: poiTableScrollBar }
            model: PoiModel {
                id: poiModel
                TableModelColumn {
                    display: "name"
                }
                TableModelColumn {
                    display: "city"
                }
                TableModelColumn {
                    display: "addr"
                }
                TableModelColumn {
                    display: "tel"
                }
                TableModelColumn {
                    display: "lat"
                }
                TableModelColumn {
                    display: "lng"
                }
                TableModelColumn {
                    display: "category"
                }
            }
            delegate: TextField {
                required property var model
                padding: 8
                wrapMode: TextInput.WrapAnywhere
                //            implicitWidth: contentWidth + Math.max((leftPadding + rightPadding), padding*2)
//                implicitWidth: TableView.view.width / 7
                text: model.display
                readOnly: true
            }
        }
        Pagination {
            id: pagination
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            total: poiModel.total
            onCurrentPageChanged: {
                poiModel.currentPage = currentPage
            }
        }
    }
}
