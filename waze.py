from urllib.request import urlopen
from urllib.error import HTTPError
from http.client import RemoteDisconnected
import json

# Plovdiv
URL = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=42.109866620565185&left=24.56079483032227&ma=200&mj=100&mu=20&right=24.956302642822266&top=42.185619292989614&types=alerts"
# Sofia
# URL = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=42.64190732763769&left=23.16398620605469&ma=200&mj=100&right=23.55949401855469&top=42.73593586744372&types=alerts"
# Stara Zagora
# URL = "https://www.waze.com/row-rtserver/web/TGeoRSS?bottom=42.40520165483446&left=25.52699089050293&ma=200&mj=100&right=25.72474479675293&top=42.45241232558495&types=alerts"


class WazeNotifier:
    data = {}
    data_accidents = []
    reported_accidents = []

    def refresh_data(self):
        self.data = {}
        try:
            response = urlopen(URL)
            data_json = json.loads(response.read())
            self.data = data_json
        except (HTTPError, RemoteDisconnected) as err:
            print('WazeNotifier refresh_data error', err)
            self.data = {}

    def filter_accidents(self):
        self.data_accidents = []
        if 'alerts' not in self.data:
            return
        for item in self.data['alerts']:
            id = item['id']
            # print('filter_accidents', id, item)
            # print('reported_accidents', self.reported_accidents)
            if item['type'] == 'ACCIDENT' and 'street' in item and id not in self.reported_accidents:
                print('New accident', item)
                self.data_accidents.append(item)

    def store_data(self):
        # add new items to old data
        for item in self.data_accidents:
            id = item['id']
            self.reported_accidents.append(id)
        # keep only 10 reported accidents
        self.reported_accidents = self.reported_accidents[-10:]

    def notify(self):
        self.refresh_data()
        self.filter_accidents()
        msgs = []
        for item in self.data_accidents:
            street = item['street']
            x = item['location']['x']
            y = item['location']['y']
            msgs.append(
                f'Нов доклад за катастрофа: {street} - {y},{x} https://google.com/maps/place/{y},{x}')
        self.store_data()
        return "\n".join(msgs)
