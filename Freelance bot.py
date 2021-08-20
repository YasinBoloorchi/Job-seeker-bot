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


def getupd():
    cmd   = 'getUpdates'

    resp  = requests.get(URL + cmd)                                # reading the url
    line  = aux_dec2utf8(resp)                                     # converting the content to utf-8
    updates   = json.loads(line)
    
    for upd in updates['result']:
        
        print(upd)
        firstname = upd['message']['from']['first_name']
        messageText = upd['message']['text']
        chatId = upd['message']['chat']['id']

        uid = upd['update_id']
        offset = '?offset={}'.format(uid + 1)

        print(f'{firstname} said {messageText}')
        sendMessage(chatId, messageText)
        # system(f'espeak "{firstname} said {messageText}"')

        resp = requests.get(URL + cmd + offset)
    

while True:
    getupd()
            







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
