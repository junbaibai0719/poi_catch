
import pathlib
import sys

from PySide6.QtQml import QJSValue
sys.path.append(pathlib.Path(__file__).absolute().parent.parent.as_posix())

from PySide6.QtCore import QObject, Qt
from qdataclass import qdataclass

from models.ObjectItemModel import ObjectItemModel


def test_ObjectItemModel_rowCount():
    m = ObjectItemModel()
    assert m.rowCount() == 0

def test_ObjectItemModel_inherited_columnCount():
    m = ObjectItemModel()
    assert m.columnCount() == 1


def test_ObjectItemModel_inherited_generic():
    class MyObjectItemModel(ObjectItemModel[dict]):
        pass
    
    m = MyObjectItemModel()
    assert m.__special_type__ is dict

def test_ObjectItemModel_inherited_special_type():
    class MyObjectItemModel(ObjectItemModel[dict]):
        __special_type__ = list
    
    m = MyObjectItemModel()
    assert m.__special_type__ is list


def test_ObjectItemModel_data():
    class MyObjectItemModel(ObjectItemModel):
        pass
    
    m = MyObjectItemModel()
    m.rows = [{"a": 1}]
    assert m.data(m.index(0, 0), Qt.ItemDataRole.UserRole.value+1)['a'] == 1

def test_ObjectItemModel_column_data():
    class MyObjectItemModel(ObjectItemModel):
        pass
    
    m = MyObjectItemModel()
    obj = QObject()
    obj.setProperty("display", QJSValue('name'))
    m.appendColumn(obj)
    obj = QObject()
    obj.setProperty("display", QJSValue('age'))
    m.appendColumn(obj)
    m.rows = [{"name": 1, "age": 18}]
    assert m.data(m.index(0, 0), Qt.ItemDataRole.DisplayRole.value) == 1
    assert m.data(m.index(0, 1), Qt.ItemDataRole.DisplayRole.value) == 18

def test_ObjectItemModel_data_modelDataRole():
    """
    test data(index, role) with modelDataRole
    """
    @qdataclass.qDataClass
    class MyDataClass(QObject):
        name: str
        age: int
        
    class MyObjectItemModel(ObjectItemModel[MyDataClass]):
        pass
    
    m = MyObjectItemModel()
    obj = QObject()
    obj.setProperty("display", QJSValue('name'))
    m.appendColumn(obj)
    obj = QObject()
    obj.setProperty("display", QJSValue('age'))
    m.appendColumn(obj)
    mydata = MyDataClass()
    mydata.name = 1
    mydata.age = 18
    m.rows = [mydata]
    assert m.data(m.index(0, 0), Qt.ItemDataRole.UserRole.value+1) is mydata

def test_ObjectItemModel_column_data_qdataclass():
    @qdataclass.qDataClass
    class MyDataClass(QObject):
        name: str
        age: int
    
    class MyObjectItemModel(ObjectItemModel[MyDataClass]):
        pass
    
    m = MyObjectItemModel()
    obj = QObject()
    obj.setProperty("display", QJSValue('name'))
    m.appendColumn(obj)
    obj = QObject()
    obj.setProperty("display", QJSValue('age'))
    m.appendColumn(obj)
    mydata = MyDataClass()
    mydata.name = 1
    mydata.age = 18
    m.rows = [mydata]
    assert m.data(m.index(0, 0), Qt.ItemDataRole.DisplayRole.value) == 1
    assert m.data(m.index(0, 1), Qt.ItemDataRole.DisplayRole.value) == 18

def test_ObjectItemModel_modelData():
    @qdataclass.qDataClass
    class MyDataClass(QObject):
        name: str
        age: int
    
    class MyObjectItemModel(ObjectItemModel[MyDataClass]):
        pass
    
    m = MyObjectItemModel()
    obj = QObject()
    obj.setProperty("display", QJSValue('name'))
    m.appendColumn(obj)
    obj = QObject()
    obj.setProperty("display", QJSValue('age'))
    m.appendColumn(obj)
    mydata = MyDataClass()
    mydata.name = 1
    mydata.age = 18
    m.rows = [mydata]
    assert m.modelData(m.index(0, 0)).name == 1
    assert m.modelData(m.index(0, 1)).age == 18

def test_ObjectItemModel_setData():
    class MyObjectItemModel(ObjectItemModel):
        pass
    
    m = MyObjectItemModel()
    obj = QObject()
    obj.setProperty("display", QJSValue('name'))
    m.appendColumn(obj)
    obj = QObject()
    obj.setProperty("display", QJSValue('age'))
    m.appendColumn(obj)
    m.rows = [{"name": 1, "age": 18}]
    set_value = 2
    m.setData(m.index(0, 0), set_value, Qt.ItemDataRole.DisplayRole.value)
    assert m.data(m.index(0, 0), Qt.ItemDataRole.DisplayRole.value) == set_value

def test_ObjectItemModel_setData_qdataclass():
    @qdataclass.qDataClass
    class MyDataClass(QObject):
        name: str
        age: int
        
    class MyObjectItemModel(ObjectItemModel[MyDataClass]):
        pass
    
    m = MyObjectItemModel()
    obj = QObject()
    obj.setProperty("display", QJSValue('name'))
    m.appendColumn(obj)
    obj = QObject()
    obj.setProperty("display", QJSValue('age'))
    m.appendColumn(obj)
    mydata = MyDataClass()
    mydata.name = 1
    mydata.age = 18
    m.rows = [mydata]
    m.setData(m.index(0, 0), 2, Qt.ItemDataRole.DisplayRole.value)
    assert m.data(m.index(0, 0), Qt.ItemDataRole.DisplayRole.value) == 2

