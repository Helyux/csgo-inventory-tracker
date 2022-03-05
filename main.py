"""
TBD
"""

__author__ = "Lukas Mahler"
__version__ = "0.0.0"
__date__ = "06.03.2022"
__email__ = "m@hler.eu"
__status__ = "Development"

import os
import sys

# Self
from src import util
from src import util_sql


def main():
    # Start logger
    logpath = os.path.dirname(os.path.abspath(__file__)) + r"/log"
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
    sql.disconnect()


if __name__ == "__main__":
    main()
