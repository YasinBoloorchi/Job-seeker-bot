import requests
from bs4 import BeautifulSoup
import re


def get_last_post_id(chnl_id):
    web_page = requests.get("https://t.me/s/"+chnl_id)
    souped_web_page = BeautifulSoup(web_page.text , 'html.parser')

    all_posts = souped_web_page.findAll('div' , attrs={'class' : 'tgme_widget_message js-widget_message'})
    last_post_id = all_posts[-1]['data-post'].split('/')[1]
    
    return last_post_id


def read_chnl_info_file(chnl_inf_file_path):
    # chnl_inf_table = []
    # read chanles info from file and put it in a list
    with open(chnl_inf_file_path, 'r') as chnl_inf:
        chnl_inf_table = list([line.split(',')[0], line.split(',')[1]] for line in chnl_inf.readlines())
        # for line in chnl_inf.readlines():
        #     chnl_inf_table.append([line.split(',')[0], line.split(',')[1]])

        chnl_inf.close()
    
    return chnl_inf_table


def update_chnl_info_table(chnl_inf_table):
    # update channels info file
    for line in chnl_inf_table:
        print(line)
        chnl_id = line[0]
        # chnl_last_post_id = line[1]

        chnl_last_post_id = get_last_post_id(chnl_id)
        line[1] = chnl_last_post_id
    
    return chnl_inf_table


def update_chnl_info_file(chnl_inf_file_path, chnl_inf_table):
    with open(chnl_inf_file_path, 'w') as chnl_inf:
        for line in chnl_inf_table:
            chnl_inf.write(str(line[0]+','+line[1]))
    
        chnl_inf.close()


def get_new_post(chnl_link, last_post_id):
    chnl_id = chnl_link.split('/')[-1]
    
    post = requests.get("https://t.me/"+chnl_id+'/'+last_post_id)
    souped_post = BeautifulSoup(post.text , 'html.parser')

    post_text = str(souped_post.findAll('meta')[5])
    print(type(post_text))
    if 'الکترونیک' in post_text:
        print('FOUND IT!')
    else:
        print('find another soloution.')


def main():
    chnl_inf_file_path = './channels_info.csv'
    url = "https://t.me/s/project_board"
    chnl_inf_table = []

    # initial update channels info/last post id
    chnl_inf_table = update_chnl_info_table(read_chnl_info_file(chnl_inf_file_path))

    # update channels info file
    update_chnl_info_file(chnl_inf_file_path, chnl_inf_table)

    # for line in chnl_inf_table:
    for line in chnl_inf_table:
        get_new_post(line[0], line[1])
        
    # Working in here
    # https://t.me/freelancer_job/78814
    # get_new_post('freelancer_job', '78814')
    


main()










# token = str(re.findall('.*name=\"(.*)\" t.*value=\"(.*)\"' , rawToken)[0][1])
# tokenName = str(re.findall('.*name=\"(.*)\" t.*value=\"(.*)\"' , rawTokenName)[0][1])
# eventVal = str(re.findall('.*name=\"(.*)\" t.*value=\"(.*)\"' , rawEventVal)[0][1])
