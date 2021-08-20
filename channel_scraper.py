import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

log_status = 'v'


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
    log(f'Getting last post id for channel: {chnl_id}', 'i', log_status)
    web_page = requests.get("https://t.me/s/"+chnl_id)
    souped_web_page = BeautifulSoup(web_page.text , 'html.parser')

    all_posts = souped_web_page.findAll('div' , attrs={'class' : 'tgme_widget_message js-widget_message'})
    last_post_id = all_posts[-1]['data-post'].split('/')[1]
    
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


def check_related(chnl_link, last_post_id, key_words):
    chnl_id = chnl_link.split('/')[-1]
    
    post = requests.get("https://t.me/"+chnl_id+'/'+last_post_id)
    souped_post = BeautifulSoup(post.text , 'html.parser')

    post_text = str(souped_post.findAll('meta')[5])

    for word in key_words:
        if word in post_text:
            print('Related')
    

def read_keywords(key_words_file_path):
    with open(key_words_file_path, 'r') as key_words_file:
        key_words = [keyword.strip() for keyword in key_words_file.readlines()]
        key_words_file.close()

    return key_words


def main():
    key_words_file_path = './keywords.txt'
    chnl_inf_file_path = './channels_info.csv'
    url = "https://t.me/s/project_board"
    chnl_inf_table = []

    # initial update channels info/last post id
    chnl_inf_table = update_chnl_info_table(read_chnl_info_file(chnl_inf_file_path))

    # update channels info file
    update_chnl_info_file(chnl_inf_file_path, chnl_inf_table)

    # read the keywords
    key_words = read_keywords(key_words_file_path)
    
    print(chnl_inf_table)
    
    # https://t.me/freelancer_job/78814
    # check_related('freelancer_job', '78814', key_words)
    


main()










# token = str(re.findall('.*name=\"(.*)\" t.*value=\"(.*)\"' , rawToken)[0][1])
# tokenName = str(re.findall('.*name=\"(.*)\" t.*value=\"(.*)\"' , rawTokenName)[0][1])
# eventVal = str(re.findall('.*name=\"(.*)\" t.*value=\"(.*)\"' , rawEventVal)[0][1])
