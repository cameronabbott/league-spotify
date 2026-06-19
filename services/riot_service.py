import requests
from urllib.parse import quote
from utils.config import HEADERS, REGION_TO_ROUTING

UNEXPECTED_API_ERROR = "Unexpected error found. Please try again later."


class RiotApiError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def raise_riot_error(response, action):
    print(f"Error {action}: {response.status_code} - {response.text}")

    if response.status_code in (401, 403):
        raise RiotApiError(
            502,
            UNEXPECTED_API_ERROR,
        )

    if response.status_code == 429:
        raise RiotApiError(
            429,
            UNEXPECTED_API_ERROR,
        )

    raise RiotApiError(
        502,
        UNEXPECTED_API_ERROR,
    )


def get_puuid(game_name, tag_line):
    print(f"\nFetching puuid for player: {game_name} #{tag_line}")

    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        if response.status_code == 404:
            print(f"Account not found: {response.status_code} - {response.text}")
            return None
        raise_riot_error(response, "fetch the Riot account")
    
    puuid = response.json().get("puuid")
    if puuid is None:
        print("Error: 'puuid' not found in the response")
    else:    
        print(f"puuid: {puuid}\n")
        return puuid

def get_matches(puuid, region, count=10):
    print(f"\nFetching the last {count} ranked matches in {region} for puuid: {puuid}")
    ranked_queue_id = 420  # Ranked Solo/Duo queue ID
    routing = REGION_TO_ROUTING.get(region)
    if not routing:
        print(f"Error: Invalid region '{region}'")
        return None
    
    url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}&queue={ranked_queue_id}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise_riot_error(response, "fetch ranked match history")
    
    matches = response.json()
    print(f"Matches: {matches}\n")
    return matches

# team position - for role 
# investigate what other stats we want like kp, kda, cs, gold, damage, vision score, etc
# win loss

def get_match_data(match_id, region):
    print(f"\nFetching match data for match ID: {match_id} in region: {region}")
    routing = REGION_TO_ROUTING.get(region)
    if not routing:
        print(f"Error: Invalid region '{region}'")
        return None
    
    url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        raise_riot_error(response, "fetch match data")
    
    match_data = response.json()
    # print(f"Match Data: {match_data}")
    return match_data
