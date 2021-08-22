import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from time import sleep 

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


def check_related(chnl_id, last_post_id, key_words):
    post = requests.get("https://t.me/"+chnl_id+'/'+last_post_id)
    souped_post = BeautifulSoup(post.text , 'html.parser')

    post_text = str(souped_post.findAll('meta')[5])

    for word in key_words:
        if word in post_text:
            # print('Related!' , word ,'in:')
            # print(post_text)
            return True
    

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
    
    # Here is the bug, fix it properly next time.
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
    
    # sync chnl last post minus one
    chnl_inf_table = sync_chnl_inf_table(chnl_inf_table)

    # print(chnl_inf_table)
    

    while True:
        for chnl in chnl_inf_table:
            print(f'checking channel {chnl[0]} post: {chnl[1]}\t\t\t\t')
            if check_new_post(chnl[0], chnl[1]):
                chnl[1] = str(int(chnl[1])+1)
                update_chnl_info_file(chnl_inf_file_path, chnl_inf_table)
                
                if check_related(chnl[0], chnl[1], key_words):
                    log(f'Sending Message: https://t.me/{chnl[0]}/{chnl[1]}', 'i', log_status)


main()

# project_board,80104
# freelancer_job,79033
# job_finder2020,24171
# Daneshjoo_com,2411
# divar_daneshjoyi,20617
# Project_unii1,19532
# prozhe_pazhoh,13395
# Prozhe_Land,6810
# shoghl_yaby,8908
# best_projectt,38675
# sent_projects,19239
# iProject,12782
# Project_Daneshjoii,7810
# Team_Work_Students,3950
# Daneshjoo_com,2411
# job_freelancer,17332
# projet_channel,19105
