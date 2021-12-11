import requests
import uuid


class TargetInterface:
    def getOrders(self): pass

    def marketPrice(self): pass


class GetData:
    _baseUrl_orderBook = "https://api.kucoin.com/api/v1/market/orderbook/level2_20?symbol="
    _baseUrl_price = "https://api.kucoin.com/api/v1/market/stats?symbol="
    _orderBook_json = None
    _price_json = None

    def __init__(self, first_token: str, second_token: str):
        first_token = first_token.upper()
        second_token = second_token.upper()
        response = requests.get(self._baseUrl_orderBook + first_token + "-" + second_token)
        self._orderBook_json = response.json()
        response = requests.get(self._baseUrl_price + first_token + "-" + second_token)
        self._price_json = response.json()

    def importFromApi(self, first_token: str, second_token: str):
        first_token = first_token.upper()
        second_token = second_token.upper()
        response = requests.get(self._baseUrl_orderBook + first_token + "-" + second_token)
        self._orderBook_json = response.json()
        response = requests.get(self._baseUrl_price + first_token + "-" + second_token)
        self._price_json = response.json()

    def getJson(self, command: str):
        if command == "orderBook":
            return self._orderBook_json
        elif command == "price":
            return self._price_json


class Adaptee:
    _orderBookJSON = None
    _priceJSON = None
    _orderList = None
    _priceDict = None

    def __init__(self, data: GetData):
        self._orderBookJSON = data.getJson("orderBook")
        self._priceJSON = data.getJson("price")

    def getOrders(self):
        self._orderList = list(dict(self._orderBookJSON)['data']['bids'])
        self._orderList = list(map(lambda x: (float(x[0]), float(x[1])), self._orderList))
        del self._orderList[9:len(self._orderList) - 1]
        return self._orderList

    def marketPrice(self):
        self._priceDict = dict(self._priceJSON)['data']
        return self._priceDict


class Adapter(TargetInterface):
    _csvPath = None
    _orderBook = None
    _marketPrice = None
    _adaptee = None

    def __init__(self, adaptee: Adaptee):
        self._adaptee = adaptee

    @staticmethod
    def fileName():
        return str(uuid.uuid4()) + ".csv"

    def getOrders(self):
        self._orderBook = self._adaptee.getOrders()
        file_name = Adapter.fileName()
        with open(file_name, mode="w") as file:
            file.write("Price, Amount\n")
            for item in self._adaptee.getOrders():
                file.write(str(item[0]) + ", " + str(item[1]) + "\n")
            file.close()
        return self._orderBook

    def marketPrice(self):
        self._marketPrice = self._adaptee.marketPrice()
        keys: list = self._marketPrice.keys()
        values: list = self._marketPrice.values()
        file_name = Adapter.fileName()
        with open(file_name, mode="w") as file:
            count = 0
            for item in keys:
                file.write(item)
                if count == len(keys) - 1:
                    break
                else:
                    count += 1
                    file.write(", ")
            file.write("\n")

            count = 0
            for item in values:
                file.write(str(item))
                if count == len(values) - 1:
                    break
                else:
                    count += 1
                    file.write(", ")
            file.write("\n")
        return self._marketPrice


class Client(TargetInterface):
    _adapter = None

    def __init__(self, __adapter: Adapter):
        self._adapter = __adapter

    def getOrders(self):
        return self._adapter.getOrders()

    def marketPrice(self):
        return self._adapter.marketPrice()


date = GetData("BTC", "usdt")
adp = Adaptee(date)
adapter = Adapter(adp)
client = Client(adapter)
client.getOrders()
client.marketPrice()
