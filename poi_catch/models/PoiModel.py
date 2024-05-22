import asyncio
import os
import pathlib
import traceback
from typing import List, Optional, Tuple
from PySide6.QtCore import Property, QModelIndex, QObject, QPersistentModelIndex, QSettings, QThread, QUrl, Signal, QAbstractItemModel, Slot

from PySide6.QtCore import QCoreApplication
from PySide6.QtQml import QmlElement, qmlRegisterType
import aiohttp
import qasync
import qdataclass

from .ObjectItemModel import ObjectItemModel
from .poi import Poi
from utils.logger import Logger


QML_IMPORT_NAME = "poi"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0  # Optional

log = Logger(__name__)


def construct_settings_location() -> str:
    instance = QCoreApplication.instance()
    if instance is None:
        raise RuntimeError("QCoreApplication instance is not available")
    path = pathlib.Path(str(os.getenv("APPDATA"))).absolute().joinpath(
        f"{instance.organizationName().upper()[0]}{instance.organizationName()[1:]}"
    ).joinpath(
        instance.applicationName()
    ).joinpath(
        "poi_catch.ini"
    )
    return f"file:///{path.as_posix()}"

class ThreadLoop(QThread):

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        # 设置接口并发数
        self.semaphore = asyncio.Semaphore(6, loop=self.loop)


    def run(self) -> None:
        self.loop.run_forever()

    def coro_threadsafe(self, coro):
        async def _coro_with_sem(coro):
            async with self.semaphore:
                return await coro

        future =  asyncio.run_coroutine_threadsafe(_coro_with_sem(coro), self.loop)
        return asyncio.wrap_future(future)

@QmlElement
class PoiModel(ObjectItemModel, QObject):


    def __init__(self, parent=None):
        super().__init__(parent)
        self._api_name = ""
        self._city = ""
        self._keyword = ""
        self._poi_fetch_api = None

        self.thread_loop = ThreadLoop()
        self.thread_loop.start()

        self.apiNameChanged.connect(self.on_apiNameChanged)

        self._total_result:list = []
        self._total: int = 0
        self._current_page: int = 1
        self.currentPageChanged.connect(self.on_currentPageChanged)

    apiNameChanged:Signal = Signal(str)
    @Property(str, notify=apiNameChanged)
    def apiName(self):
        return self._api_name
    
    @apiName.setter # type: ignore
    def apiName(self, value):
        self._api_name = value
        self.apiNameChanged.emit(value)
    
    @Slot(str)
    def on_apiNameChanged(self, value):
        if value == "百度":
            self._poi_fetch_api = self.parse_baidu_poi
        elif value == "高德":
            self._poi_fetch_api = self.parse_gaode_poi
        elif value == "腾讯":
            self._poi_fetch_api = self.parse_tx_poi
        elif value == "360":
            self._poi_fetch_api = self.parse_360_poi
        else:
            pass

    cityChanged:Signal = Signal(str)
    @Property(str, notify=cityChanged)
    def city(self):
        return self._city
    
    @city.setter # type: ignore
    def city(self, value):
        self._city = value
        self.cityChanged.emit(value)

    keywordChanged:Signal = Signal(str)
    @Property(str, notify=keywordChanged)
    def keyword(self):
        return self._keyword
    
    @keyword.setter # type: ignore
    def keyword(self, value):
        self._keyword = value
        self.keywordChanged.emit(value)

    totalChanged:Signal = Signal(int)
    @Property(int, notify=totalChanged)
    def total(self):
        return self._total
    
    @total.setter # type: ignore
    def total(self, value):
        self._total = value
        self.totalChanged.emit(value)

    currentPageChanged:Signal = Signal(int)
    @Property(int, notify=currentPageChanged)
    def currentPage(self):
        return self._current_page
    
    @currentPage.setter # type: ignore
    def currentPage(self, value):
        self._current_page = value
        self.currentPageChanged.emit(value)

    @Slot(int)
    def on_currentPageChanged(self, value):
        try:
            self.rows = self._total_result[(value-1)*10:value*10]
        except IndexError:
            traceback.print_exc()

    @qasync.asyncSlot()
    async def fetchPoiData(self):
        try:
            total, data = await self.thread_loop.coro_threadsafe(self._poi_fetch_api(self.keyword, self.city))
            self.rows = data
            self._total_result = data
            self.total = len(self._total_result)
            tasks = []
            for i in range(1, total // 10 + 2):
                log.info(f"fetching page {i}")
                async def task(i):
                    total, data = await self.thread_loop.coro_threadsafe(self._poi_fetch_api(self.keyword, self.city, i))
                    log.info(f"page {i} fetched {len(data)} total: {total}")
                    self._total_result.extend(data)
                    self.total = len(self._total_result)
                tasks.append(task(i))
            await asyncio.gather(*tasks)
        except:
            traceback.print_exc()
        
    async def parse_baidu_poi(self, keyword, city, page = 1) -> Tuple[int, List[Poi]]:
        log.info(f"fetching poi data from {self.apiName}")
        log.info(f"city: {city}, keyword: {keyword}")
        from ws.ws import poi_search_baidu, sess_baidu
        async with sess_baidu() as sess:
            res = await poi_search_baidu(sess, keyword, city, page)
            total = res["result"]["total"]
            total = int(total)
            def content2poi(content):
                poi_list = []
                for poi_info in content:
                    poi = Poi()
                    poi.name = poi_info["name"]
                    poi.city = poi_info["city_name"]
                    poi.addr = poi_info["addr"]
                    poi.tel = poi_info.get("tel", "")
                    poi.lat = poi_info["x"]/10**7
                    poi.lng = poi_info["y"]/10**7
                    poi.category = poi_info["std_tag"]
                    poi_list.append(poi)
                return poi_list
            poi_list = []
            if "content" in res:
                poi_list = content2poi(res["content"])
            return total, poi_list

    async def parse_360_poi(self, keyword, city, page = 1) -> Tuple[int, List[Poi]]:
        """
        解析360地图POI
        :param keyword: 关键字
        :param city: 城市
        :param page: 页码
        :return: 总数和POI列表
        """
        from ws.ws import poi_search_360, sess_360
        async with sess_360() as sess:
            res = await poi_search_360(sess, keyword, city, page)
            total = res.get("totalcount", 0)
            total = int(total)
            def content2poi(content):
                poi_list = []
                for poi_info in content:
                    poi = Poi()
                    poi.name = poi_info["name"]
                    poi.city = poi_info["city"]
                    poi.addr = poi_info["address"]
                    poi.tel = poi_info.get("tel", "")
                    poi.lat = poi_info["x"]
                    poi.lng = poi_info["y"]
                    poi.category = poi_info["cat_new_name"]
                    poi_list.append(poi)
                return poi_list
            poi_list = []
            if "poi" in res:
                poi_list = content2poi(res["poi"])
            return total, poi_list
        
    async def parse_tx_poi(self, keyword, city, page=1) -> Tuple[int, List[Poi]]:
        """
        解析腾讯地图POI
        :param keyword: 关键字
        :param city: 城市
        :param page: 页码
        :return: 总数和POI列表
        """
        from ws.ws import poi_search_tx, sess_tx
        async with sess_tx() as sess:
            settings = QSettings(QUrl(construct_settings_location()).toLocalFile(), QSettings.Format.IniFormat)
            log.info(construct_settings_location())
            log.info(settings.contains("tencent/key"))
            key:str = str(settings.value("tencent/key", ""))
            sk:str = str(settings.value("tencent/sk", ""))
            log.info(f"{key}, {sk}")
            res = await poi_search_tx(sess, key, sk, keyword, city, page)
            if res["status"] != 0:
                # todo
                ...
            
            total = res.get("count", 0)
            total = int(total)
            def content2poi(content:List[dict]):
                poi_list = []
                for poi_info in content:
                    poi = Poi()
                    poi.name = poi_info["title"]
                    poi.city = poi_info["ad_info"]["city"]
                    poi.addr = poi_info["address"]
                    poi.tel = poi_info.get("tel", "")
                    poi.lat = poi_info["location"]["lat"]
                    poi.lng = poi_info["location"]["lng"]
                    poi.category = poi_info["category"]
                    poi_list.append(poi)
                return poi_list
            poi_list = []
            if "data" in res:
                poi_list = content2poi(res["data"])
            return total, poi_list