"""
TBD
"""

__author__ = "Lukas Mahler"
__version__ = "0.0.0"
__date__ = "20.03.2022"
__email__ = "m@hler.eu"
__status__ = "Development"

import sys

# Self
from src import util
from src import util_sql
from src import util_steam


def main():

    # Start logger
    logpath = "./log"
    logname = "worker.log"
    log = util.Logger(logpath, logname)

    # Log any unhandled exception
    sys.excepthook = log.unhandledException

    # Load toml config
    config = util.getConf("prod.toml", log)

    # Create and use a new SQL Instance
    sql = util_sql.SQLinstance(config, log)
    sql.connect()
    sql.check_database()
    sql.check_tables()

    # Steam
    steam = util_steam.SteamInstance(sql, config, log)

    print("\n<<< Exit using CTRL-C >>>\n")
    try:
        while True:
            dbid, item_hash = sql.getLastupdated()
            print(item_hash)
            price_data = steam.getItemPrice(item_hash)
            price_data = util_steam.sanatize(price_data)  # Sanatize the Data
            sql.updateItem(dbid, price_data)

    except KeyboardInterrupt:
        pass

    # Disconnect
    sql.disconnect()


if __name__ == "__main__":
    main()
