#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import datetime
import psycopg2


# In[2]:


from config import ServerConfig
#from LOCAL_config import Config, LocalConfig, ProductionConfig

config = ServerConfig()


# In[3]:


class BotHandler:
    
    def __init__(self, token, update_handler):
        self.update_handler = update_handler
        self.update_processing = update_handler.handle_update
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.offset = None

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': self.offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def start(self):
        updates = self.get_updates()
        for upd in updates:
            self.update_processing(upd)
            self.offset = upd['update_id'] + 1


# In[4]:


class UpdateHandler:
    
    def initialize(self, bot, db_handler):
        self.bot = bot
        self.api_url = bot.api_url
        self.db_handler = db_handler
        
    def handle_update(self, update):
        chat_id = update['message']['chat']['id']
        chat_text = update['message']['text']
        if chat_text == 'set':
            self.process_request(update)
            return
        self.send_message(chat_id, datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S)") + '_' + chat_text)
        
    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp   
    
    def process_request(self, update):
        chat_id = update['message']['chat']['id']
        chat_text = update['message']['text']
        
        deadlines_table = self.db_handler.get_table('deadlines')
        
        expiration_time = 'now()'
        deadline = ['DEFAULT', chat_id, expiration_time, chat_text]
        
        self.db_handler.insert_row(deadlines_table, deadline)
        
        notifications_table = self.db_handler.get_table('notifications')
        ['chat_id', 't24_hours', 't6_hours', 't1_hour', 't30_mins', 't15_mins', 't5_mins', 'zero_time']
        
        timings = [True, True, True, True, True, False, False, True]
        notifications = [chat_id, *timings]
        
        self.db_handler.insert_update_row(notifications_table, notifications)


# In[5]:


class Table:
    
    def __init__(self, name, columns_names, columns_datatypes, key_column_index):
        self.name = name
        self.cols_names = columns_names
        self.cols_datatypes = columns_datatypes
        self.key_column_index = key_column_index
        
        assert(len(columns_datatypes) == len(columns_names))
        
        self.names_string = Table.array_to_string(columns_names)
        self.datatypes_string = Table.array_to_string(columns_datatypes)
        self.combined_string = Table.array_to_string(list(map(lambda x, y: x + ' ' + y, columns_names, columns_datatypes)))
        
    def array_to_string(array, add_brackets = True, add_quotation_marks = False, ignore_default = True):
        new_str = ''
        if add_quotation_marks:
            if ignore_default and 'DEFAULT' in array:
                for el in array:
                    if el == 'DEFAULT':
                        new_str += str(el) + ', '
                    else:
                        new_str += "'" + str(el) + "'" + ', '
                new_str = new_str[:-2]
            else:
                new_str =  ''.join((["'" + str(el) + "'" + ', ' for el in array]))[:-2]
        else:
            new_str = ''.join(([str(el) + ', ' for el in array]))[:-2]
            
        if add_brackets:
            new_str = "(" + new_str + ')'
            
        return new_str
        #"(" + ''.join((["'" + str(el) + "'" + ', ' for el in array]))[:-2]  + ')'
        
class DatabaseHandler:
    # ADD HERE SOME SIMPLE EXCEPTIONS HANDLING
    
    def __init__(self, dbname, username, password, hostname, tables):
        self.dbname = dbname
        self.username = username
        self.password = password
        self.hostname = hostname
        
        self.tables = tables
    
    def get_table(self, table_name, return_index = False):
        for i, table in enumerate(self.tables):
            if table.name == table_name:
                if return_index:
                    return i, table
                return table
        return None
    
    def add_table(self, table, replace_if_exists = False):
        if not isinstance(table, Table):
            print('not a table')
            assert(False)
            
        if not self.get_table(table.name) is None:
            if replace_if_exists:
                table_index = self.get_table(table.name, return_index = True)[0]
                self.tables[table_index] = table
                return
            print('table %s already exists' % table.name)
            return
        
        self.tables.append(table)
        
    def sync(self, forced_delete = False):
        conn, cur = self.connect()
                
        if forced_delete:
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'")
            for table_name in cur.fetchall():
                if self.get_table(table_name) is None:
                    cur.execute("DROP TABLE %s" % table_name)
        
        for table in self.tables:
            cur.execute("select * from information_schema.tables where table_name = '%s'" % table.name)
            
            if not cur.rowcount > 0:
                cur.execute("CREATE TABLE %s %s" % (table.name, table.combined_string))
            
        self.disconnect(conn, cur, commit = True)
        
    def connect(self):
        conn = psycopg2.connect(dbname = self.dbname, user = self.username, 
                                password = self.password, host = self.hostname)
        cur = conn.cursor()
        return conn, cur
        
    def disconnect(self, conn, cur, commit = False):
        if commit:
            conn.commit()
        cur.close()
        conn.close()
        
    def diplay_table_data(self, table):
        conn, cur = self.connect()
        cur.execute("SELECT * FROM %s" % table.name)
    
        print('Content of %s:' % table.name)
        print('--------------')
        for row in cur.fetchall():
            for col_name, el in zip(table.cols_names, row):
                print(col_name, '=', el, ' ')
            print()
        print('--------------')
        
        self.disconnect(conn, cur)
        
    def insert_row(self, table, row_vals):
        conn, cur = self.connect()
        
        row_vals_str = Table.array_to_string(row_vals, add_quotation_marks = True)
        
        cur.execute("INSERT INTO %s %s VALUES %s" % (table.name, table.names_string, row_vals_str))
        
        self.disconnect(conn, cur, commit = True)
        
    def insert_update_row(self, table, row_vals):
        conn, cur = self.connect()
        
        row_vals_str = Table.array_to_string(row_vals, add_quotation_marks = True)
        
        key_val = row_vals[table.key_column_index]
        key_val_name = table.cols_names[table.key_column_index]
        
        cur.execute("SELECT * FROM %s WHERE %s = %s" % (table.name, key_val_name, key_val))
        
        if cur.rowcount > 0:
            cur.execute("UPDATE %s SET %s = %s WHERE %s = %s" % (table.name, table.names_string, 
                                                                 row_vals_str, key_val_name, key_val));
        else:
            cur.execute("INSERT INTO %s %s VALUES %s" % (table.name, table.names_string, row_vals_str))
        
        self.disconnect(conn, cur, commit = True)
    
    def remove_row(self, e):
        pass


# In[6]:


def init_databases():
    db_handler.sync(forced_delete = True)
    
    deadlines = Table('deadlines', ['deadline_id', 'chat_id', 'expiration_time', 'description'], 
                    ['serial PRIMARY KEY', 'integer NOT NULL', 'timestamp NOT NULL', 'varchar'], 0)
    
    db_handler.add_table(deadlines, replace_if_exists = True)

    notifications = Table('notifications', 
                          ['chat_id', 't24_hours', 't12_hours', 't6_hours', 't1_hour', 't30_mins', 't15_mins', 't5_mins', 'zero_time'], 
                          ['integer NOT NULL PRIMARY KEY', 'bool', 'bool', 'bool', 'bool', 'bool', 'bool', 'bool', 'bool'], 0)
    
    db_handler.add_table(notifications, replace_if_exists = True)
    
    db_handler.sync()


# In[7]:


db_handler = DatabaseHandler(config.BD_DATABASE, config.BD_USERNAME, config.BD_PASSWORD, config.BD_HOSTNAME, [])
update_handler = UpdateHandler()
bot = BotHandler(config.TOKEN, update_handler)
update_handler.initialize(bot, db_handler)


# In[8]:


def main():  
    init_databases()
    while True:
        bot.start()


# In[9]:


if config.CONFIG_NAME == Config.SERVER_CONFIG:
    if __name__ == '__main__':  
        try:
            main()
        except KeyboardInterrupt:
            exit()
else:
    try:
        main()
    except KeyboardInterrupt:
        pass


# In[49]:





# In[ ]:




