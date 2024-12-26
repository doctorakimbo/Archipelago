"""
Looks through data object to double-check it makes sense. Will fail for missing or duplicate definitions or
duplicate claims and give warnings for unused and unignored locations or warps.
"""
import logging
from typing import List
from .data import load_json_data, data

_IGNORABLE_LOCATIONS = frozenset({
    # Duplicate rival trainers
    "TRAINER_MOS_RANGER_SQUAD_LIQUIPUT_REWARD",
    "TRAINER_MOS_RANGER_SQUAD_PEYERO_REWARD",
    "TRAINER_RIVAL_HOLLYS_LAB_LIQUIPUT_REWARD",
    "TRAINER_RIVAL_HOLLYS_LAB_PEYERO_REWARD",
    "TRAINER_RIVAL_ORPIMENCE_LIQUIPUT_REWARD",
    "TRAINER_RIVAL_ORPIMENCE_PEYERO_REWARD",
    "TRAINER_RIVAL_RAVENPLUME_LIQUIPUT_REWARD",
    "TRAINER_RIVAL_RAVENPLUME_PEYERO_REWARD",
    "TRAINER_RIVAL_SEAFIN_LIQUIPUT_REWARD",
    "TRAINER_RIVAL_SEAFIN_PEYERO_REWARD",
    "TRAINER_RIVAL_VICTORY_ROAD_LIQUIPUT_REWARD",
    "TRAINER_RIVAL_VICTORY_ROAD_PEYERO_REWARD"
})

# todo: vega
_IGNORABLE_WARPS = frozenset({
    # Elevators
    "MAP_CELADON_CITY_DEPARTMENT_STORE_1F:2/MAP_CELADON_CITY_DEPARTMENT_STORE_ELEVATOR:0!",
    "MAP_CELADON_CITY_DEPARTMENT_STORE_2F:0/MAP_CELADON_CITY_DEPARTMENT_STORE_ELEVATOR:0!",
    "MAP_CELADON_CITY_DEPARTMENT_STORE_3F:0/MAP_CELADON_CITY_DEPARTMENT_STORE_ELEVATOR:0!",
    "MAP_CELADON_CITY_DEPARTMENT_STORE_4F:0/MAP_CELADON_CITY_DEPARTMENT_STORE_ELEVATOR:0!",
    "MAP_CELADON_CITY_DEPARTMENT_STORE_5F:0/MAP_CELADON_CITY_DEPARTMENT_STORE_ELEVATOR:0!",
    "MAP_CELADON_CITY_DEPARTMENT_STORE_ELEVATOR:0,1/MAP_DYNAMIC:-1!",
    
    "MAP_ROCKET_HIDEOUT_B1F:3/MAP_ROCKET_HIDEOUT_ELEVATOR:0!",
    "MAP_ROCKET_HIDEOUT_B2F:3/MAP_ROCKET_HIDEOUT_ELEVATOR:0!",
    "MAP_ROCKET_HIDEOUT_B4F:1/MAP_ROCKET_HIDEOUT_ELEVATOR:0!",
    "MAP_ROCKET_HIDEOUT_ELEVATOR:0/MAP_DYNAMIC:-1!",
    
    "MAP_SILPH_CO_1F:2/MAP_SILPH_CO_ELEVATOR:0!",
    "MAP_SILPH_CO_2F:6/MAP_SILPH_CO_ELEVATOR:0!",
    "MAP_SILPH_CO_3F:9/MAP_SILPH_CO_ELEVATOR:0!",
    "MAP_SILPH_CO_4F:6/MAP_SILPH_CO_ELEVATOR:0!",
    "MAP_SILPH_CO_5F:6/MAP_SILPH_CO_ELEVATOR:0!",
    "MAP_SILPH_CO_6F:4/MAP_SILPH_CO_ELEVATOR:0!",
    "MAP_SILPH_CO_7F:5/MAP_SILPH_CO_ELEVATOR:0!",
    "MAP_SILPH_CO_8F:6/MAP_SILPH_CO_ELEVATOR:0!",
    "MAP_SILPH_CO_9F:4/MAP_SILPH_CO_ELEVATOR:0!",
    "MAP_SILPH_CO_10F:5/MAP_SILPH_CO_ELEVATOR:0!",
    "MAP_SILPH_CO_11F:2/MAP_SILPH_CO_ELEVATOR:0!",
    "MAP_SILPH_CO_ELEVATOR:0/MAP_DYNAMIC:-1!",
    
    # Trainer Tower
    "MAP_TRAINER_TOWER_LOBBY:0/MAP_TRAINER_TOWER_1F:1",
    "MAP_TRAINER_TOWER_LOBBY:2/MAP_TRAINER_TOWER_ELEVATOR:0!",
    "MAP_TRAINER_TOWER_1F:0/MAP_TRAINER_TOWER_2F:1",
    "MAP_TRAINER_TOWER_1F:1/MAP_TRAINER_TOWER_LOBBY:0",
    "MAP_TRAINER_TOWER_2F:0/MAP_TRAINER_TOWER_3F:1",
    "MAP_TRAINER_TOWER_2F:1/MAP_TRAINER_TOWER_1F:0",
    "MAP_TRAINER_TOWER_3F:0/MAP_TRAINER_TOWER_4F:1",
    "MAP_TRAINER_TOWER_3F:1/MAP_TRAINER_TOWER_2F:0",
    "MAP_TRAINER_TOWER_4F:0/MAP_TRAINER_TOWER_5F:1",
    "MAP_TRAINER_TOWER_4F:1/MAP_TRAINER_TOWER_3F:0",
    "MAP_TRAINER_TOWER_5F:0/MAP_TRAINER_TOWER_6F:1",
    "MAP_TRAINER_TOWER_5F:1/MAP_TRAINER_TOWER_4F:0",
    "MAP_TRAINER_TOWER_6F:0/MAP_TRAINER_TOWER_7F:1",
    "MAP_TRAINER_TOWER_6F:1/MAP_TRAINER_TOWER_5F:0",
    "MAP_TRAINER_TOWER_7F:0/MAP_TRAINER_TOWER_8F:1",
    "MAP_TRAINER_TOWER_7F:1/MAP_TRAINER_TOWER_6F:0",
    "MAP_TRAINER_TOWER_8F:0/MAP_TRAINER_TOWER_ROOF:1",
    "MAP_TRAINER_TOWER_8F:1/MAP_TRAINER_TOWER_7F:0",
    "MAP_TRAINER_TOWER_ROOF:0/MAP_TRAINER_TOWER_ELEVATOR:0!",
    "MAP_TRAINER_TOWER_ROOF:1/MAP_TRAINER_TOWER_8F:0",
    "MAP_TRAINER_TOWER_ELEVATOR:0/MAP_DYNAMIC:-1!",

    # Multiplayer rooms
    "MAP_RECORD_CORNER:0,1,2,3/MAP_DYNAMIC:-1!",
    
    "MAP_CELADON_CITY_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_CERULEAN_CITY_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_CINNABAR_ISLAND_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_FIVE_ISLAND_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_FOUR_ISLAND_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_FUCHSIA_CITY_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_INDIGO_PLATEAU_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_LAVENDER_TOWN_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_ONE_ISLAND_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_PEWTER_CITY_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_ROUTE4_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_ROUTE10_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_SAFFRON_CITY_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_SEVEN_ISLAND_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_SIX_ISLAND_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_THREE_ISLAND_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_TWO_ISLAND_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_VERMILION_CITY_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_VIRIDIAN_CITY_POKEMON_CENTER_2F:1/MAP_UNION_ROOM:0!",
    "MAP_UNION_ROOM:0/MAP_DYNAMIC:-1!",
    
    "MAP_CELADON_CITY_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_CERULEAN_CITY_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_CINNABAR_ISLAND_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_FIVE_ISLAND_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_FOUR_ISLAND_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_FUCHSIA_CITY_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_INDIGO_PLATEAU_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_LAVENDER_TOWN_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_ONE_ISLAND_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_PEWTER_CITY_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_ROUTE4_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_ROUTE10_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_SAFFRON_CITY_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_SEVEN_ISLAND_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_SIX_ISLAND_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_THREE_ISLAND_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_TWO_ISLAND_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_VERMILION_CITY_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_VIRIDIAN_CITY_POKEMON_CENTER_2F:2/MAP_TRADE_CENTER:0!",
    "MAP_TRADE_CENTER:0,1/MAP_DYNAMIC:-1!",
    
    "MAP_SEVEN_ISLAND_HOUSE_ROOM1:1/MAP_SEVEN_ISLAND_HOUSE_ROOM2:0",
    "MAP_SEVEN_ISLAND_HOUSE_ROOM2:0/MAP_SEVEN_ISLAND_HOUSE_ROOM1:1",
    
    "MAP_BATTLE_COLOSSEUM_2P:0,1/MAP_DYNAMIC:-1!",
    "MAP_BATTLE_COLOSSEUM_4P:0,1,2,3/MAP_DYNAMIC:-1!"
})


def validate_regions() -> bool:
    """
    Verifies that Vega's data doesn't have duplicate or missing
    regions/warps/locations. Meant to catch problems during development like
    forgetting to add a new location or incorrectly splitting a region.
    """

    extracted_data = load_json_data("extracted_data.json")
    error_messages: List[str] = []
    warn_messages: List[str] = []
    failed = False

    def error(message: str) -> None:
        nonlocal failed
        failed = True
        error_messages.append(message)

    def warn(message: str) -> None:
        warn_messages.append(message)

    # Check regions
    for name, region in data.regions.items():
        for region_exit in region.exits:
            if region_exit not in data.regions:
                error(f"Pokemon Vega: Region [{region_exit}] referenced by [{name}] was not defined")

    # Check warps
    for source, dest in data.warp_map.items():
        if source in _IGNORABLE_WARPS:
            continue

        if dest is None:
            error(f"Pokemon Vega: Warp [{source}] has no destination")
        elif not data.warps[dest].connects_to(data.warps[source]) and not data.warps[source].is_one_way:
            error(f"Pokemon Vega: Warp [{source}] appears to be a one-way warp but was not marked as one")

    # Check locations
    region_locations = [location for region in data.regions.values() for location in region.locations]
    claimed_locations = set()
    for location_id in region_locations:
        if location_id in claimed_locations:
            error(f"Pokemon Vega: Location [{location_id}] exists in multiple regions")
        claimed_locations.add(location_id)

    for location_id in extracted_data["locations"]:
        if location_id not in claimed_locations and location_id not in _IGNORABLE_LOCATIONS:
            warn(f"Pokemon Vega: Location [{location_id}] does not belong to any region")

    warn_messages.sort()
    error_messages.sort()

    for message in warn_messages:
        logging.warning(message)

    for message in error_messages:
        logging.error(message)

    logging.debug("Pokemon Vega sanity check done. Found %s errors and %s warnings.",
                  len(error_messages),
                  len(warn_messages))

    return not failed
