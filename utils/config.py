import os
from dotenv import load_dotenv
load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not SPOTIFY_CLIENT_ID:
    raise ValueError("SPOTIFY_CLIENT_ID not found in environment variables")

if not SPOTIFY_CLIENT_SECRET:
    raise ValueError("SPOTIFY_CLIENT_SECRET not found in environment variables")

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

# min, max
ROLE_RANGES = {
    "TOP": {
        "dpm": (200, 1200),
        "kills_per_minute": (0.1, 0.5),
        "kill_participation": (0.1, 0.6),
        "assists_per_minute": (0.05, 0.4),
        "deaths_per_minute": (0.1, 0.5),
        "kda": (0.5, 5),
        "vsm": (0.3, 2),
        "epic_takedowns_per_minute": (0, 0.05),
        "csm": (4, 10),
        "game_duration": (900, 3000),
        "win": (0.4, 0.8)
    },
    "JUNGLE": {
        "dpm": (100, 1000),
        "kills_per_minute": (0.1, 0.5),
        "kill_participation": (0.2, 0.8),
        "assists_per_minute": (0.1, 0.6),
        "deaths_per_minute": (0, 0.5),
        "kda": (0.5, 5),
        "vsm": (0.5, 3),
        "epic_takedowns_per_minute": (0, 0.1),
        "csm": (4, 10),
        "game_duration": (900, 3000),
        "win": (0.4, 0.8)
    },
    "MIDDLE": {
        "dpm": (200, 1200),
        "kills_per_minute": (0, 0.5),
        "kill_participation": (0.2, 0.7),
        "assists_per_minute": (0.1, 0.5),
        "deaths_per_minute": (0.1, 0.5),
        "kda": (0.5, 5),
        "vsm": (0.3, 2),
        "epic_takedowns_per_minute": (0, 0.05),
        "csm": (4, 10),
        "game_duration": (900, 3000),
        "win": (0.4, 0.8)
    },
    "ADC": {
        "dpm": (200, 1200),
        "kills_per_minute": (0.1, 0.5),
        "kill_participation": (0.2, 0.7),
        "assists_per_minute": (0.1, 0.4),
        "deaths_per_minute": (0.1, 0.5),
        "kda": (0.5, 5),
        "vsm": (0.3, 2),
        "epic_takedowns_per_minute": (0, 0.05),
        "csm": (4, 10),
        "game_duration": (900, 3000),
        "win": (0.4, 0.8)
    },
    "UTILITY": {
        "dpm": (100, 700),
        "kills_per_minute": (0.05, 0.3),
        "kill_participation": (0.2, 0.8),
        "assists_per_minute": (0.2, 0.6),
        "deaths_per_minute": (0.15, 0.6),
        "kda": (0.5, 5),
        "vsm": (0.5, 3),
        "epic_takedowns_per_minute": (0, 0.07),
        "csm": (0, 3),
        "game_duration": (900, 3000),
        "win": (0.4, 0.8)
    }
}

# note survivability is deaths per minute inverted (1-deaths_per_minute) scaled to 0-1
ROLE_WEIGHTS = {
    "TOP": {
        "dpm": 0.6,
        "kills_per_minute": 0.4,
        "kill_participation": 0.7,
        "assists_per_minute": 0.3,
        "survivability": 0.5,
        "kda": 0.5,
        "vsm": 0.6,
        "epic_takedowns_per_minute": 0.4,
        "csm": 0.8,
        "game_duration": 0.2
    },
    "JUNGLE": {
        "dpm": 0.5,
        "kills_per_minute": 0.5,
        "kill_participation": 0.7,
        "assists_per_minute": 0.3,
        "survivability": 0.6,
        "kda": 0.4,
        "vsm": 0.5,
        "epic_takedowns_per_minute": 0.5,
        "csm": 0.6,
        "game_duration": 0.4
    },
    "MIDDLE": {
        "dpm": 0.6,
        "kills_per_minute": 0.4,
        "kill_participation": 0.7,
        "assists_per_minute": 0.3,
        "survivability": 0.5,
        "kda": 0.5,
        "vsm": 0.6,
        "epic_takedowns_per_minute": 0.4,
        "csm": 0.8,
        "game_duration": 0.2
    },
    "ADC": {
        "dpm": 0.6,
        "kills_per_minute": 0.4,
        "kill_participation": 0.7,
        "assists_per_minute": 0.3,
        "survivability": 0.6,
        "kda": 0.4,
        "vsm": 0.4,
        "epic_takedowns_per_minute": 0.6,
        "csm": 0.9,
        "game_duration": 0.1
    },
    "UTILITY": {
        "dpm": 0.7,
        "kills_per_minute": 0.3,
        "kill_participation": 0.7,
        "assists_per_minute": 0.3,
        "survivability": 0.7,
        "kda": 0.3,
        "vsm": 0.8,
        "epic_takedowns_per_minute": 0.2,
        "csm": 0.3,
        "game_duration": 0.7
    }
}

TAG_TRAIT_BIAS = {
    "Marksman": {
        "scaling": 0.25,
        "stability": 0.15
    },

    "Assassin": {
        "aggression": 0.30,
        "control": 0.15
    },

    "Mage": {
        "control": 0.30,
        "scaling": 0.15
    },

    "Tank": {
        "stability": 0.35,
        "control": 0.20
    },

    "Fighter": {
        "aggression": 0.20,
        "stability": 0.15
    },

    "Support": {
        "teamwork": 0.30,
        "control": 0.20
    }
}

MUSIC_CLUSTER_VECTORS = {
    "pop": [0.67, 0.68, 0.61, 0.52],
    "kpop": [0.79, 0.72, 0.68, 0.64],
    "jpop": [0.73, 0.55, 0.59, 0.55],
    "hiphop": [0.62, 0.77, 0.54, 0.57],
    "rap": [0.58, 0.76, 0.39, 0.60],
    "trap": [0.65, 0.79, 0.46, 0.66],
    "drill": [0.60, 0.83, 0.67, 0.68],
    "edm": [0.78, 0.62, 0.44, 0.60],
    "electronic": [0.86, 0.64, 0.49, 0.62],
    "house": [0.79, 0.76, 0.51, 0.60],
    "techno": [0.91, 0.64, 0.30, 0.76],
    "rock": [0.76, 0.48, 0.58, 0.66],
    "alternative": [0.69, 0.52, 0.41, 0.58],
    "indie": [0.67, 0.59, 0.56, 0.50],
    "lofi": [0.20, 0.60, 0.20, 0.48],
    "downtempo": [0.53, 0.78, 0.32, 0.46]
}

MUSIC_CLUSTER_TO_SPOTIFY_SERACH = {
    "pop": "pop hits",
    "kpop": "kpop",
    "jpop": "jpop",
    "hiphop": "hip hop",
    "rap": "rap",
    "trap": "trap",
    "drill": "drill",
    "edm": "edm",
    "electronic": "electronic",
    "house": "house",
    "techno": "techno",
    "rock": "rock",
    "alternative": "alternative",
    "indie": "indie",
    "lofi": "lofi",
    "downtempo": "downtempo"
}