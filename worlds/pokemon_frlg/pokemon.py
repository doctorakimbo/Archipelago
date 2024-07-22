import math
from typing import TYPE_CHECKING, Dict, List, Set
from .data import data, NUM_REAL_SPECIES, EventData, SpeciesData
from .options import (RandomizeLegendaryPokemon, RandomizeMiscPokemon, RandomizeStarters, RandomizeWildPokemon,
                      WildPokemonGroups)
if TYPE_CHECKING:
    from . import PokemonFRLGWorld

DUNGEON_GROUPS: Dict[str, str] = {
    "MAP_MT_MOON_1F": "MAP_MT_MOON",
    "MAP_MT_MOON_B1F": "MAP_MT_MOON",
    "MAP_MT_MOON_B2F": "MAP_MT_MOON",
    "MAP_ROCK_TUNNEL_1F": "MAP_ROCK_TUNNEL",
    "MAP_ROCK_TUNNEL_B1F": "MAP_ROCK_TUNNEL",
    "MAP_POKEMON_TOWER_3F": "MAP_POKEMON_TOWER",
    "MAP_POKEMON_TOWER_4F": "MAP_POKEMON_TOWER",
    "MAP_POKEMON_TOWER_5F": "MAP_POKEMON_TOWER",
    "MAP_POKEMON_TOWER_6F": "MAP_POKEMON_TOWER",
    "MAP_POKEMON_TOWER_7F": "MAP_POKEMON_TOWER",
    "MAP_SAFARI_ZONE_CENTER": "MAP_SAFARI_ZONE",
    "MAP_SAFARI_ZONE_EAST": "MAP_SAFARI_ZONE",
    "MAP_SAFARI_ZONE_NORTH": "MAP_SAFARI_ZONE",
    "MAP_SAFARI_ZONE_WEST": "MAP_SAFARI_ZONE",
    "MAP_SEAFOAM_ISLANDS_1F": "MAP_SEAFOAM_ISLANDS",
    "MAP_SEAFOAM_ISLANDS_B1F": "MAP_SEAFOAM_ISLANDS",
    "MAP_SEAFOAM_ISLANDS_B2F": "MAP_SEAFOAM_ISLANDS",
    "MAP_SEAFOAM_ISLANDS_B3F": "MAP_SEAFOAM_ISLANDS",
    "MAP_SEAFOAM_ISLANDS_B4F": "MAP_SEAFOAM_ISLANDS",
    "MAP_POKEMON_MANSION_1F": "MAP_POKEMON_MANSION",
    "MAP_POKEMON_MANSION_2F": "MAP_POKEMON_MANSION",
    "MAP_POKEMON_MANSION_3F": "MAP_POKEMON_MANSION",
    "MAP_POKEMON_MANSION_B1F": "MAP_POKEMON_MANSION",
    "MAP_VICTORY_ROAD_1F": "MAP_VICTORY_ROAD",
    "MAP_VICTORY_ROAD_2F": "MAP_VICTORY_ROAD",
    "MAP_VICTORY_ROAD_3F": "MAP_VICTORY_ROAD",
    "MAP_MT_EMBER_EXTERIOR": "MAP_MT_EMBER",
    "MAP_MT_EMBER_SUMMIT_PATH_1F": "MAP_MT_EMBER",
    "MAP_MT_EMBER_SUMMIT_PATH_2F": "MAP_MT_EMBER",
    "MAP_MT_EMBER_SUMMIT_PATH_3F": "MAP_MT_EMBER",
    "MAP_MT_EMBER_RUBY_PATH_1F": "MAP_MT_EMBER",
    "MAP_MT_EMBER_RUBY_PATH_B1F": "MAP_MT_EMBER",
    "MAP_MT_EMBER_RUBY_PATH_B1F_STAIRS": "MAP_MT_EMBER",
    "MAP_MT_EMBER_RUBY_PATH_B2F": "MAP_MT_EMBER",
    "MAP_MT_EMBER_RUBY_PATH_B2F_STAIRS": "MAP_MT_EMBER",
    "MAP_MT_EMBER_RUBY_PATH_B3F": "MAP_MT_EMBER",
    "MAP_FOUR_ISLAND_ICEFALL_CAVE_ENTRANCE": "MAP_FOUR_ISLAND_ICEFALL_CAVE",
    "MAP_FOUR_ISLAND_ICEFALL_CAVE_1F": "MAP_FOUR_ISLAND_ICEFALL_CAVE",
    "MAP_FOUR_ISLAND_ICEFALL_CAVE_B1F": "MAP_FOUR_ISLAND_ICEFALL_CAVE",
    "MAP_FOUR_ISLAND_ICEFALL_CAVE_BACK": "MAP_FOUR_ISLAND_ICEFALL_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM1": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM2": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM3": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM4": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM5": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM6": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM7": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM8": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM9": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM10": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM11": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM12": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM13": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_FIVE_ISLAND_LOST_CAVE_ROOM14": "MAP_FIVE_ISLAND_LOST_CAVE",
    "MAP_CERULEAN_CAVE_1F": "MAP_CERULEAN_CAVE",
    "MAP_CERULEAN_CAVE_2F": "MAP_CERULEAN_CAVE",
    "MAP_CERULEAN_CAVE_B1F": "MAP_CERULEAN_CAVE"
}

STARTER_INDEX: Dict[str, int] = {
    "STARTER_POKEMON_BULBASAUR": 0,
    "STARTER_POKEMON_CHARMANDER": 1,
    "STARTER_POKEMON_SQUIRTLE": 2
}

NON_STATIC_MISC_POKEMON: List[str] = {
    "CELADON_PRIZE_POKEMON_1",
    "CELADON_PRIZE_POKEMON_2",
    "CELADON_PRIZE_POKEMON_3",
    "CELADON_PRIZE_POKEMON_4",
    "CELADON_PRIZE_POKEMON_5"
}


def filter_species_by_nearby_bst(species: List[SpeciesData], target_bst: int) -> List[SpeciesData]:
    # Sort by difference in bst, then chop off the tail of the list that's more than
    # 10% different. If that leaves the list empty, increase threshold to 20%, then 30%, etc.
    species = sorted(species, key=lambda species: abs(sum(species.base_stats) - target_bst))
    cutoff_index = 0
    max_percent_different = 10
    while cutoff_index == 0 and max_percent_different < 10000:
        while (cutoff_index < len(species) and
               abs(sum(species[cutoff_index].base_stats) - target_bst) < target_bst * (max_percent_different / 100)):
            cutoff_index += 1
        max_percent_different += 10

    return species[:cutoff_index + 1]


def randomize_wild_encounters(world: "PokemonFRLGWorld") -> None:
    if world.options.wild_pokemon == RandomizeWildPokemon.option_vanilla:
        return

    from collections import defaultdict

    game_version = world.options.game_version.current_key
    min_pokemon_needed = math.ceil(max(world.options.oaks_aide_route_2.value,
                                       world.options.oaks_aide_route_10.value,
                                       world.options.oaks_aide_route_11.value,
                                       world.options.oaks_aide_route_16.value,
                                       world.options.oaks_aide_route_15.value) * 1.2)
    should_match_bst = world.options.wild_pokemon in {
        RandomizeWildPokemon.option_match_base_stats,
        RandomizeWildPokemon.option_match_base_stats_and_type
    }
    should_match_type = world.options.wild_pokemon in {
        RandomizeWildPokemon.option_match_type,
        RandomizeWildPokemon.option_match_base_stats_and_type
    }
    species_map: Dict[int, int] = {}
    dungeon_species_map: Dict[str, Dict[int, int]] = {}

    for map_group in DUNGEON_GROUPS.values():
        if map_group not in dungeon_species_map:
            dungeon_species_map[map_group] = {}

    # Route 21 is split into a North and South Map. We'll set this after we randomize one of them
    # in order to ensure that both maps have the same encounters
    route_21_randomized = False

    placed_species = set()

    map_names = list(world.modified_maps.keys())
    world.random.shuffle(map_names)
    for map_name in map_names:
        map_data = world.modified_maps[map_name]

        new_encounter_slots: List[List[int]] = [None, None, None]
        old_encounters = [map_data.land_encounters,
                          map_data.water_encounters,
                          map_data.fishing_encounters]

        # Check if the current map is a Route 21 map and the other one has already been randomized.
        # If so, set the encounters of the current map based on teh other Route 21 map.
        if map_name == "MAP_ROUTE21_NORTH" and route_21_randomized:
            map_data.land_encounters.slots[game_version] =\
                world.modified_maps["MAP_ROUTE21_SOUTH"].land_encounters.slots[game_version]
            map_data.water_encounters.slots[game_version] =\
                world.modified_maps["MAP_ROUTE21_SOUTH"].water_encounters.slots[game_version]
            map_data.fishing_encounters.slots[game_version] =\
                world.modified_maps["MAP_ROUTE21_SOUTH"].fishing_encounters.slots[game_version]
            continue
        elif map_name == "MAP_ROUTE21_SOUTH" and route_21_randomized:
            map_data.land_encounters.slots[game_version] =\
                world.modified_maps["MAP_ROUTE21_NORTH"].land_encounters.slots[game_version]
            map_data.water_encounters.slots[game_version] =\
                world.modified_maps["MAP_ROUTE21_NORTH"].water_encounters.slots[game_version]
            map_data.fishing_encounters.slots[game_version] =\
                world.modified_maps["MAP_ROUTE21_NORTH"].fishing_encounters.slots[game_version]
            continue

        if map_name == "MAP_ROUTE21_NORTH" or map_name == "MAP_ROUTE21_SOUTH":
            route_21_randomized = True

        for i, table in enumerate(old_encounters):
            if table is not None:
                # Create a map from the original species to new species
                # instead of just randomizing every slot.
                # Force area 1-to-1 mapping, in other words.
                species_old_to_new_map: Dict[int, int] = {}
                for species_id in table.slots[game_version]:
                    if species_id not in species_old_to_new_map:
                        if (world.options.wild_pokemon_groups == WildPokemonGroups.option_species and
                                species_id in species_map):
                            new_species_id = species_map[species_id]
                        elif (world.options.wild_pokemon_groups == WildPokemonGroups.option_dungeons and
                              map_name in DUNGEON_GROUPS and
                              species_id in dungeon_species_map[DUNGEON_GROUPS[map_name]]):
                            new_species_id = dungeon_species_map[DUNGEON_GROUPS[map_name]][species_id]
                        else:
                            original_species = data.species[species_id]

                            # Construct progressive tiers of blacklists that can be peeled back if they
                            # collectively cover too much of the Pokédex. A lower index in `blacklists`
                            # indicates a more important set of species to avoid. Entries at `0` will
                            # always be blacklisted.
                            blacklists: Dict[int, List[Set[int]]] = defaultdict(list)

                            # Blacklist Pokémon already on this table
                            blacklists[0].append(set(species_old_to_new_map.values()))

                            # If we are randomizing by groups, blacklist any species that is
                            # already a part of this group
                            if world.options.wild_pokemon_groups == WildPokemonGroups.option_species:
                                blacklists[0].append(set(species_map.values()))
                            elif (world.options.wild_pokemon_groups == WildPokemonGroups.option_dungeons and
                                  map_name in DUNGEON_GROUPS):
                                blacklists[0].append(set(dungeon_species_map[DUNGEON_GROUPS[map_name]].values()))

                            # If we haven't placed enough species for Oak's Aides yet, blacklist
                            # species that have already been placed until we reach that number
                            if len(placed_species) < min_pokemon_needed:
                                blacklists[1].append(placed_species)

                            # Type matching blacklist
                            if should_match_type:
                                blacklists[2].append({
                                    species.species_id
                                    for species in world.modified_species.values()
                                    if not bool(set(species.types) & set(original_species.types))
                                })

                            merged_blacklist: Set[int] = set()
                            for max_priority in reversed(sorted(blacklists.keys())):
                                merged_blacklist = set()
                                for priority in blacklists.keys():
                                    if priority <= max_priority:
                                        for blacklist in blacklists[priority]:
                                            merged_blacklist |= blacklist

                                if len(merged_blacklist) < NUM_REAL_SPECIES:
                                    break

                            candidates = [
                                species for species in world.modified_species.values() if
                                species.species_id not in merged_blacklist
                            ]

                            if should_match_bst:
                                candidates = filter_species_by_nearby_bst(candidates, sum(original_species.base_stats))

                            new_species_id = world.random.choice(candidates).species_id

                            if world.options.wild_pokemon_groups == WildPokemonGroups.option_species:
                                species_map[original_species.species_id] = new_species_id
                            elif (world.options.wild_pokemon_groups == WildPokemonGroups.option_dungeons and
                                  map_name in DUNGEON_GROUPS):
                                dungeon_species_map[DUNGEON_GROUPS[map_name]][original_species.species_id] = \
                                    new_species_id

                        species_old_to_new_map[species_id] = new_species_id
                        placed_species.add(new_species_id)

                # Actually create the new list of slots and encounter table
                new_slots: List[int] = []
                for species_id in table.slots[game_version]:
                    new_slots.append(species_old_to_new_map[species_id])

                new_encounter_slots[i] = new_slots

        if map_data.land_encounters is not None:
            map_data.land_encounters.slots[game_version] = new_encounter_slots[0]
        if map_data.water_encounters is not None:
            map_data.water_encounters.slots[game_version] = new_encounter_slots[1]
        if map_data.fishing_encounters is not None:
            map_data.fishing_encounters.slots[game_version] = new_encounter_slots[2]


def randomize_starters(world: "PokemonFRLGWorld") -> None:
    if world.options.starters == RandomizeStarters.option_vanilla:
        return

    should_match_bst = world.options.starters in {
        RandomizeStarters.option_match_base_stats,
        RandomizeStarters.option_match_base_stats_and_type,
    }
    should_match_type = world.options.starters in {
        RandomizeStarters.option_match_type,
        RandomizeStarters.option_match_base_stats_and_type,
    }

    for name, starter in world.modified_starters.items():
        original_starter = data.species[starter.species_id]

        type_blacklist = {
            species.species_id
            for species in world.modified_species.values()
            if not bool(set(species.types) & set(original_starter.types))
        } if should_match_type else set()

        candidates = [
            species
            for species in world.modified_species.values()
            if species.species_id not in type_blacklist
        ]

        if should_match_bst:
            candidates = filter_species_by_nearby_bst(candidates, sum(original_starter.base_stats))

        new_starter = world.random.choice(candidates)
        starter.species_id = new_starter.species_id


def randomize_legendaries(world: "PokemonFRLGWorld") -> None:
    if world.options.legendary_pokemon == RandomizeLegendaryPokemon.option_vanilla:
        return

    game_version = world.options.game_version.current_key

    should_match_bst = world.options.legendary_pokemon in {
        RandomizeLegendaryPokemon.option_match_base_stats,
        RandomizeLegendaryPokemon.option_match_base_stats_and_type
    }
    should_match_type = world.options.legendary_pokemon in {
        RandomizeLegendaryPokemon.option_match_type,
        RandomizeLegendaryPokemon.option_match_base_stats_and_type
    }

    for name, legendary in data.legendary_pokemon.items():
        original_species = world.modified_species[legendary.species_id[game_version]]

        candidates = list(world.modified_species.values())
        if should_match_type:
            candidates = [
                species
                for species in candidates
                if bool(set(species.types) & set(original_species.types))
            ]
        if should_match_bst:
            candidates = filter_species_by_nearby_bst(candidates, sum(original_species.base_stats))

        world.modified_legendary_pokemon[name].species_id[game_version] = world.random.choice(candidates).species_id


def randomize_misc_pokemon(world: "PokemonFRLGWorld") -> None:
    if world.options.misc_pokemon == RandomizeMiscPokemon.option_vanilla:
        return

    game_version = world.options.game_version.current_key

    should_match_bst = world.options.legendary_pokemon in {
        RandomizeLegendaryPokemon.option_match_base_stats,
        RandomizeLegendaryPokemon.option_match_base_stats_and_type
    }
    should_match_type = world.options.legendary_pokemon in {
        RandomizeLegendaryPokemon.option_match_type,
        RandomizeLegendaryPokemon.option_match_base_stats_and_type
    }

    for name, misc_pokemon in data.misc_pokemon.items():
        original_species = world.modified_species[misc_pokemon.species_id[game_version]]

        candidates = list(world.modified_species.values())
        if should_match_type:
            candidates = [
                species
                for species in candidates
                if bool(set(species.types) & set(original_species.types))
            ]
        if should_match_bst:
            candidates = filter_species_by_nearby_bst(candidates, sum(original_species.base_stats))

        world.modified_misc_pokemon[name].species_id[game_version] = world.random.choice(candidates).species_id

    # Update the events that correspond to the misc Pokémon
    for name, misc_pokemon in world.modified_misc_pokemon.items():
        if name not in world.modified_events:
            continue

        species = world.modified_species[misc_pokemon.species_id[game_version]]
        item = f'{species.name}' if name in NON_STATIC_MISC_POKEMON else f'Static {species.name}'

        new_event = EventData(
            world.modified_events[name].id,
            world.modified_events[name].name,
            item,
            world.modified_events[name].parent_region_id
        )

        world.modified_events[name] = new_event
