"""
TBD
"""

__author__ = "Lukas Mahler"
__version__ = "0.0.0"
__date__ = "23.04.2022"
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

    # TODO Temporary fix, remove the success key
    sanatized_price_data.pop("success")

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

        url = f"https://steamcommunity.com/profiles/{steam_id}/inventory/json/730/2"

        # This is production
        req = self.doSteamRequest(url)
        data = json.loads(req.text)

        """
        # Get json to test with once
        req = self.doSteamRequest(url)
        data = json.loads(req.text)
        with open(f'example_data.json', 'w') as f:
            json.dump(data, f)

        # TODO DEBUG

        if 'more' in data:
            print(data['more'])
            print(data['more_start'])
        """

        """
        # This is to test
        with open('example_data.json') as tx:
            data = json.load(tx)
        """

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

        cumulated = self.getCumulated(data['rgInventory'])

        for item in data['rgDescriptions'].values():

            self.log.pipeOut(f"Bucket: {self.bucket} / Name {item['name']} / "
                             f"Tradeable {item['tradable']} / Marketable {item['marketable']}", lvl='DEBUG')

            if item['marketable'] == 1:
                num_owned = cumulated[item['classid']]
                item_hash = item['market_hash_name']

                # Only request new prices when it's a new item_hash or the data is stale
                stale = True
                sql_item = self.sql.getItemfromHash(item_hash)

                if not sql_item:
                    price_data = sanatize(self.getItemPrice(item_hash))
                else:
                    updated = sql_item[7]
                    if updated < datetime.datetime.now() - datetime.timedelta(hours=1):
                        price_data = sanatize(self.getItemPrice(item_hash))
                    else:
                        # We can use the data from the database entry
                        stale = False
                        self.log.pipeOut(f"Using cached non stale database values for [{item_hash}]", lvl='DEBUG')
                        price_data = {'lowest_price': sql_item[4],
                                      'median_price': sql_item[5],
                                      'volume': sql_item[6]}

                price_lowest = price_data['lowest_price']
                price_median = price_data['median_price']
                price_volume = price_data['volume']

                if price_lowest:

                    calculation_price = price_lowest

                    # Transfer price_data to database
                    if stale:
                        if sql_item:
                            self.sql.updateItem(sql_item[0], price_data, classid=item['classid'])
                        else:
                            self.sql.insertItem(item['name'], item_hash, price_data, classid=item['classid'])

                else:
                    # Don't transfer into sql since no price_lowest!
                    # Price lowest is needed, show an error when it's missing
                    # We can calculate with an old Value

                    self.log.pipeOut(f"No 'lowest_price' on {item['name']}, "
                                     f"calculation might be inadequate since we use other (stale) values", lvl='error')

                    # Do we have the median?
                    if price_median:
                        calculation_price = price_median
                    else:
                        # Do we have an old value?
                        if sql_item:
                            calculation_price = sql_item[4]
                        else:
                            # We are fucked, just use 0.
                            calculation_price = 0

                price_cumulated = float(num_owned) * float(calculation_price)

                self.log.pipeOut(f"lowest: {price_lowest} {self.symbol} / median: {price_median} {self.symbol} / "
                                 f"volume: {price_volume} / owned: {num_owned} / "
                                 f"total: {str(price_cumulated)} {self.symbol}", lvl='DEBUG')

                total += price_cumulated

        return total

    @staticmethod
    def getCumulated(data):
        """

        """

        cumulated = {}
        for item in data.values():

            classid = item['classid']

            if classid in cumulated.keys():
                cumulated[classid] += 1
            else:
                cumulated[classid] = 1

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
                xtime = datetime.datetime.strptime(price_point[0], "%b %d %Y %H: +0").strftime("%d.%m.%y - %H:%M GMT")
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

    def doSteamRequest(self, url, proxy=None):
        """

        """

        if self.bucket == 20:
            self.cooldown()

        url = requote_uri(url)  # requote because item_hash often contains spaces

        self.log.pipeOut(f"Requesting [{url}] | Proxy = {proxy['https'] if proxy else None}", lvl='debug')
        req = requests.get(url, cookies=self.cookies, proxies=proxy, timeout=10)
        self.bucket += 1

        while req.status_code != 200:

            if req.status_code == 429:
                # TODO Implement a proxy cycle sytem if we hit the rate limit
                self.log.pipeOut(f"We accidentally hit the rate limit, bucket size is [{self.bucket}]", lvl='warning')
                self.cooldown()
                req = requests.get(url, cookies=self.cookies, proxies=proxy, timeout=10)  # Retrying

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
