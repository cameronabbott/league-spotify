from services.riot_service import get_match_data
from utils.data_loader import CHAMPION_TAGS
from utils.config import ROLE_RANGES, ROLE_WEIGHTS, TAG_TRAIT_BIAS
from utils.helpers import normalise, clamp

from collections import defaultdict

TAGS = ["Marksman", "Assassin", "Mage", "Tank", "Fighter", "Support"]

ROLES = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]

def get_player_data_from_match(match_data, puuid):
    print(f"\nExtracting player data for puuid: {puuid} from match data")
    participants = match_data.get("info", {}).get("participants", [])
    
    for participant in participants:
        if participant.get("puuid") == puuid:
            player_data = {
                "champion": participant["championName"],
                "role": participant["teamPosition"],
                "kills": participant["kills"],
                "deaths": participant["deaths"],
                "assists": participant["assists"],
                "kill_participation": participant["challenges"].get("killParticipation", 0),
                "damage": participant["totalDamageDealtToChampions"],
                "vision_score": participant["visionScore"],
                "cs": participant["totalMinionsKilled"],
                "win": participant["win"],
                "game_duration": match_data["info"]["gameDuration"],
                "epic_takedowns": participant["challenges"]["baronTakedowns"] + participant["challenges"]["dragonTakedowns"] + participant["challenges"]["riftHeraldTakedowns"]
            }
            if player_data["game_duration"] < 300:
                print(f"Game duration is very short ({player_data['game_duration']} seconds). Returning None.")
                return None
            print(f"Player Data: {player_data}\n")
            return player_data
    print(f"Error: Player with puuid {puuid} not found in match data")
    return None

# if someone plays supp it will skew some of the stats
# maybe change this later or separate
def build_average_vector(puuid, matches, region):
    n = 0
    if matches is None:
        print(f"No matches found for puuid: {puuid}")
        return {}


    print(f"\nBuilding average vector for puuid: {puuid} using matches: {matches}")

    sums = {"archetype": {tag: 0 for tag in TAGS},
            "role": {role: 0 for role in ROLES},
            "kills": 0,
            "deaths": 0,
            "assists": 0,
            "kill_participation": 0,
            "damage": 0,
            "vision_score": 0,
            "cs": 0,
            "win": 0,
            "game_duration": 0,
            "objective_participation": 0,
            "epic_takedowns": 0}


    for match_id in matches:
        match_data = get_match_data(match_id, region)
        player_data = get_player_data_from_match(match_data, puuid)
    
        if player_data:
            n += 1
            role = player_data["role"]
            sums["role"][role] += 1
            sums["kills"] += player_data["kills"]
            sums["deaths"] += player_data["deaths"]
            sums["assists"] += player_data["assists"]
            sums["kill_participation"] += player_data["kill_participation"]
            sums["damage"] += player_data["damage"]
            sums["vision_score"] += player_data["vision_score"]
            sums["cs"] += player_data["cs"]
            sums["win"] += 1 if player_data["win"] else 0
            sums["game_duration"] += player_data["game_duration"]
            sums["epic_takedowns"] += player_data["epic_takedowns"]

            champion_name = player_data["champion"]
            tags = CHAMPION_TAGS[champion_name]
            if len(tags) == 1:
                sums["archetype"][tags[0]] += 1
            elif len(tags) == 2:
                sums["archetype"][tags[0]] += 0.7
                sums["archetype"][tags[1]] += 0.3
            else:
                print(f"Error: Champion {champion_name} has unexpected number of tags: {len(tags)}")
        
    if n == 0:
        print(f"No valid matches found for puuid: {puuid}")
        return {}
    average_sums = {key: (sums[key] / n if isinstance(sums[key], (int, float)) else {subkey: sums[key][subkey] / n for subkey in sums[key]}) for key in sums}
    deaths = 1
    if average_sums["deaths"] > 0:
        deaths = average_sums["deaths"]
    average_sums["kda"] = (average_sums["kills"] + average_sums["assists"]) / deaths
    average_sums["csm"] = average_sums["cs"] / (average_sums["game_duration"] / 60)
    average_sums["dpm"] = average_sums["damage"] / (average_sums["game_duration"] / 60)
    average_sums["vsm"] = average_sums["vision_score"] / (average_sums["game_duration"] / 60)
    average_sums["kills_per_minute"] = average_sums["kills"] / (average_sums["game_duration"] / 60)
    average_sums["assists_per_minute"] = average_sums["assists"] / (average_sums["game_duration"] / 60)
    average_sums["deaths_per_minute"] = average_sums["deaths"] / (average_sums["game_duration"] / 60)
    average_sums["epic_takedowns_per_minute"] = average_sums["epic_takedowns"] / (average_sums["game_duration"] / 60)

    print(f"Average Sums: {average_sums}\n")

    print("VALID MATCHES CONSIDERED: ", n)
    return average_sums

def obtain_normalised_vector(average_vector):
    normalised_vector = defaultdict(float)
    for role in average_vector["role"]:
         if average_vector["role"][role] > 0:
            for metric in ROLE_RANGES[role]:
                min_val, max_val = ROLE_RANGES[role][metric]
                if metric == "deaths_per_minute":
                    normalised_vector["survivability"] += (1 - normalise(average_vector[metric], min_val, max_val)) * average_vector["role"][role]
                else:
                    normalised_vector[metric] += normalise(average_vector[metric], min_val, max_val) * average_vector["role"][role]

    print(f"Normalised Vector: {normalised_vector}\n")
    return normalised_vector
# lets think which actual persoanlity i want
# role archetype plays into each of these
# use position to normalise, e.g. supp no cs
# aggression - dpm, kills per min
# teamwork - kp, assists per min
# stability - deaths per minute, kda
# control - vision score per minute, epic takedowns per minute
# scaling - csm, game duration

# i should also use the role archetype to infleucne some of them, e.g. mage more scaling
# current win rate can tie into one of the spotify things
# need to compare to baseline, we can change it later

# aggression, teamwork,
#aggression, teamwork, objective focus, vision control, zfarming efficiency, win rate, archetype preference, role preference
def build_personality_vector(normalised_vector, role_ratio, tag_ratio):
    personality_vector = defaultdict(float)
    for role in role_ratio:
        if role_ratio[role] > 0:
            personality_vector["aggression"] += role_ratio[role] * (ROLE_WEIGHTS[role]["dpm"] * normalised_vector["dpm"] + ROLE_WEIGHTS[role]["kills_per_minute"] * normalised_vector["kills_per_minute"])
            personality_vector["teamwork"] += role_ratio[role] * (ROLE_WEIGHTS[role]["kill_participation"] * normalised_vector["kill_participation"] + ROLE_WEIGHTS[role]["assists_per_minute"] * normalised_vector["assists_per_minute"])
            personality_vector["stability"] += role_ratio[role] * (ROLE_WEIGHTS[role]["survivability"] * normalised_vector["survivability"] + ROLE_WEIGHTS[role]["kda"] * normalised_vector["kda"])
            personality_vector["control"] += role_ratio[role] * (ROLE_WEIGHTS[role]["vsm"] * normalised_vector["vsm"] + ROLE_WEIGHTS[role]["epic_takedowns_per_minute"] * normalised_vector["epic_takedowns_per_minute"])
            personality_vector["scaling"] += role_ratio[role] * (ROLE_WEIGHTS[role]["csm"] * normalised_vector["csm"] + ROLE_WEIGHTS[role]["game_duration"] * normalised_vector["game_duration"])
    
    tag_effect = defaultdict(float)
    for tag in tag_ratio:
        if tag_ratio[tag] > 0:
            for personality in TAG_TRAIT_BIAS[tag]:
                tag_effect[personality] += tag_ratio[tag] * TAG_TRAIT_BIAS[tag][personality]
    
    for personality in personality_vector:
        personality_vector[personality] = clamp(personality_vector[personality] + tag_effect.get(personality, 0), 0, 1)

    print(f"Personality Vector: {personality_vector}\n")
    return personality_vector

