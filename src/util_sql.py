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
        self.db = config['SQL']['db_name']
        self.default_tables = ['items']

        if not self.db:
            self.log.pipeOut("Please provide the name of the Database in your config.", lvl="critical")

    def check_database(self):
        #  Check if the database exists
        qtx = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'DBName'"
        if self.connection:
            if not len(self.query(qtx.replace('DBName', self.db))) > 0:
                self.log.pipeOut(f"Database {self.db} doesn't exist.", lvl="critical")
            else:
                self.query(f"USE {self.db}")
                self.log.pipeOut(f"Database [{self.db}] is ready")

    def check_tables(self):
        # Check if the default needed tables exist
        qtx = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'TBLName'"
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
                       "`Name` VARCHAR(50) NULL DEFAULT NULL,"
                       "`Lowest` DOUBLE NULL DEFAULT NULL,"
                       "`Median` DOUBLE NULL DEFAULT NULL,"
                       "`Updated` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
                       "PRIMARY KEY (`ID`) USING BTREE)"
                       "COLLATE='utf8_german2_ci'"
                       "ENGINE=InnoDB;")

    def connect(self):
        try:
            self.connection = mysql.connector.connect(host=self.hostname, user=self.username, password=self.password)
            self.cursor = self.connection.cursor()
            self.log.pipeOut(f"Connected to {self.hostname}")
        except mysql.connector.Error as e:
            self.log.pipeOut(e, lvl="error")

    def query(self, qtx):
        rows = []
        if self.connection:
            self.cursor.execute(qtx)
            for row in self.cursor:
                self.log.pipeOut(row, lvl="debug")
                rows.append(row)

        return rows

    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            self.cursor = None
            self.connection = None
            self.log.pipeOut(f"Disconnected from {self.hostname}")


if __name__ == "__main__":
    exit()
