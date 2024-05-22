from typing import Any, Dict, Generic, List, TypeVar, Union, overload
from PySide6.QtCore import ClassInfo, Property, QByteArray, QMetaObject, QModelIndex, QObject, QPersistentModelIndex, Qt, Signal, QAbstractItemModel
from PySide6.QtQml import ListProperty, QJSValue, QmlElement, qmlRegisterType


QML_IMPORT_NAME = "qdataclass.models"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0 # Optional

T = TypeVar("T")

@QmlElement
@ClassInfo(DefaultProperty="columns") # type: ignore
class ObjectItemModel(QAbstractItemModel, Generic[T], QObject):
    """
    a model that contains a list of objects
    暂不支持多层嵌套
    todo multi-level nesting support
    """
    __special_type__:type = object

    def __new__(cls):
        if hasattr(cls, "__orig_bases__") and not cls.__special_type__:
            sub_cls = cls.__orig_bases__[0]
            if hasattr(sub_cls, "__origin__") and sub_cls.__origin__.__name__ == "ObjectItemModel":
                cls.__special_type__ = sub_cls.__args__[0]
        return super().__new__(cls)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: List[T] = []
        self._columns: list = []

    rowsChanged = Signal()
    @Property(list, notify=rowsChanged)
    def rows(self) -> List[T]:
        return self._rows
    
    @rows.setter # type: ignore
    def rows(self, rows: List[T]):
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()
        self.rowsChanged.emit()

    def appendColumn(self, column:QObject):
        column_dict:dict = {}
        for role in Qt.ItemDataRole:
            role_name = role.name[:-4]
            role_name = f'{role_name[0].lower()}{role_name[1:]}'
            v: QJSValue = column.property(role_name)
            if v:
                column_dict.update({
                    role_name: v.toString(),
                })
        self._columns.append(column_dict)

    columnsChanged = Signal()
    columns = ListProperty(QObject, appendColumn, notify=columnsChanged) # type: ignore
    

    def index(self, row: int, column: int, parent: Union[QPersistentModelIndex, QModelIndex] = QModelIndex()) -> QModelIndex:
        if row < 0 or row >= len(self._rows):
            return QModelIndex()
        if column < 0 or column >= self.columnCount(parent):
            return QModelIndex()
        return self.createIndex(row, column)
    
    @overload
    def parent(self) -> QObject:
        ...

    @overload
    def parent(self, child: Union[QModelIndex, QPersistentModelIndex]) -> QModelIndex:
        ...

    def parent(self, child: Union[QModelIndex, QPersistentModelIndex]=QModelIndex()) -> Union[QModelIndex, QObject]:
        return QModelIndex()
    
    
    def columnCount(self, parent: Union[QPersistentModelIndex, QModelIndex] = QModelIndex()) -> int:
        return max(self._columns.__len__(), 1)
    
    def roleNames(self) -> Dict[int, QByteArray]:
        role_names = super().roleNames()
        role = Qt.ItemDataRole.UserRole.value + 1
        role_names.update({
            role: QByteArray(b'modelData')
        })
        return role_names

    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = 0) -> Any:
        if not index.isValid():
            return None
        data = self._rows[index.row()]
        role_name_b = self.roleNames().get(role)
        if not role_name_b:
            return None
        role_name = role_name_b.toStdString()
        if role_name == "modelData":
            return data
        if self._columns.__len__() == 0:
            return None
        prop_name = self._columns[index.column()].get(role_name)
        if not prop_name:
            return None
        if isinstance(data, dict):
            return data.get(prop_name)
        if hasattr(data, prop_name):
            return getattr(data, prop_name)
        else:
            return None
    
    def setData(self, index: Union[QPersistentModelIndex, QModelIndex], value: Any, role: int = 0) -> bool:
        if not index.isValid():
            return False
        if role is None:
            return False
        role_name_b = self.roleNames().get(role)
        if not role_name_b:
            return False
        role_name = role_name_b.toStdString()
        if role_name == "modelData":
            self._rows[index.row()] = value
            self.dataChanged.emit(index, role)
            return True
        if self._columns.__len__() == 0:
            return False
        prop_name = self._columns[index.column()].get(role_name)
        if not prop_name:
            return False
        item = self._rows[index.row()]
        if isinstance(item, dict):
            item[prop_name] = value
            self.dataChanged.emit(index, role)
            return True
        if hasattr(self._rows[index.row()], prop_name):
            setattr(self._rows[index.row()], prop_name, value)
            self.dataChanged.emit(index, role)
            return True
        return False

    def rowCount(self, parent: Union[QPersistentModelIndex, QModelIndex] = QModelIndex()) -> int:
        return len(self._rows)
    
    def modelData(self, index: QModelIndex) -> T:
        return self._rows[index.row()]
    