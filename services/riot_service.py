import requests
from urllib.parse import quote
from utils.config import RIOT_API_KEY

# todo get user input for summoner name and reigion
# region dont matter for getting puuid but does for puuid call
# need to translate summoner name to puuid and then use puuid to get match history

# The AMERICAS routing value serves NA, BR, LAN and LAS. The ASIA routing value serves KR and JP. 
# The EUROPE routing value serves EUNE, EUW, ME1, TR and RU. The SEA routing value serves OCE, SG2, TW2 and VN2.

HEADERS = {
    "X-Riot-Token": RIOT_API_KEY
}

REGION_TO_ROUTING = {
    "KR": "asia",
    "JP": "asia",

    "EUNE": "europe",
    "EUW": "europe",
    "ME1": "europe",
    "TR": "europe",
    "RU": "europe",

    "OCE": "sea",
    "SG2": "sea",
    "TW2": "sea",
    "VN2": "sea",

    "NA": "americas",
    "BR": "americas",
    "LAN": "americas",
    "LAS": "americas",
}

def get_puuid(game_name, tag_line):
    print(f"Fetching puuid for player: {game_name} #{tag_line}")
    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Error fetching puuid: {response.status_code} - {response.text}")
        return None
    
    puuid = response.json().get("puuid")
    if puuid is None:
        print("Error: 'puuid' not found in the response")
    else:    
        print(f"puuid: {puuid}")
        return puuid

def get_matches(puuid, region, count=10):
    print(f"Fetching the last {count} ranked matches in {region} for puuid: {puuid}")
    routing = REGION_TO_ROUTING.get(region)
    if not routing:
        print(f"Error: Invalid region '{region}'")
        return None
    
    url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Error fetching matches: {response.status_code} - {response.text}")
        return None
    
    matches = response.json()
    print(f"Matches: {matches}")
    return matches

# team position - for role 
# investigate what other stats we want like kp, kda, cs, gold, damage, vision score, etc
# win loss
# forfeit games, if forfeit worse mood probably
def get_match_data(match_id, region):
    print(f"Fetching match data for match ID: {match_id} in region: {region}")
    routing = REGION_TO_ROUTING.get(region)
    if not routing:
        print(f"Error: Invalid region '{region}'")
        return None
    
    url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Error fetching match data: {response.status_code} - {response.text}")
        return None
    
    match_data = response.json()
    print(f"Match Data: {match_data}")
    return match_data

def get_player_data_from_match(match_data, puuid):
    print(f"Extracting player data for puuid: {puuid} from match data")
    participants = match_data.get("info", {}).get("participants", [])
    
    for participant in participants:
        if participant.get("puuid") == puuid:
            print(f"Player Data: {participant}")
            return participant
    
    print(f"Error: Player with puuid {puuid} not found in match data")
    return None

game_name = "Hide on bush"
tag_line = "KR1"

puuid = get_puuid(game_name, tag_line)
faker_matches = get_matches(puuid, "KR")

match_data = get_match_data(faker_matches[0], "KR")
print("--- Player Data from Match ---")
player_data = get_player_data_from_match(match_data, puuid)


# no ranked games test
# game_name = "Askeladd"
# tag_line = "4037"

# puuid = get_puuid(game_name, tag_line)
# get_matches(puuid, "EUW")