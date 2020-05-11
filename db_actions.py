import psycopg2
import configparser
from datetime import date
import logging

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

config = configparser.ConfigParser()

config.read('db.ini')

conn_string = f"host = '{config['DBConfig']['HOST']}' dbname='{config['DBConfig']['DB']}' user='{config['DBConfig']['USER']}' password='{config['DBConfig']['PASSWORD']}'"

class DBActions:

    def __init__(self):
        self.conn=psycopg2.connect(conn_string)
        self.cursor=conn.cursor()

    def _exit(self):
        self.cursor.close()
        self.conn.close()

    def _handle_error(self,error_message):
        logger.debug(f'SQL ERROR:\n{error_message}')
        self.conn.rollback()


    def add_to_tracker(self,user,ioc,ioc_type):
        self.cursor = conn.cursor()
        date = date.today()
        query=f"INSERT INTO {config['DBConfig']['TRACKER_TABLE']}(NAME, IOC_TYPE, IOC, TIME) VALUES ({user}, {ioc_type}, {ioc}, {date}"
        try:
            self.cursor.execute(query)
        except Exception as err:
            self._handle_error(err)
        self._exit()

    def get_user_iocs(self,user):
        self.cursor = conn.cursor()
        query = f"SELECT IOC_TYPE, IOC FROM {config['DBConfig']['TRACKER_TABLE']} WHERE NAME = {user}"
        try:
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            self._exit()
            return records
        except Exception as err:
            self._handle_error(err)
            self._exit()
            return 'DATABASE ERROR - IF THIS PERSISTS PLEASE CONTACT SLACKBOT SUPPORT'