#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from time import sleep
import datetime
import psycopg2
from urllib.parse import urlparse 
import os

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
            
class UpdateHandler:
    
    def initialize(self, bot):
        self.bot = bot
        self.api_url = bot.api_url
        
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
        
        args_to_str = lambda args: "(" + ''.join((["'" + str(arg) + "'" + ', ' for arg in args]))[:-2]  + ')'
        
        result = urlparse(database_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        hostname = result.hostname
        
        conn = psycopg2.connect(
            database = database,
            user = username,
            password = password,
            host = hostname
        )
        cur = conn.cursor()
        
        deadlines_table = 'deadlines'
        deadlines_table_cols = '(chat_id integer NOT NULL, expiration_time timestamp NOT NULL, desciption varchar)'
        deadlines_table_cols_names = '(chat_id, expiration_time, desciption)'
        deadlines_table_cols_num = 3
        
        notifications_table = 'notifications'
        notifications_table_cols = '(chat_id integer NOT NULL PRIMARY KEY, t24_hours bool, t12_hours bool, t6_hours bool,\
        t1_hour bool, t30_mins bool, t15_mins bool, t5_mins bool, zero_time bool)'
        notifications_table_names = '(chat_id, t24_hours, t12_hours, t6_hours,\
        t1_hour, t30_mins, t15_mins, t5_mins, zero_time)'
        notifications_table_cols_num = 9

        expiration_time = 'now()'
        deadline = [chat_id, expiration_time, chat_text]

        cur.execute("INSERT INTO %s%s VALUES%s" % (deadlines_table, deadlines_table_cols_names, args_to_str(deadline)))

        timings = [True, True, True, True, True, False, False, True]
        notifications = [chat_id, *timings]
        
        cur.execute('SELECT * FROM %s where chat_id = %s' % (notifications_table, chat_id))
        does_exist = bool(cur.rowcount)

        if does_exist:
            cur.execute("UPDATE %s SET %s = %s WHERE chat_id = %s" % (notifications_table, notifications_table_names, 
                                                                      args_to_str(notifications), chat_id));
        else:
            cur.execute("INSERT INTO %s%s VALUES%s" % (notifications_table, notifications_table_names, 
                                                       args_to_str(notifications)))
        
        conn.commit()

        cur.close()
        conn.close()


# In[2]:


token = os.environ['TOKEN']
database_url = os.environ['DATABASE_URL']

# In[3]:


handler = UpdateHandler()
bot = BotHandler(token, handler)
handler.initialize(bot)

#class DatabasesHandler

def init_databases():
    result = urlparse(database_url)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname

    conn = psycopg2.connect(
        database = database,
        user = username,
        password = password,
        host = hostname
    )
    cur = conn.cursor()

    deadlines_table = 'deadlines'
    deadlines_table_cols = '(chat_id integer NOT NULL, expiration_time timestamp NOT NULL, desciption varchar)'
    deadlines_table_cols_names = '(chat_id, expiration_time, desciption)'
    deadlines_table_cols_num = 3

    cur.execute("select * from information_schema.tables where table_name = %s", (deadlines_table,))
    does_exist = bool(cur.rowcount)
    if not bool(cur.rowcount):
        cur.execute("CREATE TABLE %s %s" % (deadlines_table, deadlines_table_cols))

    notifications_table = 'notifications'
    notifications_table_cols = '(chat_id integer NOT NULL PRIMARY KEY, t24_hours bool, t12_hours bool, t6_hours bool,\
    t1_hour bool, t30_mins bool, t15_mins bool, t5_mins bool, zero_time bool)'
    notifications_table_names = '(chat_id, t24_hours, t12_hours, t6_hours,\
    t1_hour, t30_mins, t15_mins, t5_mins, zero_time)'
    notifications_table_cols_num = 9

    cur.execute("select * from information_schema.tables where table_name = %s", (notifications_table,))
    does_exist = bool(cur.rowcount)

    if not bool(cur.rowcount):
        cur.execute("CREATE TABLE %s %s" % (notifications_table, notifications_table_cols))

    conn.commit()

    cur.close()
    conn.close()
    
def main():  
    init_databases()
    while True:
        bot.start()



# In[4]:


if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()


# In[ ]:





# In[ ]:




