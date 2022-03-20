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
    logname = "csgo-inventory-tracker.log"
    log = util.Logger(logpath, logname)

    # Log any unhandled exception
    sys.excepthook = log.unhandledException

    # Load toml config
    config = util.getConf("prod.toml", log)

    # Create and use a new SQL Instance
    sql = util_sql.SQLinstance(config, log)
    sql.connect()
    sql.check_tables()

    # Steam
    steam = util_steam.SteamInstance(sql, config, log)

    # Check an Inventory
    tracked_users = sql.getTracked()

    if not tracked_users:
        # Add the default ID from config
        userinfo = steam.getUserInfo(config['Other']['steam_id'])
        sql.addUser(userinfo)
        tracked_users = sql.getTracked()

    for tracked_user in tracked_users:
        print(f"<--- Working on [{tracked_user[2]} / {tracked_user[1]}] --->")
        total = steam.getInventoryValue(tracked_user[1])
        print(f"[{tracked_user[2]} / {tracked_user[1]}] total inventory worth is: {total}\n<{30*'-'}>")

    # Disconnect
    sql.disconnect()


if __name__ == "__main__":
    main()
