import json
from urllib.request import urlopen


def get_water():
    api_key = open("gfy_token.txt", "r").read()
    url = 'http://api.giphy.com/v1/gifs/random?tag=fun+water&api_key=' + api_key
    fp = urlopen(url)
    contents = json.load(fp)
    return contents['data']['url']
