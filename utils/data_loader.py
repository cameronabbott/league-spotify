import requests

def load_champion_tags():
    url = "https://ddragon.leagueoflegends.com/cdn/16.11.1/data/en_US/champion.json"
    data = requests.get(url).json()['data']

    champion_tags = {}
    for champ_name, champ_info in data.items():
        champion_tags[champ_name] = champ_info['tags']
    
    return champion_tags

CHAMPION_TAGS = load_champion_tags()