""" Download and save officer data from NYPD Online


Example usage:
    ./savedata
"""

import requests
import os
import json
import six
import threading
import time

tax_id_dict = {}

LIST_URL = 'https://oip.nypdonline.org/api/reports/2/datasource/serverList?aggregate=&filter=&group=&page='
DETAIL_URL = 'https://oip.nypdonline.org/api/reports/'
OFFICER_URL = 'https://oip.nypdonline.org/api/reports/1/datasource/list'
SAVE_DICTIONARY = './data-folders/'
TMP_DIRECTORY = './tmp/'
SAVE_TAX_ID_LIST = 'tax_id_list'
LIST_OF_FILTERS = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,1027,1028,1029,1030,1031,1032,1033,1034,1035,1036,1037,2041,2042]

def append_to_tax_id_dict(value_to_append):
    if value_to_append in tax_id_dict:
        print(" DUPLICATE found"+str(value_to_append))
    else:
        tax_id_dict[value_to_append] = True

def make_folder(folder_path):
    os.mkdir(folder_path)

def query_list_url_get_taxids(page,pageSize):
    url = LIST_URL+str(page)+'&pageSize='+str(pageSize)
    headers = {'Content-Type': 'application/json','Cookie': 'user=Dl03--EYI2nawt3xnyi8U-zVa8MFSosL8CIh-v9M-9hDSVxFNeD4mkvoH1RVEzBIZkHau5xp57PiqDp6EHzKzHbywKfQ8PzHFAT8bhloKh0zQFqPC1OO1Uxn4QnxfX_N6wmmZbTaGkZQOFgYxcMYfBLv6ZutVAukPV6CzbxzljqdXeYYbQxpG-PXT-Wy1GITH3h1WjwR4oyg21iHzq04Nhykhbf3IkDGWXYIPgmxK8ARs0WtdoYnSOyXNIMvjT99qCKOKA83Idg1a-lLk-8HGV-p3C8ilYPVfGtkY2kJPuN9K_bNOYg7DSm0CPbRShOrg46eRvz-n5pz9oR8jtignx1c49gG4ER-OKxssLQA07_zBT5RaqYt58-r4lMe790i; BNI_persistence=fQZHNVs5szWnatWt8bmuAJzA1b_wBc4-MEyNgCTaFVZXK0PKH-jBaxkrS6oaSZ0Bz_eln6qu8a74Wj0uSvRC7g=='}
    r = requests.get(url, headers=headers)
    jsonreturn = r.json()
    total = jsonreturn['Total']
    for returned_value in jsonreturn['Data']:
        append_to_tax_id_dict(returned_value['RowValue'])

    if (page*pageSize<total):
        return query_list_url_get_taxids(page+1,pageSize)
    else:
        return list(tax_id_dict.keys())

def save_officer_record_to_file_with_tax_id_return_folder_path(tax_id):
    data = '{"filters":[{"key":"@TAXID","label":"TAXID","values":["'+str(tax_id)+'"]}]}'
    headers = {'Content-Type': 'application/json','Cookie': 'user=Dl03--EYI2nawt3xnyi8U-zVa8MFSosL8CIh-v9M-9hDSVxFNeD4mkvoH1RVEzBIZkHau5xp57PiqDp6EHzKzHbywKfQ8PzHFAT8bhloKh0zQFqPC1OO1Uxn4QnxfX_N6wmmZbTaGkZQOFgYxcMYfBLv6ZutVAukPV6CzbxzljqdXeYYbQxpG-PXT-Wy1GITH3h1WjwR4oyg21iHzq04Nhykhbf3IkDGWXYIPgmxK8ARs0WtdoYnSOyXNIMvjT99qCKOKA83Idg1a-lLk-8HGV-p3C8ilYPVfGtkY2kJPuN9K_bNOYg7DSm0CPbRShOrg46eRvz-n5pz9oR8jtignx1c49gG4ER-OKxssLQA07_zBT5RaqYt58-r4lMe790i; BNI_persistence=fQZHNVs5szWnatWt8bmuAJzA1b_wBc4-MEyNgCTaFVZXK0PKH-jBaxkrS6oaSZ0Bz_eln6qu8a74Wj0uSvRC7g=='}
    r = requests.post(OFFICER_URL,data =data, headers=headers)
    response_json = r.json()[0]
    data_save = response_json['Items']
    name = response_json['Label'].strip()
    data_save.append({'name':name})
    folder_name = tax_id+'_'+name
    make_folder(SAVE_DICTIONARY+folder_name)
    save_json_to_file(data_save,SAVE_DICTIONARY+folder_name+'/'+folder_name+'_'+'summary')
    while threading.active_count() >100:
        print("waiting")
        time.sleep(10)

    for filter_num in LIST_OF_FILTERS:
        #p1 = multiprocessing.Process(target=save_officer_detail_record_to_file_with_tax_id_and_filter_number, args=(tax_id,filter_num,folder_name))
        t = threading.Thread(target=save_officer_detail_record_to_file_with_tax_id_and_filter_number, args=(tax_id,filter_num,folder_name))
        t.start()

    #all_processes = [multiprocessing.Process(target=save_officer_detail_record_to_file_with_tax_id_and_filter_number, args=(tax_id,filter_num,folder_name)) for filter_num in LIST_OF_FILTERS]
    #for p in all_processes:
    #    p.start()

    #for p in all_processes:
    #    p.join()    
    
        #save_officer_detail_record_to_file_with_tax_id_and_filter_number(tax_id,filter_num,folder_name)

def save_officer_detail_record_to_file_with_tax_id_and_filter_number(tax_id, filter_num,folder_name):
    global error_iter
    url = DETAIL_URL+str(filter_num)+'/datasource/list'
    data = '{"filters":[{"key":"@TAXID","label":"TAXID","values":["'+str(tax_id)+'"]}]}'
    headers = {'Content-Type': 'application/json','Cookie': 'user=Dl03--EYI2nawt3xnyi8U-zVa8MFSosL8CIh-v9M-9hDSVxFNeD4mkvoH1RVEzBIZkHau5xp57PiqDp6EHzKzHbywKfQ8PzHFAT8bhloKh0zQFqPC1OO1Uxn4QnxfX_N6wmmZbTaGkZQOFgYxcMYfBLv6ZutVAukPV6CzbxzljqdXeYYbQxpG-PXT-Wy1GITH3h1WjwR4oyg21iHzq04Nhykhbf3IkDGWXYIPgmxK8ARs0WtdoYnSOyXNIMvjT99qCKOKA83Idg1a-lLk-8HGV-p3C8ilYPVfGtkY2kJPuN9K_bNOYg7DSm0CPbRShOrg46eRvz-n5pz9oR8jtignx1c49gG4ER-OKxssLQA07_zBT5RaqYt58-r4lMe790i; BNI_persistence=fQZHNVs5szWnatWt8bmuAJzA1b_wBc4-MEyNgCTaFVZXK0PKH-jBaxkrS6oaSZ0Bz_eln6qu8a74Wj0uSvRC7g=='}
    r = requests.post(url,data =data, headers=headers)
    response_json = r.json()
    if len(response_json)>0:
#        save_json_to_file(response_json,SAVE_DICTIONARY+folder_name+'/filter_'+str(filter_num))
        save_json_to_file(response_json,folder_name+tax_id+'filter_'+str(filter_num))
    else:
        print("Tax Id "+tax_id+' missing summary '+str(error_iter))
        error_iter = error_iter +1

def save_officer_info_with_list_tax_ids(tax_ids):
    i =0
    for tax_id in tax_ids:
        if i > 1950:
            try:
                folder_path = save_officer_record_to_file_with_tax_id_return_folder_path(tax_id)
                print("i "+str(i))
            except:
                print("failed i"+str(i))
        i=i+1

def save_json_to_file(json_to_save, file_path_to_save):
    with open(file_path_to_save, 'w') as filehandle:
        json.dump(json_to_save, filehandle)

def save_tax_ids_to_file():
    with open(SAVE_TAX_ID_LIST, 'w') as filehandle:
        json.dump(list(tax_id_dict.keys()), filehandle)
    
def load_tax_ids_from_file():
    with open(SAVE_TAX_ID_LIST, 'r') as filehandle:
         return json.load(filehandle)

def get_folders_in_path(path_to_search):
    return os.listdir(path_to_search)

def file_exists(file_to_check):
    return False

def temp_iterate():
    #iterate through folder
    # save filter 1
    list_of_folders = get_folders_in_path('./data-folders/')
    for officer_folder in list_of_folders:
        tax_id = officer_folder.split('_')[0]
        while threading.active_count() >100:
            print("waiting")
            time.sleep(10)
        t = threading.Thread(target=save_officer_detail_record_to_file_with_tax_id_and_filter_number, args=(tax_id,9,officer_folder))
        t.start()

if __name__ == '__main__':
    #query_list_url_get_taxids(1,100)
    #save_tax_ids_to_file()  
    tax_id_list = load_tax_ids_from_file()
    save_officer_info_with_list_tax_ids(tax_id_list)
