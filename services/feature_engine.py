from services.riot_service import get_match_data
from utils.data_loader import CHAMPION_TAGS

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
                "kill_participation": participant["challenges"]["killParticipation"],
                "damage": participant["totalDamageDealtToChampions"],
                "vision_score": participant["visionScore"],
                "cs": participant["totalMinionsKilled"],
                "win": participant["win"]
            }
            print(f"Player Data: {player_data}\n")
            return player_data
    
    print(f"Error: Player with puuid {puuid} not found in match data")
    return None

# i should just do all the aggregation here
def build_archetype_role_vector(puuid, matches, region):
    n = len(matches)
    archetype_sum = {tag: 0 for tag in TAGS}
    role_sum = {role: 0 for role in ROLES}
    if matches is None or n == 0:
        print(f"No matches found for puuid: {puuid}")
        return {tag: 0 for tag in TAGS}

    print(f"\nBuilding archetype vector for puuid: {puuid} using matches: {matches}")
    for match_id in matches:
        match_data = get_match_data(match_id, region)
        player_data = get_player_data_from_match(match_data, puuid)

        if player_data:
            role = player_data["role"]
            role_sum[role] += 1
            champion_name = player_data["champion"]
            tags = CHAMPION_TAGS[champion_name]
            if len(tags) == 1:
                archetype_sum[tags[0]] += 1
            elif len(tags) == 2:
                archetype_sum[tags[0]] += 0.7
                archetype_sum[tags[1]] += 0.3
            else:
                print(f"Error: Champion {champion_name} has unexpected number of tags: {len(tags)}")

    print(f"Archetype Vector: {archetype_sum}")
    print(f"Role Vector: {role_sum}")

    match_archetype_vector = {tag: archetype_sum[tag] / n for tag in TAGS}
    match_role_vector = {role: role_sum[role] / n for role in ROLES}
    print(f"Normalized Archetype Vector: {match_archetype_vector}")
    print(f"Normalized Role Vector: {match_role_vector}\n")

    return match_archetype_vector, match_role_vector
