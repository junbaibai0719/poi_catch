import asyncio
import traceback
from typing import List, Tuple
from PySide6.QtCore import Property, QModelIndex, QObject, QPersistentModelIndex, QThread, Signal, QAbstractItemModel, Slot

from PySide6.QtQml import QmlElement, qmlRegisterType
import aiohttp
import qasync
import qdataclass

from models.ObjectItemModel import ObjectItemModel
from models.poi import Poi
from utils.logger import Logger


QML_IMPORT_NAME = "poi"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0  # Optional

log = Logger(__name__)


class ThreadLoop(QThread):

    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)
        self.loop: asyncio.BaseEventLoop = asyncio.new_event_loop()
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
    
    @apiName.setter
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
    
    @city.setter
    def city(self, value):
        self._city = value
        self.cityChanged.emit(value)

    keywordChanged:Signal = Signal(str)
    @Property(str, notify=keywordChanged)
    def keyword(self):
        return self._keyword
    
    @keyword.setter
    def keyword(self, value):
        self._keyword = value
        self.keywordChanged.emit(value)

    totalChanged:Signal = Signal(int)
    @Property(int, notify=totalChanged)
    def total(self):
        return self._total
    
    @total.setter
    def total(self, value):
        self._total = value
        self.totalChanged.emit(value)

    currentPageChanged:Signal = Signal(int)
    @Property(int, notify=currentPageChanged)
    def currentPage(self):
        return self._current_page
    
    @currentPage.setter
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
        from ws.ws import poi_search_baidu
        async with aiohttp.ClientSession("https://map.baidu.com", headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
        }) as sess:
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
        from ws.ws import poi_search_360
        async with aiohttp.ClientSession("https://restapi.map.360.cn", headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
        }) as sess:
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