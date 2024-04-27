from PySide6.QtCore import Property, QObject, Signal
from PySide6.QtQml import QmlElement
import qdataclass


@qdataclass.qDataClass
class Poi(QObject):
    name: str
    city: str
    addr: str
    tel: str
    lat: float
    lng: float
    category: str
    