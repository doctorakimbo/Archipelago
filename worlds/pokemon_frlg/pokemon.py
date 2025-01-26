import copy
import math
from typing import TYPE_CHECKING, Dict, List, Set, Tuple

from .data import (data, LEGENDARY_POKEMON, NUM_REAL_SPECIES, EncounterSpeciesData, EventData, LearnsetMove,
                   SpeciesData, TrainerPokemonData)
from .options import (HmCompatibility, RandomizeAbilities, RandomizeLegendaryPokemon, RandomizeMiscPokemon,
                      RandomizeMoves, RandomizeStarters, RandomizeTrainerParties, RandomizeTypes, RandomizeWildPokemon,
                      TmTutorCompatibility, WildPokemonGroups)
from .util import bool_array_to_int, int_to_bool_array

if TYPE_CHECKING:
    from random import Random
    from . import PokemonVegaWorld

_DAMAGING_MOVES = frozenset({
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 13, 16, 17, 20, 21, 22, 23, 24, 25,
    26, 27, 29, 30, 31, 33, 34, 35, 36, 37,
    38, 40, 41, 42, 44, 49, 51, 52, 53, 55,
    56, 58, 59, 60, 61, 62, 63, 64, 65, 66,
    67, 69, 71, 72, 75, 76, 80, 82, 83, 84,
    85, 87, 88, 89, 91, 93, 94, 98, 99, 101,
    121, 122, 123, 124, 125, 126, 128, 129, 130, 131,
    132, 136, 140, 141, 143, 145, 146, 149, 152, 154,
    155, 157, 158, 161, 162, 163, 167, 168, 172, 175,
    177, 179, 181, 183, 185, 188, 189, 190, 192, 196,
    198, 200, 202, 205, 209, 210, 211, 216, 217, 218,
    221, 222, 223, 224, 225, 228, 229, 231, 232, 233,
    237, 238, 239, 242, 245, 246, 247, 248, 250, 251,
    253, 257, 263, 265, 267, 276, 279, 280, 282, 284,
    290, 292, 295, 296, 299, 301, 302, 304, 305, 306,
    307, 308, 309, 310, 311, 314, 315, 317, 318, 323,
    324, 325, 326, 327, 328, 330, 331, 332, 333, 337,
    338, 340, 341, 342, 343, 344, 345, 348, 350, 351,
    352, 353, 354, 355, 356, 357, 358, 359, 360, 361,
    362, 363, 364, 365, 366, 368, 369, 370, 371, 372,
    373, 374, 375, 376, 377, 378, 379, 380, 381, 382,
    383, 384, 386, 387, 388, 389, 390, 391, 392, 393,
    394, 395, 396, 397, 398, 399, 400, 401, 402, 403,
    404, 405, 406, 407, 408, 409, 410, 411, 412, 415,
    416, 417, 418, 420, 421, 422, 423, 424, 425, 426,
    427, 428, 431, 432, 433, 434, 435, 436, 437, 438,
    439, 441, 442, 443, 444, 446, 447, 448, 449, 450,
    451, 452, 453, 454, 455, 456, 457, 458, 459, 460,
    461, 462, 463, 464, 465, 466, 467, 468, 469, 470,
    471, 473, 474, 475, 476, 477, 479, 480, 481, 482,
    485, 486, 487, 488, 489, 491, 493, 494, 495, 496,
    499, 501, 502, 503, 505, 506, 507, 508, 509, 510
})

_HM_MOVES = frozenset({
    15, 19, 57, 70, 127, 148, 249, 291
})

_MOVE_BLACKLIST = frozenset({
    0, 165
})

_DUNGEON_GROUPS: Dict[str, str] = {
    "MAP_WISEMANS_CAVE_B1F": "MAP_WISEMANS_CAVE",
    "MAP_WISEMANS_CAVE_B2F": "MAP_WISEMANS_CAVE",
    "MAP_SPIRIT_MANSION_1F": "MAP_SPIRIT_MANSION",
    "MAP_SPIRIT_MANSION_2F": "MAP_SPIRIT_MANSION",
    "MAP_SPIRIT_MANSION_B1F": "MAP_SPIRIT_MANSION",
    "MAP_UNDERSEA_TUNNEL_1F": "MAP_UNDERSEA_TUNNEL",
    "MAP_UNDERSEA_TUNNEL_B1F": "MAP_UNDERSEA_TUNNEL",
    "MAP_UNDERSEA_TUNNEL_B2F": "MAP_UNDERSEA_TUNNEL",
    "MAP_UNDERSEA_TUNNEL_B3F": "MAP_UNDERSEA_TUNNEL",
    "MAP_DH_BUILDING_AFTER_TELEPORT": "MAP_DH_BUILDING",
    "MAP_DH_BUILDING_B1F": "MAP_DH_BUILDING",
    "MAP_DH_BUILDING_DILFORD_CHAMBER": "MAP_DH_BUILDING",
    "MAP_DH_BUILDING_LIPTOO_CHAMBER": "MAP_DH_BUILDING",
    "MAP_DH_BUILDING_MONEAN_CHAMBER": "MAP_DH_BUILDING",
    "MAP_DH_BUILDING_RIXY_CHAMBER": "MAP_DH_BUILDING",
    "MAP_DH_BUILDING_SCUFIB_CHAMBER": "MAP_DH_BUILDING",
    "MAP_DH_BUILDING_VIAPOIS_CHAMBER": "MAP_DH_BUILDING",
    "MAP_DH_BUILDING_WEEPTH_CHAMBER": "MAP_DH_BUILDING",
    "MAP_SAFARI_ZONE_CENTER": "MAP_SAFARI_ZONE",
    "MAP_SAFARI_ZONE_EAST": "MAP_SAFARI_ZONE",
    "MAP_SAFARI_ZONE_NORTH": "MAP_SAFARI_ZONE",
    "MAP_SAFARI_ZONE_WEST": "MAP_SAFARI_ZONE",
    "MAP_TOWER_OF_DARKNESS_B1F": "MAP_TOWER_OF_DARKNESS",
    "MAP_TOWER_OF_DARKNESS_B2F": "MAP_TOWER_OF_DARKNESS",
    "MAP_PORCELIA_FOREST_EAST": "MAP_PORCELIA_FOREST",
    "MAP_PORCELIA_FOREST_WEST": "MAP_PORCELIA_FOREST",
    "MAP_CHATEAU_OF_TIME_1F_ENTRANCE": "MAP_CHATEAU_OF_TIME",
    "MAP_CHATEAU_OF_TIME_1F_TUNNELS": "MAP_CHATEAU_OF_TIME",
    "MAP_CHATEAU_OF_TIME_2F_1R": "MAP_CHATEAU_OF_TIME",
    "MAP_CHATEAU_OF_TIME_2F_2R": "MAP_CHATEAU_OF_TIME",
    "MAP_CHATEAU_OF_TIME_2F_DUSKNOIR_ROOM": "MAP_CHATEAU_OF_TIME",
    "MAP_CHATEAU_OF_TIME_2F_LEGENDARIES_ROOM": "MAP_CHATEAU_OF_TIME",
    "MAP_CHATEAU_OF_TIME_3F": "MAP_CHATEAU_OF_TIME",
    "MAP_CHATEAU_OF_TIME_B1F_MAZE": "MAP_CHATEAU_OF_TIME",
    "MAP_CHATEAU_OF_TIME_B1F_SOUTH_OF_MAZE": "MAP_CHATEAU_OF_TIME",
    "MAP_CHATEAU_OF_TIME_B1F_STAIRS_ROOM": "MAP_CHATEAU_OF_TIME",
    "MAP_CHATEAU_OF_TIME_B2F": "MAP_CHATEAU_OF_TIME",
    "MAP_MT_SNOWFALL_1F": "MAP_MT_SNOWFALL",
    "MAP_MT_SNOWFALL_2F": "MAP_MT_SNOWFALL",
    "MAP_MT_SNOWFALL_3F_EAST": "MAP_MT_SNOWFALL",
    "MAP_MT_SNOWFALL_3F_WEST": "MAP_MT_SNOWFALL",
    "MAP_MT_SNOWFALL_B1F": "MAP_MT_SNOWFALL",
    "MAP_MT_SNOWFALL_B2F": "MAP_MT_SNOWFALL",
    "MAP_DH_HIDEOUT_B5F": "MAP_DH_HIDEOUT",
    "MAP_DH_HIDEOUT_B6F": "MAP_DH_HIDEOUT",
    "MAP_DH_HIDEOUT_B7F": "MAP_DH_HIDEOUT",
    "MAP_ICE_ISLAND_1F": "MAP_ICE_ISLAND",
    "MAP_ICE_ISLAND_B1F": "MAP_ICE_ISLAND",
    "MAP_ICE_ISLAND_B2F": "MAP_ICE_ISLAND",
    "MAP_ICE_ISLAND_B3F": "MAP_ICE_ISLAND",
    "MAP_ICE_ISLAND_B4F_APRIL_ROOM": "MAP_ICE_ISLAND",
    "MAP_ICE_ISLAND_B4F_GORDON_ROOM": "MAP_ICE_ISLAND",
    "MAP_LIGHTNING_ISLAND_B1F": "MAP_LIGHTNING_ISLAND",
    "MAP_LIGHTNING_ISLAND_B2F": "MAP_LIGHTNING_ISLAND",
    "MAP_LIGHTNING_ISLAND_B3F": "MAP_LIGHTNING_ISLAND",
    "MAP_LIGHTNING_ISLAND_B4F": "MAP_LIGHTNING_ISLAND",
    "MAP_LIGHTNING_ISLAND_ENTRANCE": "MAP_LIGHTNING_ISLAND",
    "MAP_FIRE_ISLAND_B1F": "MAP_FIRE_ISLAND",
    "MAP_FIRE_ISLAND_B2F": "MAP_FIRE_ISLAND",
    "MAP_FIRE_ISLAND_B3F": "MAP_FIRE_ISLAND",
    "MAP_FIRE_ISLAND_B4F": "MAP_FIRE_ISLAND",
    "MAP_FIRE_ISLAND_ENTRANCE": "MAP_FIRE_ISLAND",
    "MAP_POKEMON_CASTLE_4F": "MAP_POKEMON_CASTLE",
    "MAP_POKEMON_CASTLE_5F": "MAP_POKEMON_CASTLE",
    "MAP_POKEMON_CASTLE_6F": "MAP_POKEMON_CASTLE",
    "MAP_POKEMON_CASTLE_7F": "MAP_POKEMON_CASTLE",
    "MAP_POKEMON_CASTLE_8F": "MAP_POKEMON_CASTLE",
    "MAP_VICTORY_ROAD_1F": "MAP_VICTORY_ROAD",
    "MAP_VICTORY_ROAD_B1F": "MAP_VICTORY_ROAD",
    "MAP_VICTORY_ROAD_B2F": "MAP_VICTORY_ROAD",
    "MAP_VICTORY_ROAD_B3F": "MAP_VICTORY_ROAD",
    "MAP_VICTORY_ROAD_B4F": "MAP_VICTORY_ROAD",
    "MAP_VICTORY_ROAD_B5F": "MAP_VICTORY_ROAD",
    "MAP_VICTORY_ROAD_B6F": "MAP_VICTORY_ROAD",
    "MAP_SPHERE_RUINS_1F": "MAP_SPHERE_RUINS",
    "MAP_SPHERE_RUINS_B1F": "MAP_SPHERE_RUINS",
    "MAP_SPHERE_RUINS_B2F": "MAP_SPHERE_RUINS",
    "MAP_SPHERE_RUINS_B3F": "MAP_SPHERE_RUINS",
    "MAP_SPHERE_RUINS_B4F": "MAP_SPHERE_RUINS",
    "MAP_SPHERE_RUINS_B5F": "MAP_SPHERE_RUINS",
    "MAP_SPHERE_RUINS_B6F": "MAP_SPHERE_RUINS",
    "MAP_SPHERE_RUINS_B7F": "MAP_SPHERE_RUINS",
    "MAP_SPHERE_RUINS_B8F": "MAP_SPHERE_RUINS",
    "MAP_SPHERE_RUINS_B9F": "MAP_SPHERE_RUINS"
}

STARTER_INDEX: Dict[str, int] = {
    "STARTER_POKEMON_NIMBLEAF": 0,
    "STARTER_POKEMON_LIQUIPUT": 1,
    "STARTER_POKEMON_PEYERO": 2,
}

# The tuple represnts (trainer name, starter index in party, starter evolution stage)
_RIVAL_STARTER_POKEMON: List[Tuple[str, int, int]] = [
    [
        ("TRAINER_RIVAL_HOLLYS_LAB_NIMBLEAF", 0, 0),
        ("TRAINER_RIVAL_SEAFIN_NIMBLEAF", 1, 0),
        ("TRAINER_MOS_RANGER_SQUAD_NIMBLEAF", 3, 1),
        ("TRAINER_RIVAL_ORPIMENCE_NIMBLEAF", 2, 2),
        ("TRAINER_RIVAL_RAVENPLUME_NIMBLEAF", 3, 2),
        ("TRAINER_RIVAL_VICTORY_ROAD_NIMBLEAF", 4, 2),
    ],
    [
        ("TRAINER_RIVAL_HOLLYS_LAB_PEYERO", 0, 0),
        ("TRAINER_RIVAL_SEAFIN_PEYERO", 1, 0),
        ("TRAINER_MOS_RANGER_SQUAD_PEYERO", 3, 1),
        ("TRAINER_RIVAL_ORPIMENCE_PEYERO", 2, 2),
        ("TRAINER_RIVAL_RAVENPLUME_PEYERO", 3, 2),
        ("TRAINER_RIVAL_VICTORY_ROAD_PEYERO", 4, 2),
    ],
    [
        ("TRAINER_RIVAL_HOLLYS_LAB_LIQUIPUT", 0, 0),
        ("TRAINER_RIVAL_SEAFIN_LIQUIPUT", 1, 0),
        ("TRAINER_MOS_RANGER_SQUAD_LIQUIPUT", 3, 1),
        ("TRAINER_RIVAL_ORPIMENCE_LIQUIPUT", 2, 2),
        ("TRAINER_RIVAL_RAVENPLUME_LIQUIPUT", 3, 2),
        ("TRAINER_RIVAL_VICTORY_ROAD_LIQUIPUT", 4, 2),
    ]
]


def _get_random_type(random: "Random") -> int:
    picked_type = random.randrange(0, 18)
    while picked_type == 9:  # Don't pick the ??? type
        picked_type = random.randrange(0, 18)

    return picked_type


def _get_random_move(random: "Random", blacklist: Set[int]) -> int:
    extended_blacklist = _HM_MOVES | _MOVE_BLACKLIST | blacklist
    allowed_moves = [i for i in range(data.constants["MOVES_COUNT"]) if i not in extended_blacklist]
    return random.choice(allowed_moves)


def _get_random_damaging_move(random: "Random", blacklist: Set[int]) -> int:
    allowed_moves = [i for i in list(_DAMAGING_MOVES) if i not in blacklist]
    return random.choice(allowed_moves)


def _filter_species_by_nearby_bst(species: List[SpeciesData], target_bst: int) -> List[SpeciesData]:
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


def _get_trainer_pokemon_moves(world: "PokemonVegaWorld",
                               species: SpeciesData,
                               pokemon: TrainerPokemonData) -> Tuple[int, int, int, int]:
    if species.species_id not in world.per_species_tmhm_moves:
        world.per_species_tmhm_moves[species.species_id] = sorted({
            world.modified_tmhm_moves[i]
            for i, is_compatible in enumerate(int_to_bool_array(species.tm_hm_compatibility))
            if is_compatible
        })

    # TMs and HMs compatible with the species
    tm_hm_movepool = world.per_species_tmhm_moves[species.species_id]

    # Moves the Pokémon could have learned by now
    level_up_movepool = sorted({
        move.move_id
        for move in species.learnset
        if move.move_id != 0 and move.level <= pokemon.level
    })

    if len(level_up_movepool) < 4:
        level_up_moves = [level_up_movepool[i]
                          if i < len(level_up_movepool) else 0 for i in range(4)]
    else:
        level_up_moves = world.random.sample(level_up_movepool, 4)

    if len(tm_hm_movepool) < 4:
        tm_hm_moves = list(reversed(list(tm_hm_movepool[i]
                                         if i < len(tm_hm_movepool) else 0 for i in range(4))))
    else:
        tm_hm_moves = world.random.sample(tm_hm_movepool, 4)

    # 25% chance to pick a move from TMs or HMs
    new_moves = (
        tm_hm_moves[0] if world.random.random() < 0.25 and tm_hm_moves[0] != 0 else level_up_moves[0],
        tm_hm_moves[1] if world.random.random() < 0.25 and tm_hm_moves[0] != 0 else level_up_moves[1],
        tm_hm_moves[2] if world.random.random() < 0.25 and tm_hm_moves[0] != 0 else level_up_moves[2],
        tm_hm_moves[3] if world.random.random() < 0.25 and tm_hm_moves[0] != 0 else level_up_moves[3]
    )

    return new_moves


def randomize_types(world: "PokemonVegaWorld") -> None:
    if world.options.types == RandomizeTypes.option_shuffle:
        type_map = list(range(18))
        world.random.shuffle(type_map)

        # Map the ??? type to itself. No Pokémon have this type, and we don't want any Pokémon to have it.
        mystery_type_index = type_map.index(9)
        type_map[mystery_type_index], type_map[9] = type_map[9], type_map[mystery_type_index]

        for species in world.modified_species.values():
            species.types = (type_map[species.types[0]], type_map[species.types[1]])
    elif world.options.types == RandomizeTypes.option_completely_random:
        for species in world.modified_species.values():
            new_type_1 = _get_random_type(world.random)
            new_type_2 = new_type_1

            if species.types[0] != species.types[1]:
                while new_type_1 == new_type_2:
                    new_type_2 = _get_random_type(world.random)

            species.types = (new_type_1, new_type_2)
    elif world.options.types == RandomizeTypes.option_follow_evolutions:
        already_randomized = set()

        for species in world.modified_species.values():
            if species.species_id in already_randomized:
                continue
            elif species.pre_evolution is not None:
                continue

            type_map = list(range(18))
            world.random.shuffle(type_map)

            # Map the ??? type to itself. No Pokémon have this type, and we don't want any Pokémon to have it.
            mystery_type_index = type_map.index(9)
            type_map[mystery_type_index], type_map[9] = type_map[9], type_map[mystery_type_index]

            evolutions = [species]
            while len(evolutions) > 0:
                evolution = evolutions.pop()
                evolution.types = (type_map[evolution.types[0]], type_map[evolution.types[1]])
                already_randomized.add(evolution.species_id)
                evolutions += [world.modified_species[evo.species_id] for evo in evolution.evolutions]


def randomize_abilities(world: "PokemonVegaWorld") -> None:
    if world.options.abilities == RandomizeAbilities.option_vanilla:
        return

    allowed_abilities = list(range(data.constants["ABILITIES_COUNT"]))
    allowed_abilities.remove(data.constants["ABILITY_NONE"])
    allowed_abilities.remove(data.constants["ABILITY_CACOPHONY"])
    for ability_id in world.blacklisted_abilities:
        allowed_abilities.remove(ability_id)

    if world.options.abilities == RandomizeAbilities.option_follow_evolutions:
        already_randomized = set()

        for species in world.modified_species.values():
            if species.species_id in already_randomized:
                continue
            elif (species.pre_evolution is not None and
                  species.abilities == data.species[species.pre_evolution].abilities):
                continue

            old_abilities = species.abilities
            new_abilities = (
                0 if old_abilities[0] == 0 else world.random.choice(allowed_abilities),
                0 if old_abilities[1] == 0 else world.random.choice(allowed_abilities)
            )

            evolutions = [species]
            while len(evolutions) > 0:
                evolution = evolutions.pop()
                if evolution.abilities == old_abilities:
                    evolution.abilities = new_abilities
                    already_randomized.add(evolution.species_id)
                    evolutions += [world.modified_species[evo.species_id] for evo in evolution.evolutions]
    else:
        for species in world.modified_species.values():
            old_abilities = species.abilities
            new_abilities = (
                0 if old_abilities[0] == 0 else world.random.choice(allowed_abilities),
                0 if old_abilities[1] == 0 else world.random.choice(allowed_abilities)
            )
            species.abilities = new_abilities


def randomize_moves(world: "PokemonVegaWorld") -> None:
    if world.options.moves == RandomizeMoves.option_vanilla:
        return

    for species in world.modified_species.values():
        old_learnset = species.learnset
        new_learnset: List[LearnsetMove] = []

        # All species have 4 moves at level 0. Up to 3 of them can be MOVE_NONE and
        # are used for the start with 4 moves option. We need to either replace them
        # with actual moves or leave them alone depending on the option.
        move_index = 0
        while old_learnset[move_index].move_id == 0:
            if world.options.moves == RandomizeMoves.option_start_with_four_moves:
                new_move = _get_random_move(world.random,
                                            {move.move_id for move in new_learnset} | world.blacklisted_moves)
            else:
                new_move = 0
            new_learnset.append(LearnsetMove(old_learnset[move_index].level, new_move))
            move_index += 1

        while move_index < len(old_learnset):
            if move_index == 3:
                new_move = _get_random_damaging_move(world.random, {move.move_id for move in new_learnset})
            else:
                new_move = _get_random_move(world.random,
                                            {move.move_id for move in new_learnset} | world.blacklisted_moves)
            new_learnset.append(LearnsetMove(old_learnset[move_index].level, new_move))
            move_index += 1

        species.learnset = new_learnset


def randomize_wild_encounters(world: "PokemonVegaWorld") -> None:
    from collections import defaultdict

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

    for map_group in _DUNGEON_GROUPS.values():
        if map_group not in dungeon_species_map:
            dungeon_species_map[map_group] = {}

    placed_species = set()
    priority_species = list()

    map_names = list(world.modified_maps.keys())
    world.random.shuffle(map_names)
    for map_name in map_names:
        placed_priority_species = False
        map_data = world.modified_maps[map_name]

        if map_data.sphere_ruins and world.options.exclude_sphere_ruins:
            continue

        new_encounter_slots: List[List[int]] = [None, None, None]
        old_encounters = [map_data.land_encounters,
                          map_data.water_encounters,
                          map_data.fishing_encounters]

        for i, table in enumerate(old_encounters):
            if table is not None:
                # Create a map from the original species to new species
                # instead of just randomizing every slot.
                # Force area 1-to-1 mapping, in other words.
                species_old_to_new_map: Dict[int, int] = {}
                for species_data in table.slots:
                    species_id = species_data.species_id
                    if species_id not in species_old_to_new_map:
                        original_species = data.species[species_id]
                        if (world.options.wild_pokemon_groups == WildPokemonGroups.option_species and
                                species_id in species_map):
                            new_species_id = species_map[species_id]
                        elif (world.options.wild_pokemon_groups == WildPokemonGroups.option_dungeons and
                              map_name in _DUNGEON_GROUPS and
                              species_id in dungeon_species_map[_DUNGEON_GROUPS[map_name]]):
                            new_species_id = dungeon_species_map[_DUNGEON_GROUPS[map_name]][species_id]
                        else:
                            if not placed_priority_species and len(priority_species) > 0:
                                new_species_id = priority_species.pop()
                                placed_priority_species = True
                            else:
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
                                      map_name in _DUNGEON_GROUPS):
                                    blacklists[0].append(set(dungeon_species_map[_DUNGEON_GROUPS[map_name]].values()))

                                # Blacklist from player's options
                                blacklists[2].append(world.blacklisted_wild_pokemon)

                                # Type matching blacklist
                                if should_match_type:
                                    blacklists[3].append({
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
                                    candidates = _filter_species_by_nearby_bst(candidates, sum(original_species.base_stats))

                                new_species_id = world.random.choice(candidates).species_id

                            if world.options.wild_pokemon_groups == WildPokemonGroups.option_species:
                                species_map[original_species.species_id] = new_species_id
                            elif (world.options.wild_pokemon_groups == WildPokemonGroups.option_dungeons and
                                  map_name in _DUNGEON_GROUPS):
                                dungeon_species_map[_DUNGEON_GROUPS[map_name]][original_species.species_id] = new_species_id

                        species_old_to_new_map[species_id] = new_species_id
                        placed_species.add(new_species_id)

                # Actually create the new list of slots and encounter table
                new_slots: List[EncounterSpeciesData] = []
                for species_data in table.slots:
                    new_slots.append(EncounterSpeciesData(
                        species_old_to_new_map[species_data.species_id],
                        species_data.min_level,
                        species_data.max_level
                    ))

                new_encounter_slots[i] = new_slots

        if map_data.land_encounters is not None:
            map_data.land_encounters.slots = new_encounter_slots[0]
        if map_data.water_encounters is not None:
            map_data.water_encounters.slots = new_encounter_slots[1]
        if map_data.fishing_encounters is not None:
            map_data.fishing_encounters.slots = new_encounter_slots[2]


def randomize_starters(world: "PokemonVegaWorld") -> None:
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

    new_starters: List[SpeciesData] = []

    for name, starter in world.modified_starters.items():
        original_starter = data.species[starter.species_id]

        type_blacklist = {
            species.species_id
            for species in world.modified_species.values()
            if not bool(set(species.types) & set(original_starter.types))
        } if should_match_type else set()

        merged_blacklist = set(s.species_id for s in new_starters) | world.blacklisted_starters | type_blacklist
        if len(merged_blacklist) == NUM_REAL_SPECIES:
            merged_blacklist = set(s.species_id for s in new_starters) | world.blacklisted_starters
        if len(merged_blacklist) == NUM_REAL_SPECIES:
            merged_blacklist = set(s.species_id for s in new_starters)

        candidates = [
            species
            for species in world.modified_species.values()
            if species.species_id not in merged_blacklist
        ]

        if should_match_bst:
            candidates = _filter_species_by_nearby_bst(candidates, sum(original_starter.base_stats))

        new_starter = world.random.choice(candidates)
        starter.species_id = new_starter.species_id
        new_starters.append(new_starter)

    # Change the starter in your rival's party
    for i, starter_data in enumerate(new_starters):
        starter_stages: List[SpeciesData] = [starter_data, None, None]
        if len(starter_stages[0].evolutions) > 0:
            evolution = world.random.choice(starter_stages[0].evolutions)
            starter_stages[1] = world.modified_species[evolution.species_id]
            if len(starter_stages[1].evolutions) > 0:
                evolution = world.random.choice(starter_stages[1].evolutions)
                starter_stages[2] = world.modified_species[evolution.species_id]
            else:
                starter_stages[2] = starter_stages[1]
        else:
            starter_stages[1] = starter_stages[0]
            starter_stages[2] = starter_stages[0]

        for trainer_name, starter_index, evolution_stage in _RIVAL_STARTER_POKEMON[i]:
            trainer_data = world.modified_trainers[trainer_name]
            starter_species = starter_stages[evolution_stage]
            rival_starter = trainer_data.party.pokemon[starter_index]
            new_moves = _get_trainer_pokemon_moves(world, starter_species, rival_starter)
            trainer_data.party.pokemon[starter_index] = TrainerPokemonData(starter_species.species_id,
                                                                           rival_starter.level,
                                                                           new_moves,
                                                                           True)


def randomize_legendaries(world: "PokemonVegaWorld") -> None:
    if world.options.legendary_pokemon == RandomizeLegendaryPokemon.option_vanilla:
        return

    should_match_bst = world.options.legendary_pokemon in {
        RandomizeLegendaryPokemon.option_match_base_stats,
        RandomizeLegendaryPokemon.option_match_base_stats_and_type
    }
    should_match_type = world.options.legendary_pokemon in {
        RandomizeLegendaryPokemon.option_match_type,
        RandomizeLegendaryPokemon.option_match_base_stats_and_type
    }

    placed_species = set()

    for name, legendary in data.legendary_pokemon.items():
        original_species = world.modified_species[legendary.species_id]

        if world.options.legendary_pokemon == RandomizeLegendaryPokemon.option_legendaries:
            candidates = [species for species in world.modified_species.values() if
                          species.species_id in LEGENDARY_POKEMON and species.species_id not in placed_species]
        else:
            candidates = list(world.modified_species.values())
        if should_match_type:
            candidates = [
                species
                for species in candidates
                if bool(set(species.types) & set(original_species.types))
            ]
        if should_match_bst:
            candidates = _filter_species_by_nearby_bst(candidates, sum(original_species.base_stats))

        new_species_id = world.random.choice(candidates).species_id
        world.modified_legendary_pokemon[name].species_id = new_species_id
        placed_species.add(new_species_id)

    # Update the events that correspond to the legendary Pokémon
    for name, legendary_pokemon in world.modified_legendary_pokemon.items():
        if name not in world.modified_events:
            continue

        species = world.modified_species[legendary_pokemon.species_id]
        item_name = data.events[name].item.split()

        if item_name[0] == "Static":
            item = f"Static {species.name}"
        elif item_name[0] == "Missable":
            item = f"Missable {species.name}"
        else:
            item = item_name[0]

        new_event = EventData(
            world.modified_events[name].id,
            world.modified_events[name].name,
            item,
            world.modified_events[name].parent_region_id,
            world.modified_events[name].tags
        )

        world.modified_events[name] = new_event


def randomize_misc_pokemon(world: "PokemonVegaWorld") -> None:
    if world.options.misc_pokemon == RandomizeMiscPokemon.option_vanilla:
        return

    should_match_bst = world.options.misc_pokemon in {
        RandomizeMiscPokemon.option_match_base_stats,
        RandomizeMiscPokemon.option_match_base_stats_and_type
    }
    should_match_type = world.options.misc_pokemon in {
        RandomizeMiscPokemon.option_match_type,
        RandomizeMiscPokemon.option_match_base_stats_and_type
    }

    for name, misc_pokemon in data.misc_pokemon.items():
        original_species = world.modified_species[misc_pokemon.species_id]

        candidates = list(world.modified_species.values())
        if should_match_type:
            candidates = [
                species
                for species in candidates
                if bool(set(species.types) & set(original_species.types))
            ]
        if should_match_bst:
            candidates = _filter_species_by_nearby_bst(candidates, sum(original_species.base_stats))

        world.modified_misc_pokemon[name].species_id = world.random.choice(candidates).species_id

    # Update the events that correspond to the misc Pokémon
    for name, misc_pokemon in world.modified_misc_pokemon.items():
        if name not in world.modified_events:
            continue

        species = world.modified_species[misc_pokemon.species_id]

        item_name = data.events[name].item.split()

        if item_name[0] == "Static":
            item = f"Static {species.name}"
        elif item_name[0] == "Missable":
            item = f"Missable {species.name}"
        else:
            item = item_name[0]

        new_event = EventData(
            world.modified_events[name].id,
            world.modified_events[name].name,
            item,
            world.modified_events[name].parent_region_id,
            world.modified_events[name].tags
        )

        world.modified_events[name] = new_event


def randomize_trainer_parties(world: "PokemonVegaWorld") -> None:
    if world.options.trainers == RandomizeTrainerParties.option_vanilla:
        return

    should_match_bst = world.options.trainers in {
        RandomizeTrainerParties.option_match_base_stats,
        RandomizeTrainerParties.option_match_base_stats_and_type,
    }
    should_match_type = world.options.trainers in {
        RandomizeTrainerParties.option_match_type,
        RandomizeTrainerParties.option_match_base_stats_and_type,
    }

    for trainer_id, trainer in world.modified_trainers.items():
        for i, pokemon in enumerate(trainer.party.pokemon):
            if not pokemon.locked:
                original_species = data.species[pokemon.species_id]

                type_blacklist = {
                    species.species_id
                    for species in world.modified_species.values()
                    if not bool(set(species.types) & set(original_species.types))
                } if should_match_type else set()

                merged_blacklist = world.blacklisted_trainer_pokemon | type_blacklist
                if len(merged_blacklist) == NUM_REAL_SPECIES:
                    merged_blacklist = world.blacklisted_trainer_pokemon
                if len(merged_blacklist) == NUM_REAL_SPECIES:
                    merged_blacklist = set()

                candidates = [
                    species
                    for species in world.modified_species.values()
                    if species.species_id not in merged_blacklist
                ]

                if should_match_bst:
                    candidates = _filter_species_by_nearby_bst(candidates, sum(original_species.base_stats))

                new_species = world.random.choice(candidates)

                new_moves = _get_trainer_pokemon_moves(world, new_species, pokemon)
                trainer.party.pokemon[i] = TrainerPokemonData(new_species.species_id,
                                                              pokemon.level,
                                                              new_moves,
                                                              False)


def randomize_tm_hm_compatibility(world: "PokemonVegaWorld") -> None:
    for species in world.modified_species.values():
        compatibility_array = int_to_bool_array(species.tm_hm_compatibility)

        if world.options.tm_tutor_compatibility != TmTutorCompatibility.special_range_names["vanilla"]:
            for i in range(0, 50):
                compatibility_array[i] = world.random.random() < world.options.tm_tutor_compatibility / 100

        if world.options.hm_compatibility != HmCompatibility.special_range_names["vanilla"]:
            for i in range(50, 58):
                compatibility_array[i] = world.random.random() < world.options.hm_compatibility / 100

        species.tm_hm_compatibility = bool_array_to_int(compatibility_array)


def randomize_tm_moves(world: "PokemonVegaWorld") -> None:
    if not world.options.tm_tutor_moves:
        return

    new_moves: Set[int] = set()

    for i in range(50):
        new_move = _get_random_move(world.random, new_moves | world.blacklisted_moves)
        new_moves.add(new_move)
        world.modified_tmhm_moves[i] = new_move


def randomize_tutor_moves(world: "PokemonVegaWorld") -> List[int]:
    new_moves = []

    for i in range(15):
        new_move = _get_random_move(world.random, set(new_moves) | world.blacklisted_moves)
        new_moves.append(new_move)

    return new_moves
