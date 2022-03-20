"""
TBD
"""

__author__ = "Lukas Mahler"
__version__ = "0.0.0"
__date__ = "20.03.2022"
__email__ = "m@hler.eu"
__status__ = "Development"

# Default
from datetime import datetime

# Custom
import mysql.connector


class SQLinstance:

    def __init__(self, config, log):
        self.log = log
        self.connection = None
        self.cursor = None
        self.hostname = config['SQL']['hostname']
        self.port = config['SQL']['port']
        self.username = config['SQL']['username']
        self.password = config['SQL']['password']
        self.db = config['SQL']['db_name']
        self.default_tables = ['items', 'users', 'inventories']

        if not self.db:
            self.log.pipeOut("Please provide the name of the Database in your config.", lvl="critical")

    def check_database(self):
        #  Check if the database exists
        qtx = f"SELECT * FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{self.db}'"
        if self.connection:
            if not len(self.query(qtx.replace('DBName', self.db))) > 0:
                self.log.pipeOut(f"Database {self.db} doesn't exist.", lvl="critical")
            else:
                self.query(f"USE {self.db}")
                self.log.pipeOut(f"Database [{self.db}] is ready")

    def check_tables(self):
        # Check if the default needed tables exist
        qtx = f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{self.db}' AND TABLE_NAME = 'TBLName'"
        if self.connection:
            for table in self.default_tables:
                if not len(self.query(qtx.replace('TBLName', table))) > 0:
                    self.setup_table(table)
                else:
                    self.log.pipeOut(f"Table [{table}] is ready")

    def setup_table(self, table_name):
        self.log.pipeOut(f"Setting up new Table [{table_name}]")

        if table_name == "items":
            self.query("CREATE TABLE `items` ("
                       "`ID` INT(10) NOT NULL AUTO_INCREMENT,"
                       "`Name` VARCHAR(256) NOT NULL,"
                       "`Hash` VARCHAR(256) NOT NULL,"
                       "ClassID` VARCHAR(12) NULL DEFAULT NULL"
                       "`Lowest` DOUBLE NULL DEFAULT NULL,"
                       "`Median` DOUBLE NULL DEFAULT NULL,"
                       "`Volume` INT NULL DEFAULT NULL,"
                       "`Updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
                       "PRIMARY KEY (`ID`) USING BTREE)"
                       "COLLATE='utf8_german2_ci'"
                       "ENGINE=InnoDB;")

        if table_name == "users":
            self.query("CREATE TABLE `users` ("
                       "`ID` INT(10) NOT NULL AUTO_INCREMENT,"
                       "`SteamID` VARCHAR(50) NOT NULL,"
                       "`Nickname` VARCHAR(50) NOT NULL,"
                       "`Customurl` VARCHAR(50) NOT NULL,"
                       "`LastChecked` DATETIME NULL"
                       "`Registered` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                       "PRIMARY KEY (`ID`) USING BTREE)"
                       "COLLATE='utf8_german2_ci'"
                       "ENGINE=InnoDB;")

        if table_name == "inventories":
            self.query("CREATE TABLE `inventories` ("
                       "`ID` INT(10) NOT NULL AUTO_INCREMENT,"
                       "`UID` INT(10) NOT NULL,"
                       "`Value` INT(10) NOT NULL,"
                       "`Created` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                       "PRIMARY KEY (`ID`) USING BTREE,"
                       "INDEX `fk_inventory_UID` (`UID`) USING BTREE,"
                       "CONSTRAINT `fk_inventory_UID` FOREIGN KEY (`UID`) REFERENCES "
                       "`csgo_inventory_tracker`.`users` (`ID`) ON UPDATE NO ACTION ON DELETE NO ACTION)"
                       "COLLATE='utf8_german2_ci'"
                       "ENGINE=InnoDB;")

    def connect(self):
        try:
            self.connection = mysql.connector.connect(host=self.hostname, port=self.port,
                                                      user=self.username, password=self.password)
            self.cursor = self.connection.cursor()
            self.log.pipeOut(f"Connected to {self.hostname}")

        except mysql.connector.Error as e:
            self.log.pipeOut(e, lvl="critical")

    def disconnect(self):
        if self.connection:
            self.connection.commit()
            self.cursor.close()
            self.connection.close()
            self.cursor = None
            self.connection = None
            self.log.pipeOut(f"Disconnected from {self.hostname}")

    def query(self, qtx):
        rows = []
        if self.connection:
            self.log.pipeOut(f"SQL statement [{qtx}]", lvl="debug")
            self.cursor.execute(qtx)

            for row in self.cursor:
                # self.log.pipeOut(f"{row} / {qtx}", lvl="debug")
                rows.append(row)

        return rows

    def getLastupdated(self):
        if self.connection:
            last_updated = self.query("SELECT * FROM items ORDER BY Updated ASC LIMIT 1;")[0]
            dbid = last_updated[0]
            item_hash = last_updated[2]

            return dbid, item_hash

    def getItemDBIDfromHash(self, item_hash):
        if self.connection:
            dbid = self.query(f"SELECT ID FROM items WHERE hash = '{item_hash}';")

            if dbid:
                return dbid[0][0]
            else:
                return None

    def updateItem(self, dbid, price_data):

        # build query
        available = ""
        if price_data['lowest_price']:
            available += f"Lowest={price_data['lowest_price']}"
        if price_data['median_price']:
            available += f", Median={price_data['median_price']}"
        if price_data['volume']:
            available += f", Volume={price_data['volume']}"

        qtx = f"UPDATE items SET {available}, Updated=NOW() WHERE ID={dbid};"

        self.query(qtx)
        self.connection.commit()

    def insertItem(self, item_name, item_hash, price_data, classid=None):
        qtx = f"INSERT INTO items (Name, Hash, ClassID, Lowest, Median, Volume) " \
              f"VALUES ('{item_name}', '{item_hash}', {classid}, " \
              f"{price_data['lowest_price']}, {price_data['median_price']}, {price_data['volume']});"

        self.query(qtx)
        self.connection.commit()

    def getTracked(self):
        if self.connection:
            users = self.query("SELECT * FROM users;")

            return users

    def getUser(self, steam_id):
        if self.connection:
            users = self.query(f"SELECT * FROM users WHERE SteamID = {steam_id};")

            return users

    def addUser(self, userinfo):
        if self.connection:

            # Check that the user doesn't already exist
            if len(self.getUser(userinfo['id'])) == 0:

                qtx = f"INSERT INTO users (Nickname, SteamID, Customurl) " \
                      f"VALUES ('{userinfo['nickname']}',{userinfo['id']},'{userinfo['customurl']}');"

                self.query(qtx)
                self.connection.commit()

            else:
                self.log.pipeOut(f"User already exists in database, not adding [{userinfo['nickname']}]", lvl='warning')


if __name__ == "__main__":
    exit()
