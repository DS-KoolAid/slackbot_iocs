import psycopg2
import configparser
from datetime import date
import logging

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

config = configparser.ConfigParser()

config.read('db.ini')

conn_string = f"host={config['DBConfig']['HOST']} dbname={config['DBConfig']['DB']} user={config['DBConfig']['USER']} password={config['DBConfig']['PASSWORD']}"

class DBActions:

    def __init__(self):
        try:
            self.conn=psycopg2.connect(conn_string)
            self.cursor=conn.cursor()
        except Exception as err:
            self._handle_error(err)

    
    def __del__(self):
        self.cursor.close()
        self.conn.close()

    # def _exit(self):
    #     self.cursor.close()
    #     self.conn.close()

    def _handle_error(self,error_message):
        logger.debug(f'SQL ERROR:\n{error_message}')
        self.conn.rollback()

    def _sanitize(s):
        s=s.trim(' ')
        s=s.trim('/**/')
        s=s.trim("'")
        s=s.trim('"')


    def add_to_tracker(self,user,ioc,ioc_type):
        table_name=config['DBConfig']['TRACKER_TABLE'].strip("'")
        ioc=self._sanitize(ioc)
        query=f"INSERT INTO {table_name}(NAME, IOC_TYPE, IOC, TIME) VALUES ('{user}', '{ioc_type}', '{ioc}', '{date.today()}')"
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as err:
            self._handle_error(err)
        # self._exit()

    def check_if_ioc_exists(self,ioc_array):
        table_name=config['DBConfig']['TRACKER_TABLE'].strip("'")
        for i in ioc_array:
            ioc=self._sanitize(i)
            query=f"SELECT IOC FROM {table_name} WHERE IOC = '{ioc}'"
            try:
                self.cursor.execute(query)
                test = self.cursor.fetchall()
                if test == '':
                    return ioc
            except Exception as err:
                self._handle_error(err)
            

    def get_user_iocs(self,user):
        table_name=config['DBConfig']['TRACKER_TABLE'].strip("'")
        query = f"SELECT IOC_TYPE, IOC, TIME FROM {table_name} WHERE NAME = '{user}'"
        try:
            self.cursor.execute(query)
            records = self.cursor.fetchall()
            rec_array=[]
            for i in records:
                rec={'IOC_type':i[0], 'IOC': i[1], 'TIME': i[2]}
                rec_array.append(rec)
            return rec_array
        except Exception as err:
            self._handle_error(err)
            # self._exit()
            return []