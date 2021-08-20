""" Prep the downloaded data


Example usage:
    ./prep_data

    {
		"Title": "All Arrests History",
		"Columns": [{
			"Id": "8955834d-4c64-4598-bb26-587745df7227",
			"Value": "MURDER 2ND: INTENTIONAL",
			"SortBy": "MURDER 2ND: INTENTIONAL",
			"CodeTemplate": "{Value}",
			"HeaderCodeTemplate": "{Value}"
		}, {
			"Id": "408b51bd-9d7f-499e-86e3-75eaf8636f33",
			"Value": "10/12/1982 12:00:00 AM",
			"SortBy": "10/12/1982 12:00:00 AM",
			"CodeTemplate": "{Value}",
			"HeaderCodeTemplate": "{Value}"
		}],
		"Interactions": [],
		"RelatedItems": []
	}, 

 epoch_time, date, day of week, holiday, arrest, officer_tax_id, officer_name, officer_type, officer_race,officer_sex,officer_appointment_year,officer_join_year, current_officer_cmd, ccrb complaints, etc.

"""

import os
import json
from tkinter.constants import NO
from savedata import save_json_to_file
import numpy as np
import datetime
import calendar
import holidays
from csv import reader
from dateutil.relativedelta import relativedelta

us_holidays = holidays.UnitedStates()
errors_summary = 0
BASE_DIRECTORY = './data-folders/'
CSV_DIRECTORY = './csv/'

DAY_IN_SECONDS = 60*60*24

FILTER_DETAILED_ARREST_HISTORY = 'filter_9'

def get_day_of_week(date):
    return calendar.day_name[date.weekday()]

#create days before and after holiday also
def get_holiday_with_epoch_date(epoch_date):
    day_before = epoch_date - DAY_IN_SECONDS
    day_after = epoch_date - DAY_IN_SECONDS
    if day_before in us_holidays:
        return us_holidays.get(day_before)
    elif epoch_date in us_holidays:
        return us_holidays.get(epoch_date)
    elif day_after in us_holidays:
        return us_holidays.get(day_after)
    return ''

def get_epoch_time(date):
    return int(date.timestamp())

def save_list_to_csv(list,file_path):
    np.savetxt(file_path, 
           list,
           delimiter =", ", 
           fmt ='% s')

def get_folders_in_path(path_to_search):
    return os.listdir(path_to_search)

def get_officer_taxid_and_name_from_folder_name(officer_folder):
    return officer_folder.split('_')

def get_list_of_arrests(office_folder):
    try:
        with open(BASE_DIRECTORY+office_folder+'/'+FILTER_DETAILED_ARREST_HISTORY, 'r') as filehandle:
            return json.load(filehandle)
    except:
        print("Couldnt get list of arrests")
        return []


def get_string_date_and_arrest_type_from_arrest(arrest):
    try:
        return arrest['Columns'][1]['Value'], arrest['Columns'][0]['Value'] 
    except:
        print("Couldnt parse arrest")
        return None,None

def get_date_object_string_date(string_date):
    return datetime.datetime.strptime(string_date, '%m/%d/%Y %I:%M:%S %p')

def re_arrange_officer_name(officer_name):
    name_split = officer_name.split(',')
    return name_split[1]+' '+name_split[0]

def return_json_from_file(filepath):
    try:
        with open(filepath, 'r') as filehandle:
                return json.load(filehandle)
    except:
        print('Cannot open file')
        return None

def increment_ccrb(ccrb_dictionary,officer_shield,board_decided_status):
    if officer_shield not in ccrb_dictionary:
        ccrb_dictionary[officer_shield] = {'substantiated':0,'unsubstantiated':0}
    ccrb_dictionary[officer_shield][board_decided_status] =  ccrb_dictionary[officer_shield][board_decided_status] +1

def get_officer_tax_id_with_first_last_name(officer_last_name_shield_dictiory,first,last):
    try:
        list_of_possibles = officer_last_name_shield_dictiory[last.upper()]
    except:
        print(" couldnt get possible list for "+last.upper())
        return None
    possible_tax_id = 0
    for possible in list_of_possibles:
        if first.upper() in possible['first']:
            if possible_tax_id != 0:
                print("found possible duplicate "+first+' '+last)
                return None
            else:
                possible_tax_id = possible['tax']

    return possible_tax_id



def build_ccrb_dictionary(officer_dictionary, officer_last_name_shield_dictiory):
    ccrb_dictionary = {}
    with open('./ccrb.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            officer_shield = row[4]
            if officer_shield == '0':
                officer_tax_id = get_officer_tax_id_with_first_last_name(officer_last_name_shield_dictiory,row[1],row[2])
                if officer_tax_id:
                    officer_shield = get_officer_shield(officer_dictionary,officer_tax_id)
            status_string = row[26]
            if 'Substantiated (' in status_string:
                increment_ccrb(ccrb_dictionary,officer_shield,'substantiated')
            else:
                increment_ccrb(ccrb_dictionary,officer_shield,'unsubstantiated')

    return ccrb_dictionary


def build_officer_dictionary():
    list_of_folders = get_folders_in_path(BASE_DIRECTORY)
    officer_dictionary = {}
    officer_last_name_shield = {}
    for officer_folder in list_of_folders:
        tax_id = officer_folder.split('_')[0]
        last_name = officer_folder.split('_')[1].split(',')[0]
        first_name = officer_folder.split('_')[1].split(',')[1]

        if last_name not in officer_last_name_shield:
            officer_last_name_shield[last_name] = []
        officer_last_name_shield[last_name].append({'first':first_name,'last':last_name,'tax':tax_id})
        
        officer_object = {}
        filter_1_data = return_json_from_file(BASE_DIRECTORY+officer_folder+'/filter_1')
        if filter_1_data:
            items = filter_1_data[0]['Items']
            for item in items:
                officer_object[item['Label']] = item['Value'].strip()
        officer_dictionary[tax_id] = officer_object
    return officer_dictionary,officer_last_name_shield


def get_officer_race(officer_dictionary,officer_tax_id):
    try:
        return officer_dictionary[officer_tax_id]['Ethnicity:']
    except:
        print('Couldnt get officer ethnicity for tax id'+officer_tax_id)
        return ''

def get_officer_shield(officer_dictionary,officer_tax_id):
    try:
        return officer_dictionary[officer_tax_id]['Shield No:']
    except:
        print('Couldnt get officer shield for tax id'+officer_tax_id)
        return '0'

def get_officer_assignment_date(officer_dictionary,officer_tax_id):
    try:
        return officer_dictionary[officer_tax_id]['Assignment Date:']
    except:
        print('Couldnt get officer assignment for tax id'+officer_tax_id)
        return ''

def get_officer_command(officer_dictionary,officer_tax_id):
    try:
        return officer_dictionary[officer_tax_id]['Command:']
    except:
        print('Couldnt get officer command for tax id'+officer_tax_id)
        return ''

def get_officer_appointment_date(officer_dictionary,officer_tax_id):
    try:
        return officer_dictionary[officer_tax_id]['Appointment Date:']
    except:
        print('Couldnt get officer appointment for tax id'+officer_tax_id)
        return ''

def get_officer_rank(officer_dictionary,officer_tax_id):
    try:
        return officer_dictionary[officer_tax_id]['Rank:']
    except:
        print('Couldnt get officer shield for Rank'+officer_tax_id)
        return ''

def get_ccrb_with_determination(ccrb_dictionary,officer_shield,determination):
    if officer_shield in ccrb_dictionary:
        return ccrb_dictionary[officer_shield][determination]
    else:
        return 0

def get_tenure(appointment_string):
    try:
        appointment_date_object = get_date_object_string_date(appointment_string)
        return relativedelta(datetime.date.today(), appointment_date_object).years
    except:
        return -1


if __name__ == '__main__':
    list_of_folders = get_folders_in_path('./data-folders/')
    i = 0
    officer_dictionary,officer_last_name_shield_dictiory = build_officer_dictionary()
    ccrb_dictionary = build_ccrb_dictionary(officer_dictionary, officer_last_name_shield_dictiory)
    for officer_folder in list_of_folders:
        print("officer "+str(i))
        i=i+1
        officer_tax_id,officer_name = get_officer_taxid_and_name_from_folder_name(officer_folder)
        officer_name_without_comma = re_arrange_officer_name(officer_name).strip()
        officer_race = get_officer_race(officer_dictionary,officer_tax_id)
        officer_shield = get_officer_shield(officer_dictionary,officer_tax_id)
        officer_assignment = get_officer_assignment_date(officer_dictionary,officer_tax_id)
        officer_command = get_officer_command(officer_dictionary,officer_tax_id)
        officer_appointment = get_officer_appointment_date(officer_dictionary,officer_tax_id)
        officer_tenure = get_tenure(officer_appointment)
        officer_rank = get_officer_rank(officer_dictionary,officer_tax_id)
        officer_substantiated_complaints = get_ccrb_with_determination(ccrb_dictionary,officer_shield,'substantiated')
        officer_unsubstantiated_complaints = get_ccrb_with_determination(ccrb_dictionary,officer_shield,'unsubstantiated')
        list_of_arrests = get_list_of_arrests(officer_folder)
        csv_arrests = []
        for arrest in list_of_arrests:
            string_date,arrest_type = get_string_date_and_arrest_type_from_arrest(arrest)
            if string_date:
                arrest_date_object = get_date_object_string_date(string_date)
                epoch_time = get_epoch_time(arrest_date_object)
                day_of_week = get_day_of_week(arrest_date_object)
                holiday = get_holiday_with_epoch_date(epoch_time)
                csv_arrests.append([epoch_time,string_date,day_of_week,holiday,arrest_type,officer_name_without_comma,officer_tax_id,officer_race,officer_appointment,officer_tenure,officer_assignment,officer_command,officer_rank,officer_shield,officer_substantiated_complaints,officer_unsubstantiated_complaints])
        save_list_to_csv(csv_arrests,BASE_DIRECTORY+officer_folder+'/summary.csv')
        save_list_to_csv(csv_arrests,CSV_DIRECTORY+'/'+officer_tax_id+'_'+'summary.csv')

