"""
TBD
"""

__author__ = "Lukas Mahler"
__version__ = "0.0.0"
__date__ = "23.04.2022"
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

    # Change loglevel from config
    log.changeLevel(config['Log']['level'])

    # Create and use a new SQL Instance
    sql = util_sql.SQLinstance(config, log)
    sql.connect()
    sql.check_tables()

    # Steam
    steam = util_steam.SteamInstance(sql, config, log)

    # If we use an idfile check if we added all to our database, else add them
    if 'tracked_ids' in config:
        for tracked_id in config['tracked_ids']:
            user = sql.getUser(tracked_id)
            if not user:
                userinfo = steam.getUserInfo(tracked_id)
                log.pipeOut(f"Adding new user [{userinfo['nickname']}] to database")
                sql.addUser(userinfo)

    # Find all tracked users from db
    tracked_users = sql.getTracked()

    if not tracked_users:
        # Add the default ID from config
        userinfo = steam.getUserInfo(config['Other']['steam_id'])
        sql.addUser(userinfo)
        tracked_users = sql.getTracked()

    for tracked_user in tracked_users:

        sql_uid = tracked_user[0]
        sql_steam_id = tracked_user[1]
        sql_steam_nickname = tracked_user[2]

        log.pipeOut(f"<--- {f'Working on [{sql_steam_nickname} / {sql_steam_id}]':^80} --->")
        total = steam.getInventoryValue(sql_steam_id)
        sql.addInventory(sql_uid, total)
        log.pipeOut(f"[{tracked_user[2]} / {tracked_user[1]}] total inventory worth is: {total:.2f}{steam.symbol}")
        log.pipeOut(f"<{88*'-'}>")

    # Disconnect
    sql.disconnect()


if __name__ == "__main__":
    main()
