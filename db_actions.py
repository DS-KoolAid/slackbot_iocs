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


def _sanitize(s):
        s=s.trim(' ')
        s=s.trim('/**/')
        s=s.trim("'")
        s=s.trim('"')

class DBActions:

    def __init__(self):
        try:
            self.conn=psycopg2.connect(conn_string)
            self.cursor=self.conn.cursor()
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


    def add_to_tracker(self,user,ioc,ioc_type):
        table_name=config['DBConfig']['TRACKER_TABLE'].strip("'")
        query=f"INSERT INTO {table_name}(NAME, IOC_TYPE, IOC, tc_id, TIME) VALUES (%s, %s, %s, %s, '{date.today()}')"
        try:
            self.cursor.execute(query,(user,ioc_type,ioc['ioc'],ioc['id']))
            self.conn.commit()
        except Exception as err:
            self._handle_error(err)
        # self._exit()

    def check_if_ioc_exists(self,ioc):
        table_name=config['DBConfig']['TRACKER_TABLE'].strip("'")
        # ioc=_sanitize(ioc)
        query=f"SELECT count(*) FROM {table_name} WHERE tc_id = %s"
        try:
            self.cursor.execute(query,(ioc,))
            test = self.cursor.fetchone()
            if test[0] == 0:
                return False
            else:
                return True
        except Exception as err:
            self._handle_error(err)

    def check_number_of_iocs(self,user):
        table_name=config['DBConfig']['TRACKER_TABLE'].strip("'")
        query =f'select count(*) from {table_name} where name = %s'
        try:
            self.cursor.execute(query,(user,))
            count=self.cursor.fetchone()
            return count[0]
        except Exception as err:
            self._handle_error(err)
            

    def get_user_iocs(self,user):
        table_name=config['DBConfig']['TRACKER_TABLE'].strip("'")
        query = f"SELECT IOC_TYPE, IOC, tc_id, TIME FROM {table_name} WHERE NAME = %s"
        try:
            self.cursor.execute(query,(user,))
            records = self.cursor.fetchall()
            rec_array=[]
            for i in records:
                rec={'IOC_type':i[0], 'ioc': i[1], 'id':i[2], 'TIME': i[3]}
                rec_array.append(rec)
            return rec_array
        except Exception as err:
            self._handle_error(err)
            return []

    def remove_ioc(self,ioc_id):
        table_name=config['DBConfig']['TRACKER_TABLE'].strip("'")
        query = f'DELETE FROM {table_name} where tc_id = %s'
        try:
            self.cursor.execute(query,(ioc_id,))
            self.conn.commit()
            return True
        except Exception as err:
            self._handle_error(err)
            return False
            