"""
TBD
"""

__author__ = "Lukas Mahler"
__version__ = "0.0.0"
__date__ = "19.03.2022"
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
    log = util.Logger(logpath)

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
    print("\n<<< Exit using CTRL-C >>>\n")
    steam = util_steam.SteamInstance(config, log)
    total = steam.getInventoryValue(config['Other']['steam_id'])
    print(f"{total:.2f}")

    """
    try:
        while True:
            print("exit me kekw")
    except KeyboardInterrupt:
        pass
    """

    # Disconnect
    sql.disconnect()


if __name__ == "__main__":
    main()
