import csv
import re

street_directions = {
    109: 'W',
    108: 'E',
    107: 'W',
    105: 'W',
    104: 'E',
    103: 'W',
    102: 'E',
    101: 'W',
    100: 'E',
    99: 'W',
    98: 'E',
    97: 'W',
    95: 'W',
    94: 'E',
    93: 'W',
    92: 'E',
    91: 'W',
    90: 'E',
    89: 'W',
    88: 'E',
    87: 'W',
    85: 'W',
    84: 'E',
    83: 'W',
    82: 'E',
    80: 'E',
    78: 'E',
    77: 'W',
    76: 'E',
    75: 'W',
    74: 'E',
    73: 'W',
    71: 'W',
    70: 'E',
    69: 'W',
    68: 'E',
    67: 'W',
    66: 'W',
    65: 'E',
    64: 'E',
    63: 'W',
    62: 'W',
    61: 'E',
    60: 'W'
}

def build_street_name(row):
    return str(row[4])+'-'+row[5]+'-'+row[6]+'-'+row[7]

def save_array_as_csv(array, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in array:
            writer.writerow(row)

def sort_by_distance_to_intersection(rows_with_street_name):
    sorted_rows = sorted(rows_with_street_name, key=lambda row: int(row[13]))
    return sorted_rows

def search_whole_file_for_rows_with_street_name_return_rows(street_name, old_csv):
    data = []
    for row in old_csv:
        if street_name == build_street_name(row):
            data.append(row)
    return data

def extract_number(address):
    pattern = r"\bWEST\s+(\d+)\s+STREET\b"
    match = re.search(pattern, address)
    if match:
        return int(match.group(1))
    else:
        return None

def iterate_through_rows_add_direction(rows):
    for row in rows:
        street = row[5]
        if 'WEST' in street:
            street_string = extract_number(street)
            if street_string in street_directions:
                row.append(street_directions[street_string])
    return rows

def prepare_data():
    list_of_streets = {}
    new_rows_for_file = []

    
    with open('cb7parkingsigns.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        old_csv = []
        for row in reader:
            old_csv.append(row)
    
    for row in old_csv:
        street_name = build_street_name(row)
        if street_name not in list_of_streets and street_name != 'sos_new-on_street-from_street-to_street':
            rows_with_street_name = search_whole_file_for_rows_with_street_name_return_rows(street_name, old_csv)
            sorted_rows_with_street_name = sort_by_distance_to_intersection(rows_with_street_name)
            iterate_through_rows_add_direction(sorted_rows_with_street_name)
            for row_to_append in sorted_rows_with_street_name:
                new_rows_for_file.append(row_to_append)

        list_of_streets[street_name] = True

    save_array_as_csv(new_rows_for_file,'cb7parkingsigns_prepared.csv')

prepare_data()
