""" 


Example usage:
    ./analyze_data
"""

from calendar import month, weekday
from operator import contains
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from csv import reader
import datetime
import time
import matplotlib.ticker as mtick
from matplotlib.ticker import PercentFormatter
from prep_data import build_officer_dictionary, get_officer_race, get_officer_rank,get_officer_appointment_date,get_tenure

TEN_YEARS_AGO_EPOCH_TIME = 1309729722

def get_list_weekdays_and_arrest(search_string):
    arrest_dict = {
        'Monday':0,
        'Tuesday':0,
        'Wednesday':0,
        'Thursday':0,
        'Friday':0,
        'Saturday':0,
        'Sunday':0
    }
    with open('./arrests_sorted.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            weekday = row[2].strip()
            arrest_type = row[4]
            if search_string == None or (search_string in arrest_type):
                arrest_dict[weekday] = arrest_dict[weekday] + 1
    return arrest_dict.keys(),arrest_dict.values()

def get_list_holidays_and_arrest():
    arrest_dict = {}
    with open('./arrests_sorted.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            holiday = row[3].strip()
            if holiday != '':
                if holiday not in arrest_dict:
                    arrest_dict[holiday] = 1
                else:
                    arrest_dict[holiday] = arrest_dict[holiday] + 1
    return arrest_dict.keys(),arrest_dict.values()

def get_list_of_months_and_arrets_last_10_years_involving_arrest_type(arrest_search_string):
    arrest_dict = {}
    with open('./arrests_sorted.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            epoch_time = int(row[0])
            arrest_string = row[4].lower()
            if epoch_time > TEN_YEARS_AGO_EPOCH_TIME and arrest_search_string.lower() in arrest_string:
                date_object = datetime.datetime.fromtimestamp(epoch_time)
                month = date_object.strftime("%m/%Y")
                if month not in arrest_dict:
                    arrest_dict[month] = 1
                else:
                    arrest_dict[month] = arrest_dict[month] + 1
    return arrest_dict.keys(),arrest_dict.values()

def get_list_months_and_arrests():
    arrest_dict = {}
    with open('./arrests_sorted.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            epoch_time = row[0]
            date_object = datetime.datetime.fromtimestamp(int(epoch_time))
            month = date_object.strftime("%m/%Y")
            if month not in arrest_dict:
                arrest_dict[month] = 1
            else:
                arrest_dict[month] = arrest_dict[month] + 1
    return arrest_dict.keys(),arrest_dict.values()

def get_epoch_time_x_seconds_ago(days_to_seconds):
    seconds = time.time()
    return seconds - days_to_seconds

def get_list_days_and_arrests_from_last_x_days(days, search_string):
    arrest_dict = {}
    with open('./arrests_sorted.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        days_to_seconds = days*24*60*60
        for row in csv_reader:
            epoch_time = int(row[0])
            arrest_string = row[4]
            if epoch_time > get_epoch_time_x_seconds_ago(days_to_seconds) and (search_string == None or (search_string in arrest_string)):
                date_object = datetime.datetime.fromtimestamp(int(epoch_time))
                day = date_object.strftime("%m/%d/%Y")
                if day not in arrest_dict:
                    arrest_dict[day] = 1
                else:
                    arrest_dict[day] = arrest_dict[day] + 1
    return arrest_dict.keys(),arrest_dict.values()

def get_list_months_and_arrests_from_last_x_months(months):
    list_of_months, list_of_arrests = get_list_months_and_arrests()
    return list(list_of_months)[-months:], list(list_of_arrests)[-months:]

def build_date_taxid_dictionary(date_string_format,restrict_date_string, restrict_year):
    time_arrests_dictionary = {}
    with open('./arrests_sorted.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            epoch_time = int(row[0])
            date_object = datetime.datetime.fromtimestamp(int(epoch_time))
            date_string = date_object.strftime(date_string_format)
            tax_id = row[6]
            dict_key = date_string+'_'+tax_id
            if (restrict_date_string == None or (restrict_date_string == date_string)) and (restrict_year == None or (restrict_year in date_string)):
                if dict_key not in time_arrests_dictionary:
                    time_arrests_dictionary[dict_key] = 0
                time_arrests_dictionary[dict_key] = time_arrests_dictionary[dict_key] +1
    return time_arrests_dictionary
            

def graph_arrests_by_month():
    list_of_months, list_of_arrests = get_list_months_and_arrests()
    plt.plot(list_of_months, list_of_arrests)
    plt.xlabel('Time')
    plt.ylabel('Arrests')
    plt.title('Arrests over time from CURRENTLY EMPLOYED NYPD Officers')
    plt.show()


def graph_arrests_last_10_years_by_month():
    list_of_months, list_of_arrests = get_list_months_and_arrests_from_last_x_months(12*10)
    fig, ax = plt.subplots()
    plt.plot(list_of_months, list_of_arrests)
    plt.xticks(rotation = 90) 
    plt.xlabel('Time')
    plt.ylabel('Arrests')
    plt.title('Last 10 years, arrests over time from CURRENTLY EMPLOYED NYPD Officers')
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    plt.show()

def graph_arrests_last_4_years_by_day():
    list_of_months, list_of_arrests = get_list_days_and_arrests_from_last_x_days(4*365)
    fig, ax = plt.subplots()
    plt.plot(list_of_months, list_of_arrests)
    plt.xticks(rotation = 90) 
    plt.xlabel('Time')
    plt.ylabel('Arrests')
    plt.title('Last 4 years, arrests over time from CURRENTLY EMPLOYED NYPD Officers')
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    plt.show()

def graph_arrests_last_4_years_by_day_for_string_in_arrest_type(search_string):
    list_of_months, list_of_arrests = get_list_days_and_arrests_from_last_x_days(4*365,search_string)
    fig, ax = plt.subplots()
    plt.plot(list_of_months, list_of_arrests)
    plt.xticks(rotation = 90) 
    plt.xlabel('Time')
    plt.ylabel('Arrests')
    plt.title('Last 4 years of arrests for '+search_string+' from CURRENTLY EMPLOYED NYPD Officers')
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    plt.show()

def graph_arrests_last_1_years_by_day():
    list_of_months, list_of_arrests = get_list_days_and_arrests_from_last_x_days(1*365)
    fig, ax = plt.subplots()
    plt.plot(list_of_months, list_of_arrests)
    plt.xticks(rotation = 90) 
    plt.xlabel('Time')
    plt.ylabel('Arrests')
    plt.title('Last 1 year, arrests over time from CURRENTLY EMPLOYED NYPD Officers')
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    plt.show()

def graph_arrests_by_day_of_week_for_string_in_arrest_type(string_search):
    list_weekdays, list_of_arrests = get_list_weekdays_and_arrest(string_search)
    fig, ax = plt.subplots()
    plt.plot(list_weekdays, list_of_arrests)
    plt.xticks(rotation = 90) 
    plt.xlabel('Days of Week')
    plt.ylabel('Arrests')
    plt.title('Arrests for '+string_search+' by Day of Week')
    plt.show()

def graph_arrests_by_day_of_week():
    list_weekdays, list_of_arrests = get_list_weekdays_and_arrest(None)
    fig, ax = plt.subplots()
    plt.plot(list_weekdays, list_of_arrests)
    plt.xticks(rotation = 90) 
    plt.xlabel('Days of Week')
    plt.ylabel('Arrests')
    plt.title('Arrests by Day of Week')
    plt.show()

def graph_arrests_by_holiday():
    list_holidays, list_of_arrests = get_list_holidays_and_arrest()
    fig, ax = plt.subplots()
    plt.plot(list_holidays, list_of_arrests)
    plt.xticks(rotation = 45) 
    plt.xlabel('holidays')
    plt.ylabel('Arrests')
    plt.title('Arrests by Holidays(+/- 1 day)')
    fig.subplots_adjust(bottom=0.2)
    plt.show()

def graph_arrests_last_10_years_by_month_for_string_in_arrest_type(arrest_search_string):
    list_of_months, list_of_arrests = get_list_of_months_and_arrets_last_10_years_involving_arrest_type(arrest_search_string)
    fig, ax = plt.subplots()
    fig.set_size_inches(2000/96,1000/96)
    plt.plot(list_of_months, list_of_arrests)
    plt.xticks(rotation = 90) 
    plt.xlabel('Time')
    plt.ylabel('Arrests')
    plt.title('Last 10 years, arrests involving '+ arrest_search_string+' from CURRENTLY EMPLOYED NYPD Officers')
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    #plt.show()
    plt.savefig('fig_arrests_'+arrest_search_string+'.png',dpi=96)

def graph_arrests_by_officer_per_day():
    # make dictionary of month_day_year_taxid -> # arrests
    day_arrests_dictionary = build_date_taxid_dictionary('%m/%d/%Y',None)
    value_dictionary = {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0}
    for number_arrests in day_arrests_dictionary.values():
        if number_arrests in value_dictionary:
            value_dictionary[number_arrests] = value_dictionary[number_arrests]+1
    y_axis = []
    sum_values = 0
    for raw_value in list(value_dictionary.values()):
        y_axis.append((raw_value))
        sum_values = sum_values+ raw_value

    for idx, raw_value in enumerate(y_axis):
       y_axis[idx] = (raw_value/sum_values)*100
    # count occurences of values
    #graph y axis # occurences and x axis arrests per day
    fig, ax = plt.subplots()
    plt.scatter(value_dictionary.keys(), y_axis)
    #ax.set_yscale('log')
    plt.xticks(rotation = 0) 
    plt.xlabel('Arrests per Day')
    plt.ylabel('% Occurences')
    plt.title('Occurences of arrests per day: 1 or greater up to 10')
    #for axis in [ax.xaxis, ax.yaxis]:
    #    formatter = ScalarFormatter()
    #    formatter.set_scientific(False)
    #    axis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(100)) 
    plt.show()
    return None

def graph_arrests_by_officer_2019():
    #ignore if apointment year is same year
    year_arrests_dictionary = build_date_taxid_dictionary('%Y','2019',None)
    year_dictionary = {}
    for number_arrests in year_arrests_dictionary.values():
        if number_arrests not in year_dictionary:
            year_dictionary[number_arrests] = 0
        year_dictionary[number_arrests] = year_dictionary[number_arrests]+1
    y_axis = []
    sum_values = 0
    for raw_value in list(year_dictionary.values()):
        y_axis.append((raw_value))
        sum_values = sum_values+ raw_value

    for idx, raw_value in enumerate(y_axis):
       y_axis[idx] = (raw_value/sum_values)*100
    # In 2019, Y axis = Number of officers who meet this, X axis # of arrests per year
    fig, ax = plt.subplots()
    plt.scatter(year_dictionary.keys(), y_axis)
    ax.set_yscale('log')
    plt.xticks(rotation = 0) 
    plt.xlabel('Arrests per Year')
    plt.ylabel('% of Officers')
    plt.title('The % of officers who made X arrests in 2019')
    #for axis in [ax.xaxis, ax.yaxis]:
    #    formatter = ScalarFormatter()
    #    formatter.set_scientific(False)
    #    axis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(100)) 
    plt.show()
    return None

def graph_how_many_days_make_greater_than_or_equal_to_1_arrest():
    officer_info_dictionary,officer_last_name_shield_dictiory = build_officer_dictionary()

    day_arrest_dictionary = build_date_taxid_dictionary('%m/%d/%Y',None, '2019')
    officer_dictionary = {}
    for day_tax in day_arrest_dictionary.keys():
        tax_id = day_tax.split('_')[1].strip()
        officer_appointment = get_officer_appointment_date(officer_info_dictionary,tax_id)
        officer_tenure = get_tenure(officer_appointment)
        if 10 < int(officer_tenure) <20 :
            if tax_id not in officer_dictionary:
                officer_dictionary[tax_id] = 0
            officer_dictionary[tax_id] = officer_dictionary[tax_id]+1
    y_axis = [0]*50
    total_num_officers_who_made_arrests = len(officer_dictionary)
    for num_yearly_arrests in list(officer_dictionary.values()):
        if num_yearly_arrests <50:
            y_axis[num_yearly_arrests] = y_axis[num_yearly_arrests]+1

    for idx, raw_value in enumerate(y_axis):
       y_axis[idx] = (raw_value/total_num_officers_who_made_arrests)*100
    # In 2019, Y axis = Number of officers who meet this, X axis # of arrests per year
    fig, ax = plt.subplots()
    plt.scatter(list(range(0,50)), y_axis)
    #ax.set_yscale('log')
    plt.xticks(rotation = 0) 
    plt.xlabel('Days that made arrests in 2019')
    plt.ylabel('% of Officers')
    plt.title('The % of officers who made made arrests on X days 2019 tenure between 10 and 20 years')
    #for axis in [ax.xaxis, ax.yaxis]:
    #    formatter = ScalarFormatter()
    #    formatter.set_scientific(False)
    #    axis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(100)) 
    plt.show()
    return None

def graph_variance_of_arrest_types():
    #iterate through all officers
    # count number of arrest types ( Dictionary key arrest type, value arrests)
    #calculate variance ( - median)sqrt
    #list of officer variances
    #count occurences of variances
    #plot

if __name__ == '__main__':
    #graph_arrests_by_month()
    #graph_arrests_last_10_years_by_month()
    #graph_arrests_last_4_years_by_day()
    #graph_arrests_last_4_years_by_day_for_string_in_arrest_type('MURDER')
    #graph_arrests_last_1_years_by_day()
    #graph_arrests_by_day_of_week()
    #graph_arrests_by_day_of_week_for_string_in_arrest_type('AGGRAVATED UNLIC OPER')
    #graph_arrests_by_holiday()
    #graph_arrests_last_10_years_by_month_for_string_in_arrest_type('FIREARM')
    #graph_arrests_by_officer_per_day() 
    #graph_arrests_by_officer_2019()
    #graph_how_many_days_make_greater_than_or_equal_to_1_arrest()
    #graph_how_many_days_make_greater_than_or_equal_to_1_arrest()
    #graph_arrests_by_officer_2019_rank()
    graph_variance_of_arrest_types()
    #graph_variance_of_arrest_types_by_rank()
    #graph_variance_of_arrest_types_by_race()
    #graph_variance_of_arrest_types_by_tenure()

