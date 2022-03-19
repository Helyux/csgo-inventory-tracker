"""
TBD
"""

__author__ = "Lukas Mahler"
__version__ = "0.0.0"
__date__ = "19.03.2022"
__email__ = "m@hler.eu"
__status__ = "Development"


# Default
import sys
import time
import shutil
import os.path
import logging
from logging.handlers import RotatingFileHandler

# Custom
import toml


def getConf(fname, log):
    """

    """
    if fname.endswith(".toml"):
        if os.path.isfile(fname):
            try:
                config = toml.load(fname)
                checkConf(config)
                return config
            except ValueError as e:
                log.pipeOut(f"The provided '.toml' is probably invalid, returned error:\n{e}", lvl="critical")
        else:
            log.pipeOut(f"Couldn't locate the '.toml' file [{fname}].", lvl="error")
            log.pipeOut("Creating a new '.toml' file from template, please edit and restart.")
            shutil.copy("src/template.toml", fname)
            exit(1)
    else:
        log.pipeOut(f"The provided config file [{fname}] is not a '.toml' file.", lvl="error")
        log.pipeOut("Creating a new '.toml' file from template, please edit and restart.")
        shutil.copy("src/template.toml", "prod.toml")
        exit(1)


def checkConf(config):
    """
    TODO check if keys exist
    """
    pass


class Logger:
    """
    Create a rotating log in a log folder
    """

    def __init__(self, logpath, reprint=True, lvl="DEBUG"):

        self.reprint = reprint
        self.log = logging.getLogger("mylog")
        if not os.path.exists(logpath):
            os.makedirs(logpath)

        handler = RotatingFileHandler(os.path.join(logpath, "csgo-inventory-tracker.log"),
                                      encoding='utf-8',
                                      maxBytes=1 * 1024 * 1024,
                                      backupCount=10)
        logformat = logging.Formatter("%(asctime)s %(levelname)8s %(message)s", "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(logformat)
        self.log.addHandler(handler)
        self.log.setLevel(lvl)

    def pipeOut(self, msg, lvl="INFO"):
        """
        All output pipes through this function.
        It's possible to print the output to console [set reprint to True]
        or run in silent log mode. [set reprint to False]
        """

        lvl = lvl.upper()
        lvln = int(getattr(logging, lvl))
        self.log.log(lvln, msg)

        if self.reprint:
            print(f"[{time.strftime('%H:%M:%S')}]{f'[{lvl}]':10s} {msg}")

        if lvl == "CRITICAL":
            exit(1)

    def unhandledException(self, exc_type, exc_value, exc_traceback):
        """
        src = https://stackoverflow.com/a/16993115/5593051
        """

        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        self.log.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


if __name__ == "__main__":
    exit()
