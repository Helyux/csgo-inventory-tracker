"""
TBD
"""

__author__ = "Lukas Mahler"
__version__ = "0.0.0"
__date__ = "26.02.2022"
__email__ = "m@hler.eu"
__status__ = "Development"


import mysql.connector


class SQLinstance:

    def __init__(self, config, log):
        self.log = log
        self.connection = None
        self.cursor = None
        self.hostname = config['SQL']['hostname']
        self.username = config['SQL']['username']
        self.password = config['SQL']['password']

        self.itemdb = config['SQL']['db_items']
        self.inventorydb = config['SQL']['db_inventory']

        if not self.itemdb and not self.inventorydb:
            self.setupdbs

    def setubdbs(self):
        self.log.pipeOut("Setting up new Databases")

    def connect(self):
        try:
            self.connection = mysql.connector.connect(host=self.hostname, user=self.username, password=self.password)
            self.cursor = self.connection.cursor()
            self.log.pipeOut(f"Connected to {self.hostname}")
        except mysql.connector.Error as e:
            self.log.pipeOut(e)

    def query(self, qtx):
        if self.connection:
            self.cursor.execute(qtx)

    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            self.cursor = None
            self.connection = None
            self.log.pipeOut(f"Disconnected from {self.hostname}")


if __name__ == "__main__":
    exit()
