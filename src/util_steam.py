"""
TBD
"""

__author__ = "Lukas Mahler"
__version__ = "0.0.0"
__date__ = "17.03.2022"
__email__ = "m@hler.eu"
__status__ = "Development"

# Default
import json
import time
import logging
import datetime
from statistics import median

# Custom
import requests
from requests.utils import requote_uri


def getCurrency(config):
    """

    https://partner.steamgames.com/doc/store/pricing/currencies
    """

    currency_name = config['Other']['currency']

    with open('./src/steam_currency_values.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        if currency_name in data:
            currency_num = int(data[currency_name]['num'])
            currency_symbol = data[currency_name]['symbol']
        else:
            currency_num = 3  # Default to EUR if defined not found
            currency_symbol = "€"

    return currency_num, currency_symbol


def sanatize(price):
    """

    """
    price = price[:-1]  # Remove the currency symbol (like $/€ etc)
    if ",--" in price:
        sanatized_price = price.replace(",--", ".00")
    else:
        sanatized_price = price.replace(",", ".")

    return sanatized_price


class SteamInstance:

    def __init__(self, config, log):

        self.log = log
        self.bucket = 0
        self.currency, self.symbol = getCurrency(config)
        self.cookies = {'steamLoginSecure': 'xxx'}

        # Stop requests libary from logging
        logging.getLogger("requests").setLevel(logging.WARNING)

    def getInventory(self, steam_id):
        """

        """

        url = f"https://steamcommunity.com/inventory/{steam_id}/730/2"

        """ this is production
        req = self.doSteamRequest(url)
        data = json.loads(req.text)
        """

        """ Get json to test with once
        req = self.doSteamRequest(url)
        data = json.loads(req.text)
        with open('example_data.json', 'w') as f:
            json.dump(data, f)
        """

        # This is to test
        with open('example_data.json') as tx:
            data = json.load(tx)

        if data:
            return data
        else:
            self.log.pipeOut(f"Couldn't get Inventory for id [{steam_id}]", lvl="warning")
            return None

    def getInventoryValue(self, steam_id):
        """

        """

        total = 0.00

        data = self.getInventory(steam_id)

        if not data:
            self.log.pipeOut(f"No data for id {steam_id}", lvl="warning")
            return

        cumulated = self.getCumulated(data['assets'])

        for item in data['descriptions']:
            print(f"Bucket: {self.bucket} / Name {item['name']} / "
                  f"Tradeable {item['tradable']} / Marketable {item['marketable']}")
            if item['marketable'] == 1:
                num_owned = cumulated[item['classid']]
                item_hash = item['market_hash_name']
                price_data = self.getItemPrice(item_hash)

                if 'lowest_price' in price_data:
                    price_lowest = sanatize(price_data['lowest_price'])
                else:
                    # Price lowest is needed for calculation, atleast show error where missing
                    # Would be good to take the last entry in the db if we couldn't get a new one
                    price_lowest = None
                    self.log.pipeOut(f"No 'lowest_price' on {item['name']}, calculation might be false", lvl='error')
                    continue

                if 'median_price' in price_data:
                    price_median = sanatize(price_data['median_price'])
                else:
                    price_median = None

                if 'volume' in price_data:
                    price_volume = price_data['volume']
                else:
                    price_volume = None

                price_cumulated = float(num_owned) * float(price_lowest)

                print(f"lowest: {price_lowest} {self.symbol} / median: {price_median} {self.symbol} / "
                      f"volume: {price_volume} / owned: {num_owned} / total: {str(price_cumulated)} {self.symbol}")

                total += price_cumulated

        return total

    def getCumulated(self, data):
        """

        """

        cumulated = {}
        for item in data:
            classid = item['classid']
            if classid in cumulated.keys():
                cumulated[classid] += 1
            else:
                cumulated[classid] = 1

        self.log.pipeOut(cumulated, lvl='debug')

        return cumulated

    def getItemPriceHistory(self, item_hash):
        """
        Get the price history of an item on the scm.
        This only works with a valid steamLoginSecure cookie
        """

        url = f"https://steamcommunity.com/market/" \
              f"pricehistory/?country=DE&currency={self.currency}&appid=730&market_hash_name={item_hash}"

        req = self.doSteamRequest(url)
        data = json.loads(req.text)

        if data:

            data = data["prices"][-30:]  # From json to list /// Letzten 30 Einsträge

            prices = []
            nsold = []

            for price_point in data:
                time = datetime.datetime.strptime(price_point[0], "%b %d %Y %H: +0").strftime("%d.%m.%y - %H:%M GMT")
                prices.append(price_point[1])
                nsold.append(price_point[2])

            print(f"Median price: {median(prices)}")
            print(f"Median sold:  {median(nsold)}")

    def getItemPrice(self, item_hash):
        """
        Get the current price of an item on the scm
        This works even without a valid steamLoginSecure cookie
        """

        url = f"https://steamcommunity.com/market/" \
              f"priceoverview/?currency={self.currency}&appid=730&market_hash_name={item_hash}"

        req = self.doSteamRequest(url)
        data = json.loads(req.text)

        # Check all keys are available
        expected_keys = ['success', 'lowest_price', 'volume', 'median_price']

        # Retries
        max_retries = 3
        retries = 1

        while retries <= max_retries and not all(k in data for k in expected_keys):
            self.log.pipeOut(f"Missing keys for {item_hash}, retrying [{retries}/{max_retries}]", lvl='warning')

            req = self.doSteamRequest(url)
            data = json.loads(req.text)

            retries += 1
            time.sleep(1)

        if data:
            return data

    def doSteamRequest(self, url):
        """

        """

        if self.bucket == 20:
            self.cooldown()

        url = requote_uri(url)  # requote because item_hash often contains spaces

        self.log.pipeOut(f"Requesting [{url}]", lvl='debug')
        req = requests.get(url, cookies=self.cookies)
        self.bucket += 1

        while req.status_code != 200:

            if req.status_code == 429:
                self.log.pipeOut(f"We accidentally hit the rate limit, bucket size is {self.bucket}", lvl='warning')
                self.cooldown()
                req = requests.get(url, cookies=self.cookies)  # Retrying

            else:
                self.log.pipeOut(f"Request failed, status code is: {req.status_code}")
                return

        return req

    def cooldown(self, seconds=60):
        """

        """
        self.log.pipeOut(f"Bucket is full, starting [{seconds}] second cooldown", lvl='debug')
        time.sleep(seconds)
        self.bucket = 0


if __name__ == "__main__":
    exit()
