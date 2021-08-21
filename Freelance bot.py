import requests
import json
import re
from os import system

TOKEN = '824647284:AAFu7yEtBCfHa7ZgU3jzD7LNhq2ARSLvDQk'       # define the access token
URL   = 'https://api.telegram.org/bot{}/'.format(TOKEN)       # Telegram bot API url + TOKEN


def aux_dec2utf8(resp):                     # a function for decoding HTML content to utf-8 format
    decoded = ''
    for line in resp:
        decoded += line.decode('utf-8')
    return decoded


def sendMessage(chat_id, message):
    messageRes = requests.post(URL+'sendMessage?chat_id={}&text={}'.format(chat_id,message))
    print(messageRes)


def save_subscriber(subscriber_file_path, sub_table):
    with open(subscriber_file_path, 'w') as subscriber_file:
        for line in sub_table:
            subscriber_file.write((line+'\n'))
        subscriber_file.close()


def load_subscriber(subscriber_file_path):
    with open(subscriber_file_path, 'r') as subscriber_file:
        sub_table = list(line for line in subscriber_file.readlines() if len(line)>0)
        subscriber_file.close()
    return sub_table


def getupd(sub_table):
    cmd   = 'getUpdates'

    resp  = requests.get(URL + cmd)                                # reading the url
    line  = aux_dec2utf8(resp)                                     # converting the content to utf-8
    updates   = json.loads(line)

    for upd in updates['result']:

        messageText = upd['message']['text']
        chatId = upd['message']['chat']['id']
        uid = upd['update_id']
        offset = '?offset={}'.format(uid + 1)

        if messageText == '/start':
            if str(chatId) not in sub_table:
                sub_table.append(str(chatId))
                save_subscriber(subscriber_file_path,sub_table)

        print(f'{firstname} said: {messageText}')

        resp = requests.get(URL + cmd + offset)

    return sub_table
    

subscriber_file_path = './subscriber.txt'
sub_table = load_subscriber(subscriber_file_path)
while True:
    sub_table = getupd(sub_table)
    
            




# ______________________________res json style__________________________
# {
# 'update_id': 39649760,
# 'message': {
#             'message_id': 52,
#             'from': {
#                      'id': 252538659,
#                      'is_bot': False,
#                      'first_name': 'Kimia',
#                      'language_code': 'fa'
#                     },
#             'chat':{
#                     'id': 252538659,
#                     'first_name': 'Kimia',
#                     'type': 'private'
#                    },
#             'date': 1566423686,
#             'text': 'Fuck?!'}
#             }
