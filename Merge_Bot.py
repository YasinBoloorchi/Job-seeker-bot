import requests
import json
import re
from os import system
from bs4 import BeautifulSoup
from datetime import datetime

log_status = 'v'
TOKEN = '1921436351:AAFT9Kuz5__-58CveHM8iaIfy_05eT-7p3E'       # define the access token
URL   = 'https://api.telegram.org/bot{}/'.format(TOKEN)       # Telegram bot API url + TOKEN


def aux_dec2utf8(resp):                     # a function for decoding HTML content to utf-8 format
    decoded = ''
    for line in resp:
        decoded += line.decode('utf-8')
    return decoded


def sendMessage(chat_id, message):
    messageRes = requests.post(URL+'sendMessage?chat_id={}&text={}'.format(chat_id,message))


def save_subscriber(subscriber_file_path, sub_table):
    with open(subscriber_file_path, 'w') as subscriber_file:
        for line in sub_table:
            subscriber_file.write((line+'\n'))
        subscriber_file.close()


def load_subscriber(subscriber_file_path):
    with open(subscriber_file_path, 'r') as subscriber_file:
        sub_table = list(line.strip() for line in subscriber_file.readlines() if len(line)>0)
        subscriber_file.close()

    return sub_table


def getupd(subscriber_file_path, sub_table):
    cmd   = 'getUpdates'

    resp  = requests.get(URL + cmd)                                # reading the url
    line  = aux_dec2utf8(resp)                                     # converting the content to utf-8
    updates   = json.loads(line)

    for upd in updates['result']:
        firstname = upd['message']['from']['first_name']
        messageText = upd['message']['text']
        chatId = upd['message']['chat']['id']
        uid = upd['update_id']
        offset = '?offset={}'.format(uid + 1)

        if messageText == '/start':
            if str(chatId) not in sub_table:
                sub_table.append(str(chatId))
                save_subscriber(subscriber_file_path,sub_table)
                sendMessage(chatId, 'Bot is now activated for you. Please wait for jobs to send to you.')
            else:
                sendMessage(chatId, 'Bot is Already activated for you. Please wait for jobs to send to you.')

        elif messageText == '/stop':
            if str(chatId) in sub_table:
                sub_table.remove(str(chatId))
                save_subscriber(subscriber_file_path,sub_table)
                sendMessage(chatId, 'Bot is Deactivated for you.')
            else:
                sendMessage(chatId, 'Bot is not active for you. send /start to activation.')
                

        log(f'{firstname} send: {messageText}', 'i', log_status)

        resp = requests.get(URL + cmd + offset)

    return sub_table


def log(message, m_type, log_status):
    m_types = {'i':'[i]', 'e':'[E]', 'w':'[W]'}
    
    time = str(datetime.now()).split('.')[0] + ' '

    log_message = f'{time} {m_types[m_type]} {message}'

    with open('./log_file.txt', 'a') as log_file:
        log_file.write((log_message+'\n'))
        log_file.close()

    if log_status == 'v':
        print(log_message)


def get_last_post_id(chnl_id):
    # print(f'Getting last post id for channel: {chnl_id}' , end='\r')
    web_page = requests.get("https://t.me/s/"+chnl_id)
    souped_web_page = BeautifulSoup(web_page.text , 'html.parser')

    all_posts = souped_web_page.findAll('div' , attrs={'class' : 'tgme_widget_message js-widget_message'})

    
    if len(all_posts) > 0:
        last_post_id = all_posts[-1]['data-post'].split('/')[1]
    else:
        last_post_id = '1'
    
    return last_post_id


def read_chnl_info_file(chnl_inf_file_path):
    with open(chnl_inf_file_path, 'r') as chnl_inf:
        chnl_inf_table = list([line.split(',')[0], line.split(',')[1]] for line in chnl_inf.readlines())
        chnl_inf.close()
    
    return chnl_inf_table


def update_chnl_info_table(chnl_inf_table):
    for line in chnl_inf_table:
        chnl_id = line[0]
        chnl_last_post_id = line[1]

        chnl_last_post_id = get_last_post_id(chnl_id)
        line[1] = chnl_last_post_id
    
    return chnl_inf_table


def update_chnl_info_file(chnl_inf_file_path, chnl_inf_table):

    with open(chnl_inf_file_path, 'w') as chnl_inf:
        for line in chnl_inf_table:
            chnl_inf.write(str(line[0]+','+line[1]+'\n'))
    
        chnl_inf.close()


def check_related(chnl_id, last_post_id, key_words, key_words_file_path):
    key_words = read_keywords(key_words_file_path)
    post = requests.get("https://t.me/"+chnl_id+'/'+last_post_id)
    souped_post = BeautifulSoup(post.text , 'html.parser')

    post_text = str(souped_post.findAll('meta')[5])

    for word in key_words:
        if word in post_text:
            return True, word

    return False, ''


def read_keywords(key_words_file_path):
    with open(key_words_file_path, 'r') as key_words_file:
        key_words = [keyword.strip() for keyword in key_words_file.readlines()]
        key_words_file.close()

    return key_words


def check_new_post(chnl_id, chnl_last_post_id):
    post = requests.get("https://t.me/"+chnl_id+'/'+chnl_last_post_id)
    souped_post = BeautifulSoup(post.text , 'html.parser')
    post_text = str(souped_post.findAll('meta')[5])


    next_post_id = str(int(chnl_last_post_id)+1)
    next_post = requests.get("https://t.me/"+chnl_id+'/'+next_post_id)
    souped_next_post = BeautifulSoup(next_post.text , 'html.parser')
    next_post_text = str(souped_next_post.findAll('meta')[5])
    
    if post_text != next_post_text:
        if 'You can view and join' not in next_post_text:
            return True
        else:
            return False
    else:
        return False


def sync_chnl_inf_table(chnl_inf_table):
    for chnl in chnl_inf_table:
        chnl[1] = str(int(chnl[1])-1)
    
    return chnl_inf_table


def main():
    subscriber_file_path = './subscriber.txt'
    key_words_file_path = './keywords.txt'
    chnl_inf_file_path = './channels_info.csv'
    chnl_inf_table = []

    log('Loading initial files.', 'i', log_status)
    # initial load subscriber chatId
    sub_table = load_subscriber(subscriber_file_path)

    # initial update channels info/last post id
    chnl_inf_table = update_chnl_info_table(read_chnl_info_file(chnl_inf_file_path))

    # update channels info file
    update_chnl_info_file(chnl_inf_file_path, chnl_inf_table)

    # read the keywords
    key_words = read_keywords(key_words_file_path)
    
    # sync chnl last post minus one
    chnl_inf_table = sync_chnl_inf_table(chnl_inf_table)
    
    log('Bot Loop started', 'i', log_status)
    while True:
        sub_table = getupd(subscriber_file_path, sub_table)   

        for chnl in chnl_inf_table:
            print(f'checking channel {chnl[0]} post {chnl[1]}', end='            \r')
            if check_new_post(chnl[0], chnl[1]):
                chnl[1] = str(int(chnl[1])+1)
                update_chnl_info_file(chnl_inf_file_path, chnl_inf_table)
                
                related, key_word = check_related(chnl[0], chnl[1], key_words, key_words_file_path)
                 
                if related:
                    print()
                    for subscriber in sub_table:
                        sendMessage(subscriber, f'{key_word} \n https://t.me/{chnl[0]}/{chnl[1]}')
                        log(f'Sending Message: https://t.me/{chnl[0]}/{chnl[1]} -- To: {subscriber} for {key_word}', 'i', log_status)


if __name__ == '__main__':
    while True:
        log('Bot Started.', 'i', log_status)
        try:
            main()
        except KeyboardInterrupt:
            log('Bot Stopped with key interruption', 'i', log_status)
            exit(0)
