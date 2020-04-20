#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from time import sleep
import datetime

class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None

        return last_update


# In[2]:


token = TOKEN


# In[3]:


bot = BotHandler(token)  

def main():  
    new_offset = None

    while True:
        bot.get_updates(new_offset)

        last_update = bot.get_last_update()
        
        if last_update is None: 
            continue

        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text']
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name']
        
        bot.send_message(last_chat_id, datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S)"))
        new_offset = last_update_id + 1


# In[4]:


# if __name__ == '__main__':  
#     try:
#         main()
#     except KeyboardInterrupt:
#         exit()


# In[ ]:


try:
    main()
except KeyboardInterrupt:
    pass


# In[ ]:




