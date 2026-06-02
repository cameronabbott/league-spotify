import os
from dotenv import load_dotenv
load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")

if not RIOT_API_KEY:
    raise ValueError("RIOT_API_KEY not found in environment variables")

HEADERS = {
    "X-Riot-Token": RIOT_API_KEY
}


# The AMERICAS routing value serves NA, BR, LAN and LAS. The ASIA routing value serves KR and JP. 
# The EUROPE routing value serves EUNE, EUW, ME1, TR and RU. The SEA routing value serves OCE, SG2, TW2 and VN2.


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