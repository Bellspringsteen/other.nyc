""" Download and save officer data from NYPD Online


Example usage:
    ./savedata
"""

import requests
import os
import json
import six

tax_id_dict = {}

LIST_URL = 'https://oip.nypdonline.org/api/reports/2/datasource/serverList?aggregate=&filter=&group=&page='
OFFICER_URL = 'https://oip.nypdonline.org/api/reports/1/datasource/list'
SAVE_DICTIONARY = './data/'
SAVE_TAX_ID_LIST = 'tax_id_list'

def append_to_tax_id_dict(value_to_append):
    if value_to_append in tax_id_dict:
        print(" DUPLICATE found"+str(value_to_append))
    else:
        tax_id_dict[value_to_append] = True

def query_list_url_get_taxids(page,pageSize):
    url = LIST_URL+str(page)+'&pageSize='+str(pageSize)
    headers = {'Content-Type': 'application/json','Cookie': 'user=Dl03--EYI2nawt3xnyi8U-zVa8MFSosL8CIh-v9M-9hDSVxFNeD4mkvoH1RVEzBIZkHau5xp57PiqDp6EHzKzHbywKfQ8PzHFAT8bhloKh0zQFqPC1OO1Uxn4QnxfX_N6wmmZbTaGkZQOFgYxcMYfBLv6ZutVAukPV6CzbxzljqdXeYYbQxpG-PXT-Wy1GITH3h1WjwR4oyg21iHzq04Nhykhbf3IkDGWXYIPgmxK8ARs0WtdoYnSOyXNIMvjT99qCKOKA83Idg1a-lLk-8HGV-p3C8ilYPVfGtkY2kJPuN9K_bNOYg7DSm0CPbRShOrg46eRvz-n5pz9oR8jtignx1c49gG4ER-OKxssLQA07_zBT5RaqYt58-r4lMe790i; BNI_persistence=fQZHNVs5szWnatWt8bmuAJzA1b_wBc4-MEyNgCTaFVZXK0PKH-jBaxkrS6oaSZ0Bz_eln6qu8a74Wj0uSvRC7g=='}
    r = requests.get(url, headers=headers)
    jsonreturn = r.json()
    total = jsonreturn['Total']
    for returned_value in jsonreturn['Data']:
        append_to_tax_id_dict(returned_value['RowValue'])

    if (page*pageSize<total):
        query_list_url_get_taxids(page+1,pageSize)
    else:
        print('The End')

def save_officer_record_to_file_with_tax_id(tax_id):
    data = '{"filters":[{"key":"@TAXID","label":"TAXID","values":["'+str(tax_id)+'"]}]}'
    headers = {'Content-Type': 'application/json','Cookie': 'user=Dl03--EYI2nawt3xnyi8U-zVa8MFSosL8CIh-v9M-9hDSVxFNeD4mkvoH1RVEzBIZkHau5xp57PiqDp6EHzKzHbywKfQ8PzHFAT8bhloKh0zQFqPC1OO1Uxn4QnxfX_N6wmmZbTaGkZQOFgYxcMYfBLv6ZutVAukPV6CzbxzljqdXeYYbQxpG-PXT-Wy1GITH3h1WjwR4oyg21iHzq04Nhykhbf3IkDGWXYIPgmxK8ARs0WtdoYnSOyXNIMvjT99qCKOKA83Idg1a-lLk-8HGV-p3C8ilYPVfGtkY2kJPuN9K_bNOYg7DSm0CPbRShOrg46eRvz-n5pz9oR8jtignx1c49gG4ER-OKxssLQA07_zBT5RaqYt58-r4lMe790i; BNI_persistence=fQZHNVs5szWnatWt8bmuAJzA1b_wBc4-MEyNgCTaFVZXK0PKH-jBaxkrS6oaSZ0Bz_eln6qu8a74Wj0uSvRC7g=='}
    r = requests.post(OFFICER_URL,data =data, headers=headers)
    response_json = r.json()[0]
    data_save = response_json['Items']
    name = response_json['Label'].strip()
    data_save.append({'name':name})
    save_json_to_file(data_save,SAVE_DICTIONARY+tax_id+'_'+name)

def save_officer_info_with_list_tax_ids(tax_ids):
    for tax_id in tax_ids:
        save_officer_record_to_file_with_tax_id(tax_id)

def save_json_to_file(json_to_save, file_path_to_save):
    with open(file_path_to_save, 'w') as filehandle:
        json.dump(json_to_save, filehandle)

def save_tax_ids_to_file():
    with open(SAVE_TAX_ID_LIST, 'w') as filehandle:
        json.dump(list(tax_id_dict.keys()), filehandle)
    
def load_tax_ids_from_file():
    with open(SAVE_TAX_ID_LIST, 'r') as filehandle:
         return json.load(filehandle)

if __name__ == '__main__':
    query_list_url_get_taxids(1,100)
    save_tax_ids_to_file()
    #tax_id_list = load_tax_ids_from_file()
    #save_officer_info_with_list_tax_ids(tax_id_list)

