"""
TBD
"""

__author__ = "Lukas Mahler"
__version__ = "0.0.0"
__date__ = "12.03.2022"
__email__ = "m@hler.eu"
__status__ = "Development"

import json
import time
import logging
import requests
import datetime
from statistics import median
from requests.utils import requote_uri


class SteamInstance:

    def __init__(self, log):

        self.currency = 3
        self.log = log
        self.bucket = 0
        self.cookies = {'steamLoginSecure': 'xxx'}

        # Stop requests libary from logging
        logging.getLogger("requests").setLevel(logging.WARNING)

    def getInventory(self, steam_id):
        """

        """

        url = f"https://steamcommunity.com/inventory/{steam_id}/730/2"
        """
        req = self.doSteamRequest(url)
        data = json.loads(req.text)
        """
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
            print(f"Bucket: {self.bucket} / Name {item['name']} / Tradeable {item['tradable']}")
            if item['tradable'] == 1:
                num_owned = cumulated[item['classid']]
                item_hash = requote_uri(item['market_hash_name'])
                price_data = self.getItemPrice(item_hash)
                price_lowest = self.sanatize(price_data['lowest_price'])
                price_median = self.sanatize(price_data['median_price'])
                price_cumulated = float(num_owned) * float(price_lowest)

                print(f"lowest: {price_lowest}€ / median: {price_median}€ / "
                      f"owned: {num_owned} / total: {str(price_cumulated)}€")

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

        if data:
            return data

    def doSteamRequest(self, url):
        """

        """

        if self.bucket == 20:
            self.cooldown()

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

    def cooldown(self):
        """

        """
        self.log.pipeOut("Bucket is full, starting cooldown", lvl='debug')
        time.sleep(60)
        self.bucket = 0

    def sanatize(self, price):
        """

        """
        price = price[:-1]  # Remove the Symbol (like $/€ etc)
        if ",--" in price:
            sanatized_price = price.replace(",--", ".00")
        else:
            sanatized_price = price.replace(",", ".")

        return sanatized_price


if __name__ == "__main__":
    exit()
