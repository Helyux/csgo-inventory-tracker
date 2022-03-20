"""
TBD
"""

__author__ = "Lukas Mahler"
__version__ = "0.0.0"
__date__ = "20.03.2022"
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

    with open('./src/steam_currency.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        if currency_name in data:
            currency_num = int(data[currency_name]['num'])
            currency_symbol = data[currency_name]['symbol']
        else:
            currency_num = 3  # Default to EUR if defined not found
            currency_symbol = "€"

    return currency_num, currency_symbol


def sanatize(price_data):
    """

    """

    sanatized_price_data = {}

    for key, value in price_data.items():
        if 'price' in key:
            value = value[:-1]  # Remove the currency symbol (like $/€ etc)
            if ",--" in value:
                sanatized_price = value.replace(",--", ".00")
            else:
                sanatized_price = value.replace(",", ".")

            sanatized_price_data[key] = sanatized_price
        elif 'volume' in key:
            sanatized_volume = value.replace(",", "")
            sanatized_price_data[key] = sanatized_volume
        else:
            sanatized_price_data[key] = value

    # Add missing keys
    expected_keys = ['success', 'lowest_price', 'volume', 'median_price']
    for key in expected_keys:
        if key not in sanatized_price_data:
            sanatized_price_data[key] = None

    return sanatized_price_data


class SteamInstance:

    def __init__(self, sql, config, log):

        self.log = log
        self.sql = sql

        self.bucket = 0
        self.currency, self.symbol = getCurrency(config)
        self.cookies = {'steamLoginSecure': 'xxx'}
        self.apikey = config['Auth']['apikey']

        # Stop requests libary from logging
        logging.getLogger("requests").setLevel(logging.WARNING)

    def getUserInfo(self, steam_id):
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={self.apikey}&steamids={steam_id}"
        req = self.doSteamRequest(url)
        data = json.loads(req.text)

        if data:
            player_data = data['response']['players'][0]
            nickname = player_data['personaname']
            if player_data['profilestate'] == 1:
                if player_data['communityvisibilitystate'] == 3:
                    customurl = player_data['profileurl']
                    return {'id': steam_id,
                            'nickname': nickname,
                            'customurl': customurl}
                else:
                    self.log.pipeOut(f"Won't add [{nickname}] with id [{steam_id}] to database, "
                                     f"the profile is private", lvl='warning')
                    return None
            else:
                self.log.pipeOut(f"Won't add [{nickname}] with id [{steam_id}] to database, "
                                 f"the profile is not setup", lvl='warning')
                return None

    def getInventory(self, steam_id):
        """

        """

        url = f"https://steamcommunity.com/inventory/{steam_id}/730/2"

        """
        # This is production
        req = self.doSteamRequest(url)
        data = json.loads(req.text)
        """

        """
        # Get json to test with once
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

            self.log.pipeOut(f"Bucket: {self.bucket} / Name {item['name']} / "
                             f"Tradeable {item['tradable']} / Marketable {item['marketable']}", lvl='DEBUG')

            if item['marketable'] == 1:
                num_owned = cumulated[item['classid']]
                item_hash = item['market_hash_name']
                price_data = sanatize(self.getItemPrice(item_hash))

                # Transfer price_data to database
                dbid = self.sql.getItemDBIDfromHash(item_hash)
                if dbid:
                    self.sql.updateItem(dbid, price_data)
                else:
                    self.sql.insertItem(item['name'], item_hash, price_data, classid=item['classid'])

                price_lowest = price_data['lowest_price']
                price_median = price_data['median_price']
                price_volume = price_data['volume']

                if not price_data['lowest_price']:
                    # Price lowest is needed for calculation, atleast show error where missing
                    # Would be good to take the last entry in the db if we couldn't get a new one
                    self.log.pipeOut(f"No 'lowest_price' on {item['name']}, calculation might be false", lvl='error')
                    continue

                price_cumulated = float(num_owned) * float(price_lowest)

                self.log.pipeOut(f"lowest: {price_lowest} {self.symbol} / median: {price_median} {self.symbol} / "
                                 f"volume: {price_volume} / owned: {num_owned} / "
                                 f"total: {str(price_cumulated)} {self.symbol}", lvl='DEBUG')

                total += price_cumulated

        return total

    def getCumulated(self, data):
        """

        """

        cumulated = {}
        for item in data:
            classid = item['classid']

            # TODO There is some error here, idk
            if classid == "4783280738":
                print("HALLO JAAAAA")

            if classid in cumulated.keys():
                cumulated[classid] += 1
            else:
                cumulated[classid] = 1

        self.log.pipeOut(cumulated, lvl='ERROR')

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

        # TODO
        """
        ----------------------------------------------------------------------------
        Not sure if i like the retry System.
        Most of the time the three retries don't change the returned values.
        So we get nothing for retrying other then slowing down the whole execution.
        (Bucket filling up / sleep timer in between retries)
        
        Maybe think about somethink like a reque to the end.
        ----------------------------------------------------------------------------
        """

        # Retries
        max_retries = 1
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
                self.log.pipeOut(f"We accidentally hit the rate limit, bucket size is [{self.bucket}]", lvl='warning')
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
