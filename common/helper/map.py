import requests


class Map:
    def __init__(self):
        self.api_key = "AIzaSyC0MGZPpZYu79oFwRFCG0yu-IfQHyBPTnM"
        self.url = 'https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'

    def get_coordinates(self, address):
        api_response = requests.get(self.url.format(address, self.api_key))
        api_response_dict = api_response.json()
        if api_response_dict['status'] == 'OK':
            latitude = api_response_dict['results'][0]['geometry']['location']['lat']
            longitude = api_response_dict['results'][0]['geometry']['location']['lng']
            return latitude, longitude
        else:
            return 1, 1
