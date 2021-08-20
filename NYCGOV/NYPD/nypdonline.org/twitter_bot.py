from numpy.core.defchararray import array
from savedata import query_list_url_get_taxids,save_officer_detail_record_to_file_with_tax_id_and_filter_number
from prepdata import return_json_from_file,get_string_date_and_arrest_type_from_arrest,save_list_to_csv,get_date_object_string_date
import os 
import threading
import time
from csv import reader
import datetime
import argparse
from argparse import RawTextHelpFormatter
import twitter

#NYC Arrests 8/01 

#423 Arrests for XYZ
#321 Arrests for ZXY
#12 Arrests for ZYS
#2 Arrests for XYZ

CSV_FOLDER = '/tmp/nypd_data/'
CSV_FILE = CSV_FOLDER + 'yesterday.csv'
failure = 0

def save_data():
    tax_ids = query_list_url_get_taxids(1,100)
    os.makedirs(CSV_FOLDER, mode=0o777, exist_ok=True)
    for tax_id in tax_ids:
        while threading.active_count() >100:
            print("waiting")
            time.sleep(10)
        t = threading.Thread(target=save_officer_detail_record_to_file_with_tax_id_and_filter_number, args=(tax_id,9,CSV_FOLDER))
        t.start()


def parse_data_create_csv_for_yesterday(yesterday):
    global failure
    #for file in folder
    # if date is the same as yesterday, add to csv file
    csv_yesterday_arrests = []
    list_of_files = os.listdir(CSV_FOLDER)
    for officer_arrests in list_of_files:
        list_of_arrests = return_json_from_file(CSV_FOLDER+officer_arrests)
        if list_of_arrests == None:
            break
        for arrest in list_of_arrests:
            string_date,arrest_type = get_string_date_and_arrest_type_from_arrest(arrest)
            if string_date:
                string_date = string_date.split(' ')[0]
                if string_date == yesterday:
                    csv_yesterday_arrests.append([arrest_type])
            else:
                print("Couldnt get arrest "+ str(failure))
                failure += 1
    save_list_to_csv(csv_yesterday_arrests,CSV_FILE)
    
def summarize_csv_text(yesterday):

    arrest_dict = {}
    with open(CSV_FILE, 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            arrest_type = row[0].strip()
            if (arrest_type not in arrest_dict):
                arrest_dict[arrest_type] = 0
            arrest_dict[arrest_type] = arrest_dict[arrest_type]+1

    sorted_dict =  dict(sorted(arrest_dict.items(), key=lambda item: item[1], reverse=True))
    return_text = 'NYC Arrests for '+yesterday+'\n '
    #max_number = 10
    #if len(sorted_dict)<max_number:
    #    max_number = len(sorted_dict)
    list_keys = list(sorted_dict.keys())
    for i in range(0,len(sorted_dict)):
        return_text += str(sorted_dict[list_keys[i]]) +' arrests for '+ str(list_keys[i]) +' \n '
    
    return return_text


def post_text_to_twitter(text_to_post, consumer_key, consumer_secret, access_token_key,access_token_secret):
    api = twitter.Api(consumer_key,consumer_secret,access_token_key,access_token_secret,sleep_on_rate_limit=True)
    split_line = text_to_post.splitlines(True)
    post_text = ''
    twitter_posts = []
    for line in split_line:
        if len(line) + len(post_text)>160:
            twitter_posts.append(post_text)
            post_text = ''
        else:
            post_text = post_text + line
    
    
    previous_id = 0
    for post in twitter_posts:
        if previous_id != 0:
            result = api.PostUpdate(post,in_reply_to_status_id=previous_id)
        else:
            result = api.PostUpdate(post)
        previous_id = result.id

def get_yesterday_string():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=7)
    return yesterday.strftime('%-m/%-d/%Y')




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get NYPD Arrest data and post summary to twitter', formatter_class=RawTextHelpFormatter)
    parser.add_argument('-consumer_key')
    parser.add_argument('-consumer_secret')
    parser.add_argument('-access_token_key')
    parser.add_argument('-access_token_secret')
    args = parser.parse_args()
    #client = create_client(args.googleproject)

    yesterday = get_yesterday_string()
    save_data()
    parse_data_create_csv_for_yesterday(yesterday)
    text_to_post = summarize_csv_text(yesterday)
    post_text_to_twitter(text_to_post,args.consumer_key, args.consumer_secret, args.access_token_key, args.access_token_secret)


