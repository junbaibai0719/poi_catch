# This Python file uses the following encoding: utf-8
import asyncio
import pathlib
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
import qasync

from models import PoiModel, poi

qtquickcontrols2_conf_path = pathlib.Path(__file__).absolute().parent.joinpath("qtquickcontrols2.conf")

if __name__ == "__main__":
    import os
    os.environ["QT_QUICK_CONTROLS_CONF"] = qtquickcontrols2_conf_path.as_posix()
    app = QGuiApplication(sys.argv)


    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    # QQuickStyle.setStyle("Material")
    engine = QQmlApplicationEngine()
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)
    with loop:
        loop.run_forever()