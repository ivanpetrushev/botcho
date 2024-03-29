import json
from geopy.distance import great_circle
import math
from datetime import datetime

FILTER_MAX_DISTANCE = 50  # km
GEOCODING_FILENAME = 'geocoding-places-all.json'


class LightningNotifier():
    my_coords = [42.145078, 24.743958]  # Plovdiv
    # my_coords = [41.648288, 25.382538]  # Kardzhali
    # my_coords = [42.344082, 27.181206]  # Sredets
    # my_coords = [42.149151, 26.797028]  # Bolyarovo
    # my_coords = [41.385052, 2.219238]  # Barcelona
    data = None
    geocoding_data = []
    reported_clusters = {}

    def __init__(self):
        self.load_geocoding_data()

    # implement refresh_data as needed - be it as opening local file, URL, S3 object, etc

    def refresh_data(self):
        with open('../blitzortung-capture/webserver/data.json') as fp:
            try:
                self.data = json.load(fp)
            except err:
                print('LightningNotifier refresh_data error', err)
                self.data = None

    def load_geocoding_data(self):
        with open(GEOCODING_FILENAME) as fp:
            geocoding_data_json = json.load(fp)
        for item in geocoding_data_json['elements']:
            # skip villages, leave only bigger settlements
            if item['tags']['place'] == 'village':
                continue
            name = ''
            if 'name' in item['tags']:
                name = item['tags']['name']
            elif 'name:en' in item['tags']:
                name = item['tags']['name:en']
            self.geocoding_data.append({
                'lat': item['lat'],
                'lon': item['lon'],
                'name': name
            })

    def filter_latest_data(self):
        #TODO: handle stale data
        self.data = list(self.data.values())
        self.data = self.data.pop()
        # self.data = self.data['20200612-161009']

    def filter_only_nearby(self):
        close_clusters = []
        for cluster in self.data:
            cluster_coords = (cluster['center']['lat'],
                              cluster['center']['lon'])
            distance = great_circle(cluster_coords, self.my_coords)
            if distance < FILTER_MAX_DISTANCE:
                close_clusters.append(cluster)
        self.data = close_clusters
        print('LightningNotifier filter_only_nearby', close_clusters)

    # TODO: can we reduce this complexity down from O(N*M) ?
    def geocode_data(self):
        for i, item in enumerate(self.data):
            closest_place = self.geocoding_data[0]
            closest_distance = great_circle(
                [closest_place['lat'], closest_place['lon']], self.my_coords)
            for j in range(1, len(self.geocoding_data)):
                distance = great_circle([self.geocoding_data[j]['lat'], self.geocoding_data[j]['lon']], [
                                        item['center']['lat'], item['center']['lon']])
                if distance < closest_distance:
                    closest_distance = distance
                    closest_place = self.geocoding_data[j]
            self.data[i]['closest'] = {
                'name': closest_place['name'],
                'distance': closest_distance.km,
                'bearing': self.bearing(closest_place, item['center'])
            }

    # TODO: can we have this in geopy or geographiclib?
    def bearing(self, pointA, pointB):
        lat1 = math.radians(pointA['lat'])
        lat2 = math.radians(pointB['lat'])

        diffLong = math.radians(pointB['lon'] - pointA['lon'])

        x = math.sin(diffLong) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
                                               * math.cos(lat2) * math.cos(diffLong))

        initial_bearing = math.atan2(x, y)

        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360

        return compass_bearing

    def bearing_to_direction(self, bearing):
        sectors = {
            0: 'северно',
            45: 'североизточно',
            90: 'източно',
            135: 'югоизточно',
            180: 'южно',
            225: 'югозападно',
            270: 'западно',
            315: 'северозападно'
        }
        keys = list(sectors.keys())
        sector_half_size = 360 / len(keys) / 2
        for i in range(len(keys)):
            sector_key = keys[i]
            begin = sector_key - sector_half_size
            end = sector_key + sector_half_size
            print('item', begin, bearing, end)
            if begin <= bearing <= end:
                return sectors[sector_key]
        # if we are still here, bearing is most likely left of the first sector
        return sectors[keys[0]]

    def notify(self):
        self.refresh_data()
        self.filter_latest_data()
        self.filter_only_nearby()
        self.geocode_data()
        print('lightning data', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.data)
        msgs = []
        for item in self.data:
            closest_name = item['closest']['name']
            if closest_name not in self.reported_clusters:
                dist = round(item['closest']['distance'])
                bearing = round(item['closest']['bearing'])
                direction = self.bearing_to_direction(bearing)
                count = item['count']
                msgs.append(
                    f'Буря: {dist} km {direction} от {closest_name} ({count} мълнии / 5 мин)')
                # self.reported_clusters['closest_name'] = True
        # print('msgs', msgs)

        return "\n".join(msgs)
