import json
import requests
from shapely.geometry import shape, Point
import random
from math import radians, cos, sin, asin, sqrt
import os

THREE_MILES_IN_KM = 4.8
GET_SHORT_POINTS = False # set to TRUE to get points within Three Miles
ONLY_FROM_BOROUGH = None
NUMBER_OF_REQUESTS_TO_SAVE = 10

GOOGLE_TOKEN = os.environ.get('GOOGLE_TOKEN')
REQUESTS_FOLDER = '/home/regolith/Development/other.nyc/bus-redraw/requests/'

def haversine(lon1, lat1, lon2, lat2):
    """
    Copied from Stack Overflow 
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km


class LocationObject:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def string(self):
        return str(self.lat)+','+str(self.lng)

class RouteObject:
    def __init__(self, route_index, transit_time):
        self.route_index = route_index
        self.transit_time = transit_time

def get_random_point_in_nyc(point_dist_from: LocationObject):
    bottom_left_bounding = LocationObject(40.49759385335395, -74.28244329528017)
    upper_right_bouding = LocationObject(40.883984450803695, -73.73691003788345)
    while True:
        random_point = LocationObject(random.uniform(bottom_left_bounding.lat, upper_right_bouding.lat), random.uniform(upper_right_bouding.lng, bottom_left_bounding.lng))
        pnt = Point(random_point.lat,random_point.lng)
        result =  get_borough_in_nyc_for_point(random_point)
        if point_dist_from:
            distance = haversine(random_point.lng,random_point.lat,point_dist_from.lng,point_dist_from.lat)
            if distance< THREE_MILES_IN_KM and distance > 1 and result:
                return random_point
        else:
            if result:
                return random_point

def get_borough_in_nyc_for_point(location: LocationObject):
    # load GeoJSON file containing sectors
    with open('nyc.json') as f:
        js = json.load(f)

    # construct point based on lon/lat returned by geocoder
    point = Point(location.lng,location.lat)

    # check each polygon to see if it contains the point
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if ONLY_FROM_BOROUGH:
            if polygon.contains(point) and feature['properties']['borough']==ONLY_FROM_BOROUGH:
                return (feature['properties']['borough'])
        else:
            if polygon.contains(point) and feature['properties']['borough']!='Staten Island':
                return (feature['properties']['borough'])

    return False

# Note, if you are running and not getting back directions, change the departure_time to a time in the future. 
def get_google_directions_between_points(location1: LocationObject ,location2: LocationObject):
    r = requests.get('https://maps.googleapis.com/maps/api/directions/json?origin='+location1.string()+'&destination='+location2.string()+'&departure_time=1619638472&alternatives=true&mode=transit&key='+GOOGLE_TOKEN)
    if r.status_code == 200:
        json_returned_data = r.json()
        with open(REQUESTS_FOLDER+str(location1.lat)+'_'+str(location1.lng)+'_'+str(location2.lat)+'_'+str(location2.lng)+'.json', 'w') as outfile:
            json.dump(json_returned_data, outfile)

def call_google_and_save():
    for i in range(NUMBER_OF_REQUESTS_TO_SAVE):
        random_point = get_random_point_in_nyc(None)
        print(str(random_point.lat)+","+str(random_point.lng))

        if GET_SHORT_POINTS:
            random_point2 = get_random_point_in_nyc(random_point)
        else:
            random_point2 = get_random_point_in_nyc(None)

        print('https://www.google.com/maps/dir/'+str(random_point.lat)+','+str(random_point.lng)+'/'+str(random_point2.lat)+','+str(random_point2.lng)+'/')
        get_google_directions_between_points(random_point,random_point2)

def parse_saved_routes():
    return_value = []
    for filename in os.listdir(REQUESTS_FOLDER):
        if filename.endswith('.json'):
            with open(os.path.join(REQUESTS_FOLDER, filename)) as f:
                data = json.load(f)
                if len(data['routes']) != 0:
                    fastest_includes_bus_route = None
                    fastest_none_bus_route = None
                    for iter_route in range(len(data['routes'])):
                        if len(data['routes'][iter_route]['legs']) >1:
                            print("Item has more than 1 leg")
                        current_route_secs = data['routes'][0]['legs'][0]['duration']['value']
                        current_route_includes_bus = False
                        for i in range(len(data['routes'][iter_route]['legs'][0]['steps'])):
                            if data['routes'][iter_route]['legs'][0]['steps'][i]['travel_mode'] == 'TRANSIT' and data['routes'][iter_route]['legs'][0]['steps'][i]['transit_details']['line']['vehicle']['type'] == 'BUS':
                                current_route_includes_bus = True

                        if (fastest_includes_bus_route == None) or (current_route_includes_bus and current_route_secs<fastest_includes_bus_route.transit_time):
                            fastest_includes_bus_route = RouteObject(iter_route,current_route_secs)
                        elif not current_route_includes_bus and (fastest_none_bus_route == None) or (not current_route_includes_bus and current_route_secs<fastest_none_bus_route.transit_time):
                            fastest_none_bus_route = RouteObject(iter_route,current_route_secs)

                    if fastest_includes_bus_route != None:
                        if fastest_none_bus_route == None or (fastest_includes_bus_route.transit_time < (fastest_none_bus_route.transit_time -300)):
                            for i in range(len(data['routes'][fastest_includes_bus_route.route_index]['legs'][0]['steps'])):
                                if data['routes'][fastest_includes_bus_route.route_index]['legs'][0]['steps'][i]['travel_mode'] == 'TRANSIT' and data['routes'][fastest_includes_bus_route.route_index]['legs'][0]['steps'][i]['transit_details']['line']['vehicle']['type'] == 'BUS':
                                    bus_name = data['routes'][fastest_includes_bus_route.route_index]['legs'][0]['steps'][i]['transit_details']['line']['short_name']
                                    poly = data['routes'][fastest_includes_bus_route.route_index]['legs'][0]['steps'][i]['polyline']['points']
                                    save_value = {"Bus":bus_name,"poly":poly}
                                    return_value.append(save_value)

    with open('./draw_map/lines_gen.js', 'w') as outfile:
        outfile.write("var DATA =")
        json.dump(return_value, outfile)

def parse_bus_polylines():
    return_value = []
    for filename in os.listdir(REQUESTS_FOLDER):
        if filename.endswith('.json'):
            with open(os.path.join(REQUESTS_FOLDER, filename)) as f:
                data = json.load(f)
                if len(data['routes']) != 0:
                    for iter_route in range(len(data['routes'])):
                        for i in range(len(data['routes'][iter_route]['legs'][0]['steps'])):
                            if data['routes'][iter_route]['legs'][0]['steps'][i]['travel_mode'] == 'TRANSIT' and data['routes'][iter_route]['legs'][0]['steps'][i]['transit_details']['line']['vehicle']['type'] == 'BUS':
                                try:
                                    bus_name = data['routes'][iter_route]['legs'][0]['steps'][i]['transit_details']['line']['short_name']
                                    poly = data['routes'][iter_route]['legs'][0]['steps'][i]['polyline']['points']
                                    save_value = {"Bus":bus_name,"poly":poly}
                                    return_value.append(save_value)
                                except:
                                    print("exception")

    with open('./draw_map/busses.js', 'w') as outfile:
        outfile.write("var DATABUS =")
        json.dump(return_value, outfile)

def strip_and_float(stringFloat):
    if '.json' in stringFloat:
        stringFloat = stringFloat.replace('.json','')
    return float(stringFloat)

def parse_and_create_line_between_points():
    return_value = []
    for filename in os.listdir(REQUESTS_FOLDER):
        if filename.endswith('.json'):
            filename_split = filename.split('_')
            save_value = [{"lat":strip_and_float(filename_split[0]),"lng":strip_and_float(filename_split[1])},{"lat":strip_and_float(filename_split[2]),"lng":strip_and_float(filename_split[3])}]
            return_value.append(save_value)
    with open('./draw_map/points.js', 'w') as outfile:
        outfile.write("var DATAPOINTS =")
        json.dump(return_value, outfile)
                    




call_google_and_save()

#parse_bus_polylines()

#parse_saved_routes()

#parse_and_create_line_between_points()