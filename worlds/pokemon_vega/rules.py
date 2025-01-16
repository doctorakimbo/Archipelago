"""
Logic rule definitions for Pokémon Vega
"""
import math
from typing import TYPE_CHECKING, Dict, List
from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule
from .data import data
from .options import (CeruleanCaveRequirement, EliteFourRequirement, FlashRequired, Goal,
                      ItemfinderRequired, LevelScaling, JunopsisCityRoadblock, ShuffleHiddenItems)

if TYPE_CHECKING:
    from . import PokemonVegaWorld


def set_rules(world: "PokemonVegaWorld") -> None:
    player = world.player
    options = world.options
    multiworld = world.multiworld

    badge_requirements: Dict[str, str] = {
        "Cut": "Gemma Badge",
        "Fly": "Hadar Badge",
        "Surf": "Phact Badge",
        "Strength": "Arneb Badge",
        "Flash": "Elnath Badge",
        "Rock Smash": "Sarfah Badge",
        "Waterfall": "Prior Badge"
    }

    # todo: vega
    rematchable_trainer_regions: List[str] = [
        "Route 3", "Route 4 Northeast", "Route 6", "Route 8", "Route 9", "Route 10 North", "Route 10 South",
        "Route 10 Near Power Plant", "Route 11 West", "Route 12 Center", "Route 12 South", "Route 12 Behind North Tree",
        "Route 13", "Route 14", "Route 15 South", "Route 15 North", "Route 16 Northeast", "Route 16 Southwest",
        "Route 17", "Route 18 East", "Route 19", "Route 19 Water", "Route 20 East", "Route 20 Near South Cave",
        "Route 20 West", "Route 21", "Route 24", "Route 25"
    ]

    def has_badge_requirement(hm: str, state: CollectionState):
        return hm in options.remove_badge_requirement.value or state.has(badge_requirements[hm], player)

    def can_reach_any_region(regions: List[str], state: CollectionState):
        return any([state.can_reach_region(region, player) for region in regions])

    def can_cut(state: CollectionState):
        return (state.has("HM01 Cut", player)
                and has_badge_requirement("Cut", state)
                and can_use_hm(state, "Cut"))

    def can_fly(state: CollectionState):
        return (state.has("HM02 Fly", player)
                and has_badge_requirement("Fly", state)
                and can_use_hm(state, "Fly"))

    def can_surf(state: CollectionState):
        return (state.has("HM03 Surf", player)
                and has_badge_requirement("Surf", state)
                and can_use_hm(state, "Surf"))

    def can_strength(state: CollectionState):
        return (state.has("HM04 Strength", player)
                and has_badge_requirement("Strength", state)
                and can_use_hm(state, "Strength"))

    def can_flash(state: CollectionState):
        return (state.has("HM05 Flash", player)
                and has_badge_requirement("Flash", state)
                and can_use_hm(state, "Flash"))

    def can_rock_smash(state: CollectionState):
        return (state.has("HM06 Rock Smash", player)
                and has_badge_requirement("Rock Smash", state)
                and can_use_hm(state, "Rock Smash"))

    def can_waterfall(state: CollectionState):
        return (state.has("HM07 Waterfall", player)
                and has_badge_requirement("Waterfall", state)
                and can_use_hm(state, "Waterfall"))

    def can_use_hm(state: CollectionState, hm: str):
        species_can_use_hm: List[str] = world.hm_compatibility[hm]
        return state.has_any(species_can_use_hm, player)

    def has_n_badges(state: CollectionState, n: int):
        return sum([state.has(badge, player) for badge in [
            "Elnath Badge",
            "Arneb Badge",
            "Phact Badge",
            "Sarfah Badge",
            "Gemma Badge",
            "Hadar Badge",
            "Prior Badge",
            "Mirach Badge"
        ]]) >= n

    def has_n_gyms(state: CollectionState, n: int):
        return sum([state.has(gym, player) for gym in [
            "Defeat Annette",
            "Defeat Geoff",
            "Defeat Brooke",
            "Defeat Avery",
            "Defeat Chie and Rito",
            "Defeat Fenton",
            "Defeat Tara",
            "Defeat Mewtwo"
        ]]) >= n

    def gyms_beaten(state: CollectionState):
        return sum([state.has(gym, player) for gym in [
            "Defeat Annette",
            "Defeat Geoff",
            "Defeat Brooke",
            "Defeat Avery",
            "Defeat Chie & Rito",
            "Defeat Fenton",
            "Defeat Tara",
            "Defeat Mewtwo"
        ]])

    def has_n_pokemon(state: CollectionState, n: int):
        count = 0
        for species in data.species.values():
            if state.has(species.name, player):
                count += 1
            elif state.has(f'Static {species.name}', player):
                count += 1
            if count >= n:
                return True
        return False

    def can_pass_junopsis_city_roadblock(state: CollectionState):
        requirement = options.junopsis_city_roadblock
        if requirement == JunopsisCityRoadblock.option_annette:
            return state.has("Defeat Annette", player)
        elif requirement == JunopsisCityRoadblock.option_any_gym:
            return has_n_gyms(state, 1)
        elif requirement == JunopsisCityRoadblock.option_elnath_badge:
            return state.has("Elnath Badge", player)
        elif requirement == JunopsisCityRoadblock.option_any_badge:
            return has_n_badges(state, 1)
        return True

    def can_pass_cerulean_city_roadblocks(state: CollectionState):
        if "Remove Cerulean Roadblocks" in options.modify_world_state.value:
            return True
        return state.has("Save Bill", player)

    def can_enter_cerulean_cave(state: CollectionState):
        requirement = options.cerulean_cave_requirement
        count = options.cerulean_cave_count.value
        if requirement == CeruleanCaveRequirement.option_vanilla:
            return state.has_all(["Defeat Champion", "Restore Pokemon Network Machine"], player)
        elif requirement == CeruleanCaveRequirement.option_champion:
            return state.has("Defeat Champion", player)
        elif requirement == CeruleanCaveRequirement.option_restore_network:
            return state.has("Restore Pokemon Network Machine", player)
        elif requirement == CeruleanCaveRequirement.option_badges:
            return has_n_badges(state, count)
        elif requirement == CeruleanCaveRequirement.option_gyms:
            return has_n_gyms(state, count)

    def dark_cave(state: CollectionState):
        if options.flash_required != FlashRequired.option_off:
            return can_flash(state)
        return True

    def can_pass_route_523_guard(state: CollectionState):
        requirement = options.route523_guard_requirement
        count = options.route523_guard_count.value
        if requirement == Route523GuardRequirement.option_badges:
            return has_n_badges(state, count)
        elif requirement == Route523GuardRequirement.option_gyms:
            return has_n_gyms(state, count)

    def can_challenge_elite_four(state: CollectionState):
        requirement = options.elite_four_requirement
        count = options.elite_four_count.value
        if requirement == EliteFourRequirement.option_badges:
            return has_n_badges(state, count)
        elif requirement == EliteFourRequirement.option_gyms:
            return has_n_gyms(state, count)

    def evolve_level(state: CollectionState, level: int):
        return gyms_beaten(state) >= level / 7

    def can_grind_money(state: CollectionState):
        return ((state.has("Vs. Seeker", player) and can_reach_any_region(rematchable_trainer_regions, state)) or
                state.has_all(["Defeat Champion", "Restore Pokemon Network Machine"], player))

    def can_open_silph_door(floor: int, state: CollectionState):
        return (state.has_any(["Card Key", f"Card Key {floor}F"], player) or
                state.has("Progressive Card Key", player, floor - 1))

    def post_game_gossipers(state: CollectionState):
        if "Early Gossipers" in options.modify_world_state.value:
            return True
        return state.has("Defeat Champion", player)

    def get_entrance(entrance: str):
        return multiworld.get_entrance(entrance, player)

    def get_location(location: str):
        return multiworld.get_location(location, player)

    # TODO: Actually set up states for Sphere Ruins entry and Asphere defeat
    if options.goal == Goal.option_elite_four:
        multiworld.completion_condition[player] = lambda state: state.has("Defeat Champion", player)
    elif options.goal == Goal.option_distant_island:
        multiworld.completion_condition[player] = lambda state: state.has("Enter Sphere Ruins", player)
    elif options.goal == Goal.option_asphere:
        multiworld.completion_condition[player] = lambda state: state.has("Defeat Asphere", player)

    # Sky
    set_rule(get_entrance("Flying"), lambda state: can_fly(state))
    set_rule(get_entrance("Porcelia Town Fly Destination"), lambda state: state.has("Fly Porcelia Town", player))
    set_rule(get_entrance("Junopsis City Fly Destination"), lambda state: state.has("Fly Junopsis City", player))
    set_rule(get_entrance("Seafin City Fly Destination"), lambda state: state.has("Fly Seafin City", player))
    set_rule(get_entrance("Gamboge City Fly Destination"), lambda state: state.has("Fly Gamboge City", player))
    set_rule(get_entrance("Shamouti Island Fly Destination"), lambda state: state.has("Fly Shamouti Island", player))
    set_rule(get_entrance("Nephrite City Fly Destination"), lambda state: state.has("Fly Nephrite City", player))
    set_rule(get_entrance("Orpimence City Fly Destination"), lambda state: state.has("Fly Orpimence City", player))
    set_rule(get_entrance("Ravenplume City Fly Destination"), lambda state: state.has("Fly Ravenplume City", player))
    set_rule(get_entrance("Lapizula City Fly Destination"), lambda state: state.has("Fly Lapizula City", player))
    set_rule(get_entrance("Route 510 Fly Destination"), lambda state: state.has("Fly Route 510", player))
    set_rule(get_entrance("New Island Fly Destination"), lambda state: state.has("Fly New Island", player))
    set_rule(get_entrance("Shakudo Island Fly Destination"), lambda state: state.has("Fly Shakudo Island", player))

    # Porcelia Town
    set_rule(get_location("Professor Holly's Lab - Postgame Gift from Aide"), lambda state: state.has("Defeat Champion", player))
    set_rule(get_entrance("Porcelia Town Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Porcelia Town Exit (South)"), lambda state: can_rock_smash(state))
    set_rule(get_entrance("Porcelia Town Exit (North)"), lambda state: can_cut(state))
    set_rule(get_entrance("Porcelia Town Warp Flowers"), lambda state: state.has("Distant Island Unlock", player)) # todo: call function instead
    
    # Route 502
    set_rule(get_entrance("Route 502 Exit (North)"), lambda state: can_cut(state))
    set_rule(get_location("Route 502 Gatehouse 2F - School Kid Vivian Reward"), lambda state: state.has("Talk to Girl Blocking Junopsis Gym", player))
    set_rule(get_location("Route 502 Gatehouse 2F - Youngster Vincent Reward"), lambda state: state.has("Talk to Girl Blocking Junopsis Gym", player))
    set_rule(get_location("Route 502 Gatehouse 2F - Lass Violet Reward"), lambda state: state.has("Talk to Girl Blocking Junopsis Gym", player))
    set_rule(get_location("Route 502 Gatehouse 2F - School Kid Vivian Rematch Reward"), 
             lambda state: state.has("Talk to Girl Blocking Junopsis Gym", player) and state.has("Defeat Champion", player))
    set_rule(get_location("Route 502 Gatehouse 2F - School Kid Vincent Rematch Reward"), 
             lambda state: state.has("Talk to Girl Blocking Junopsis Gym", player) and state.has("Defeat Champion", player))
    set_rule(get_location("Route 502 Gatehouse 2F - School Kid Violet Rematch Reward"), 
             lambda state: state.has("Talk to Girl Blocking Junopsis Gym", player) and state.has("Defeat Champion", player))
    set_rule(get_location("Route 502 Gatehouse 2F - Postgame Gift from Violet"), 
             lambda state: state.has("Talk to Girl Blocking Junopsis Gym", player) and state.has("Defeat Champion", player))
    set_rule(get_location("Route 502 Gatehouse 2F - Postgame Gift from Vincent"), 
             lambda state: state.has("Talk to Girl Blocking Junopsis Gym", player) and state.has("Defeat Champion", player))
    set_rule(get_location("Route 502 Gatehouse 2F - Postgame Gift from Vivian"), 
             lambda state: state.has("Talk to Girl Blocking Junopsis Gym", player) and state.has("Defeat Champion", player))

    # Viridian City
    set_rule(get_entrance("Viridian City South Surfing Spot"), lambda state: can_surf(state))

    # Route 22
    set_rule(get_location("Route 22 - Early Rival Battle"), lambda state: state.has("Deliver Oak's Parcel", player))
    set_rule(get_entrance("Route 22 Surfing Spot"), lambda state: can_surf(state))

    # Route 2
    set_rule(get_location("Route 2 Trade House - Trade Abra"), lambda state: state.has("Abra", player))
    set_rule(get_entrance("Route 2 Southwest Cuttable Trees"), lambda state: can_cut(state))
    set_rule(get_entrance("Route 2 East Cuttable Tree"), lambda state: can_cut(state))

    if "Modify Route 2" in options.modify_world_state.value:
        set_rule(get_entrance("Route 2 Northwest Smashable Rock"), lambda state: can_rock_smash(state))
        set_rule(get_entrance("Route 2 Northeast Smashable Rock"), lambda state: can_rock_smash(state))
        set_rule(get_entrance("Route 2 Northeast Cuttable Tree"), lambda state: can_cut(state))
    else:
        set_rule(get_entrance("Route 2 Northwest Cuttable Tree"), lambda state: can_cut(state))
        set_rule(get_entrance("Route 2 Northeast Cuttable Tree (North)"), lambda state: can_cut(state))
        set_rule(get_entrance("Route 2 Northeast Cuttable Tree (South)"), lambda state: can_cut(state))

    # Pewter City
    set_rule(get_entrance("Pewter City Cuttable Tree"), lambda state: can_cut(state))
    set_rule(get_entrance("Pewter City Exit (East)"), lambda state: can_pass_junopsis_city_roadblock(state))

    # Route 4
    set_rule(get_location("Route 4 Pokemon Center 1F - Salesman Purchase"), lambda state: can_grind_money(state))

    # Mt. Moon
    if "Mt. Moon" in options.additional_dark_caves.value:
        set_rule(get_entrance("Mt. Moon 1F Leave South Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon 1F Leave Center-Right Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon 1F Leave Center-Left Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon 1F Leave Northwest Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon B1F Leave First Tunnel Northeast Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon B1F Leave First Tunnel Southeast Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon B1F Leave Second Tunnel East Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon B1F Leave Second Tunnel West Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon B1F Leave Third Tunnel Northwest Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon B1F Leave Third Tunnel Southeast Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon B1F Leave Fourth Tunnel West Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon B1F Leave Fourth Tunnel East Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon B2F Leave South Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon B2F Leave Northeast Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon B2F Leave Center Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Mt. Moon B2F Leave Northwest Entry"), lambda state: dark_cave(state))

        for i in range(1, 5):
            set_rule(get_location(f"Mt. Moon 1F - Land Encounter {i}"), lambda state: dark_cave(state))
            set_rule(get_location(f"Mt. Moon B2F - Land Encounter {i}"), lambda state: dark_cave(state))
            if (options.flash_required == FlashRequired.option_required and
                    options.level_scaling != LevelScaling.option_off):
                set_rule(get_location(f"Mt. Moon 1F Land Scaling {i}"), lambda state: dark_cave(state))
                set_rule(get_location(f"Mt. Moon B2F Land Scaling {i}"), lambda state: dark_cave(state))

        set_rule(get_location("Mt. Moon B1F - Land Encounter 1"), lambda state: dark_cave(state))
        if options.flash_required == FlashRequired.option_required and options.level_scaling != LevelScaling.option_off:
            set_rule(get_location("Mt. Moon B1F Land Scaling 1"), lambda state: dark_cave(state))

    # Cerulean City
    set_rule(get_location("Bike Shop - Bicycle Purchase"), lambda state: state.has("Bike Voucher", player))
    set_rule(get_location("Cerulean Trade House - Trade Poliwhirl"), lambda state: state.has("Poliwhirl", player))
    set_rule(get_entrance("Cerulean City Cuttable Tree"),
             lambda state: can_pass_cerulean_city_roadblocks(state) and can_cut(state))
    set_rule(get_entrance("Robbed House (Front)"), lambda state: can_pass_cerulean_city_roadblocks(state))
    set_rule(get_entrance("Cerulean City Outskirts Exit (East)"), lambda state: can_cut(state))
    set_rule(get_entrance("Cerulean City Near Cave Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Cerulean Cave"), lambda state: can_enter_cerulean_cave(state))

    if "Modify Route 9" in options.modify_world_state.value:
        set_rule(get_entrance("Cerulean City Outskirts Exit (East)"), lambda state: can_rock_smash(state))
    else:
        set_rule(get_entrance("Cerulean City Outskirts Exit (East)"), lambda state: can_cut(state))

    # Route 24
    set_rule(get_entrance("Route 24 Surfing Spot"), lambda state: can_surf(state))

    # Route 25
    set_rule(get_location("Route 25 - Item Near Bush"), lambda state: can_cut(state))
    set_rule(get_entrance("Route 25 Surfing Spot"), lambda state: can_surf(state))

    # Route 5
    set_rule(get_entrance("Route 5 Gate North Guard Checkpoint"), lambda state: state.has("Tea", player))
    set_rule(get_entrance("Route 5 Gate South Guard Checkpoint"), lambda state: state.has("Tea", player))

    if "Block Tunnels" in options.modify_world_state.value:
        set_rule(get_entrance("Route 5 Smashable Rocks"), lambda state: can_rock_smash(state))
        set_rule(get_entrance("Route 5 Near Tunnel Smashable Rocks"), lambda state: can_rock_smash(state))

    # Underground Path North-South Tunnel:
    set_rule(get_location("Underground Path North Entrance - Trade Nidoran M"),
             lambda state: state.has("Nidoran M", player))

    # Route 6
    set_rule(get_entrance("Route 6 Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Route 6 Gate South Guard Checkpoint"), lambda state: state.has("Tea", player))
    set_rule(get_entrance("Route 6 Gate North Guard Checkpoint"), lambda state: state.has("Tea", player))

    if "Block Tunnels" in options.modify_world_state.value:
        set_rule(get_entrance("Route 6 Smashable Rocks"), lambda state: can_rock_smash(state))
        set_rule(get_entrance("Route 6 Near Tunnel Smashable Rocks"), lambda state: can_rock_smash(state))

    # Vermilion City
    set_rule(get_location("Vermilion Trade House - Trade Spearow"), lambda state: state.has("Spearow", player))
    set_rule(get_entrance("Vermilion City Cuttable Tree"), lambda state: can_cut(state))
    set_rule(get_entrance("Vermilion City Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Vermilion City Near Gym Cuttable Tree"), lambda state: can_cut(state))
    set_rule(get_entrance("Vermilion City Near Gym Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Vermilion Harbor"), lambda state: state.has("S.S. Ticket", player))

    # S.S. Anne
    set_rule(get_entrance("S.S. Anne Exterior Surfing Spot"), lambda state: can_surf(state))

    # Route 11
    set_rule(get_entrance("Route 11 West Surfing Spot"), lambda state: can_surf(state))

    if "Route 12 Boulders" in options.modify_world_state.value:
        set_rule(get_entrance("Route 11 East Exit"), lambda state: can_strength(state))

    set_rule(get_location("Route 11 Gate 2F - Trade Nidorino"), lambda state: state.has("Nidorino", player))

    # Diglett's Cave
    if "Diglett's Cave" in options.additional_dark_caves.value:
        set_rule(get_entrance("Diglett's Cave B1F Leave Northwest Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Diglett's Cave B1F Leave Southeast Entry"), lambda state: dark_cave(state))

        for i in range(1, 3):
            set_rule(get_location(f"Diglett's Cave B1F - Land Encounter {i}"), lambda state: dark_cave(state))
            if (options.flash_required == FlashRequired.option_required and
                    options.level_scaling != LevelScaling.option_off):
                set_rule(get_location(f"Diglett's Cave B1F Land Scaling {i}"), lambda state: dark_cave(state))

    # Route 9
    if "Modify Route 9" in options.modify_world_state.value:
        set_rule(get_entrance("Route 9 Exit (West)"), lambda state: can_rock_smash(state))
    else:
        set_rule(get_entrance("Route 9 Exit (West)"), lambda state: can_cut(state))

    # Route 10
    set_rule(get_entrance("Route 10 North Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Route 10 Near Power Plant Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Power Plant (Front)"),
             lambda state: state.has("Machine Part", player) or not options.extra_key_items)
    set_rule(get_entrance("Route 10 Waterfall Drop"), lambda state: can_waterfall(state))
    set_rule(get_entrance("Route 10 Waterfall Ascend"), lambda state: can_waterfall(state))

    if "Modify Route 10" in options.modify_world_state.value:
        set_rule(get_entrance("Route 10 South Surfing Spot"), lambda state: can_surf(state))
    else:
        set_rule(get_entrance("Route 10 South Surfing Spot"), lambda state: False)
        set_rule(get_entrance("Route 10 South Landing"), lambda state: False)
        set_rule(get_entrance("Route 10 South (Fishing Battle)"), lambda state: False)

    # Rock Tunnel
    set_rule(get_entrance("Rock Tunnel 1F Leave Northeast Entry (Northeast)"), lambda state: dark_cave(state))
    set_rule(get_entrance("Rock Tunnel 1F Leave Northeast Entry (Northwest)"), lambda state: dark_cave(state))
    set_rule(get_entrance("Rock Tunnel 1F Leave Northwest Entry (Northwest)"), lambda state: dark_cave(state))
    set_rule(get_entrance("Rock Tunnel 1F Leave Northwest Entry (East)"), lambda state: dark_cave(state))
    set_rule(get_entrance("Rock Tunnel 1F Leave South Entry (Northeast)"), lambda state: dark_cave(state))
    set_rule(get_entrance("Rock Tunnel 1F Leave South Entry (South)"), lambda state: dark_cave(state))
    set_rule(get_entrance("Rock Tunnel B1F Leave Southeast Entry (Southeast)"), lambda state: dark_cave(state))
    set_rule(get_entrance("Rock Tunnel B1F Leave Southeast Entry (Northeast)"), lambda state: dark_cave(state))
    set_rule(get_entrance("Rock Tunnel B1F Leave Northwest Entry (East)"), lambda state: dark_cave(state))
    set_rule(get_entrance("Rock Tunnel B1F Leave Northwest Entry (Northwest)"), lambda state: dark_cave(state))

    for i in range(1, 6):
        set_rule(get_location(f"Rock Tunnel 1F - Land Encounter {i}"), lambda state: dark_cave(state))
        set_rule(get_location(f"Rock Tunnel B1F - Land Encounter {i}"), lambda state: dark_cave(state))
        if options.flash_required == FlashRequired.option_required and options.level_scaling != LevelScaling.option_off:
            set_rule(get_location(f"Rock Tunnel 1F Land Scaling {i}"), lambda state: dark_cave(state))
            set_rule(get_location(f"Rock Tunnel B1F Land Scaling {i}"), lambda state: dark_cave(state))

    # Lavender Town
    set_rule(get_location("Volunteer Pokemon House - Mr. Fuji's Gift"),
             lambda state: state.has("Rescue Mr. Fuji", player))

    # Route 8
    set_rule(get_entrance("Route 8 Cuttable Trees"), lambda state: can_cut(state))
    set_rule(get_entrance("Route 8 Gate East Guard Checkpoint"), lambda state: state.has("Tea", player))
    set_rule(get_entrance("Route 8 Gate West Guard Checkpoint"), lambda state: state.has("Tea", player))

    if "Block Tunnels" in options.modify_world_state.value:
        set_rule(get_entrance("Route 8 Smashable Rocks"), lambda state: can_rock_smash(state))
        set_rule(get_entrance("Route 8 Near Tunnel Smashable Rocks"), lambda state: can_rock_smash(state))

    # Route 7
    set_rule(get_entrance("Route 7 Gate West Guard Checkpoint"), lambda state: state.has("Tea", player))
    set_rule(get_entrance("Route 7 Gate East Guard Checkpoint"), lambda state: state.has("Tea", player))

    if "Block Tunnels" in options.modify_world_state.value:
        set_rule(get_entrance("Route 7 Smashable Rocks"), lambda state: can_rock_smash(state))
        set_rule(get_entrance("Route 7 Near Tunnel Smashable Rocks"), lambda state: can_rock_smash(state))

    # Celadon City
    set_rule(get_location("Celadon Department Store Roof - Thirsty Girl's Gift (Give Fresh Water)"),
             lambda state: can_grind_money(state))
    set_rule(get_location("Celadon Department Store Roof - Thirsty Girl's Gift (Give Soda Pop)"),
             lambda state: can_grind_money(state))
    set_rule(get_location("Celadon Department Store Roof - Thirsty Girl's Gift (Give Lemonade)"),
             lambda state: can_grind_money(state))
    set_rule(get_location("Celadon Game Corner - Fisherman's Gift"), lambda state: state.has("Coin Case", player))
    set_rule(get_location("Celadon Game Corner - Scientist's Gift"), lambda state: state.has("Coin Case", player))
    set_rule(get_location("Celadon Game Corner - Gentleman's Gift"), lambda state: state.has("Coin Case", player))
    set_rule(get_location("Celadon Department Store Roof - Vending Machine"), lambda state: can_grind_money(state))
    set_rule(get_location("Celadon Game Corner Prize Room - Prize Pokemon 1"),
             lambda state: state.has("Coin Case", player) and can_grind_money(state))
    set_rule(get_location("Celadon Game Corner Prize Room - Prize Pokemon 2"),
             lambda state: state.has("Coin Case", player) and can_grind_money(state))
    set_rule(get_location("Celadon Game Corner Prize Room - Prize Pokemon 3"),
             lambda state: state.has("Coin Case", player) and can_grind_money(state))
    set_rule(get_location("Celadon Game Corner Prize Room - Prize Pokemon 4"),
             lambda state: state.has("Coin Case", player) and can_grind_money(state))
    set_rule(get_location("Celadon Game Corner Prize Room - Prize Pokemon 5"),
             lambda state: state.has("Coin Case", player) and can_grind_money(state))
    set_rule(get_entrance("Celadon City Cuttable Tree"), lambda state: can_cut(state))
    set_rule(get_entrance("Celadon City Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Celadon City Near Gym Cuttable Tree"), lambda state: can_cut(state))
    set_rule(get_entrance("Rocket Hideout"),
             lambda state: state.has("Hideout Key", player) or not options.extra_key_items)
    set_rule(get_entrance("Celadon Gym Cuttable Trees"), lambda state: can_cut(state))

    # Rocket Hideout
    set_rule(get_entrance("Rocket Hideout Elevator B1F Stop"), lambda state: state.has("Lift Key", player))
    set_rule(get_entrance("Rocket Hideout Elevator B2F Stop"), lambda state: state.has("Lift Key", player))
    set_rule(get_entrance("Rocket Hideout Elevator B4F Stop"), lambda state: state.has("Lift Key", player))

    # Pokemon Tower
    set_rule(get_entrance("Pokemon Tower 6F (Ghost Battle)"), lambda state: state.has("Silph Scope", player))
    set_rule(get_entrance("Pokemon Tower 6F Near Stairs (Ghost Battle)"), lambda state: state.has("Silph Scope", player))
    set_rule(get_entrance("Pokemon Tower 6F Reveal Ghost"), lambda state: state.has("Silph Scope", player))

    if "Block Tower" in options.modify_world_state.value:
        set_rule(get_entrance("Pokemon Tower 1F (Ghost Battle)"), lambda state: state.has("Silph Scope", player))
        set_rule(get_entrance("Pokemon Tower 1F Near Stairs (Ghost Battle)"),
                 lambda state: state.has("Silph Scope", player))
        set_rule(get_entrance("Pokemon Tower 1F Reveal Ghost"), lambda state: state.has("Silph Scope", player))
    else:
        set_rule(get_entrance("Pokemon Tower 1F (Ghost Battle)"), lambda state: False)
        set_rule(get_entrance("Pokemon Tower 1F Near Stairs (Ghost Battle)"), lambda state: False)

    for i in range(3, 8):
        for j in range(1, 4):
            set_rule(get_location(f"Pokemon Tower {i}F - Land Encounter {j}"),
                     lambda state: state.has("Silph Scope", player))

    # Route 12
    set_rule(get_entrance("Route 12 West Play Poke Flute"), lambda state: state.has("Poke Flute", player))
    set_rule(get_entrance("Route 12 North Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Route 12 Center Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Route 12 Center Play Poke Flute"), lambda state: state.has("Poke Flute", player))
    set_rule(get_entrance("Route 12 South Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Route 12 South Cuttable Tree (North)"), lambda state: can_cut(state))
    set_rule(get_entrance("Route 12 South Cuttable Tree (South)"), lambda state: can_cut(state))
    set_rule(get_entrance("Route 12 South Play Poke Flute"), lambda state: state.has("Poke Flute", player))

    if "Route 12 Boulders" in options.modify_world_state.value:
        set_rule(get_entrance("Route 12 West Exit"), lambda state: can_strength(state))
        set_rule(get_entrance("Route 12 South Exit"), lambda state: can_strength(state))

    if "Modify Route 12" in options.modify_world_state.value:
        set_rule(get_entrance("Route 12 Center Water Unobstructed Path"), lambda state: False)
        set_rule(get_entrance("Route 12 South Water Unobstructed Path"), lambda state: False)

    # Route 13
    set_rule(get_entrance("Route 13 Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Route 13 Cuttable Tree"), lambda state: can_cut(state))

    if "Route 12 Boulders" in options.modify_world_state.value:
        set_rule(get_entrance("Route 13 Exit (East)"), lambda state: can_strength(state))

    # Route 14
    set_rule(get_entrance("Route 14 Cuttable Tree (North)"), lambda state: can_cut(state))
    set_rule(get_entrance("Route 14 Cuttable Tree (South)"), lambda state: can_cut(state))

    # Route 16
    set_rule(get_entrance("Route 16 Southeast Cuttable Tree"), lambda state: can_cut(state))
    set_rule(get_entrance("Route 16 Southeast Play Poke Flute"), lambda state: state.has("Poke Flute", player))
    set_rule(get_entrance("Route 16 Northeast Cuttable Tree"), lambda state: can_cut(state))
    set_rule(get_entrance("Route 16 Center Play Poke Flute"), lambda state: state.has("Poke Flute", player))
    set_rule(get_entrance("Route 16 Gate 1F Southeast Bike Checkpoint"), lambda state: state.has("Bicycle", player))

    if "Modify Route 16" in options.modify_world_state.value:
        set_rule(get_entrance("Route 16 Northeast Smashable Rock"), lambda state: can_rock_smash(state))
        set_rule(get_entrance("Route 16 Center Smashable Rock"), lambda state: can_rock_smash(state))
    else:
        set_rule(get_entrance("Route 16 Northeast Smashable Rock"), lambda state: False)
        set_rule(get_entrance("Route 16 Center Smashable Rock"), lambda state: False)

    # Route 18
    set_rule(get_entrance("Route 18 Gate 1F East Bike Checkpoint"), lambda state: state.has("Bicycle", player))
    set_rule(get_location("Route 18 Gate 2F - Trade Golduck"), lambda state: state.has("Golduck", player))

    # Fuchsia City
    set_rule(get_location("Safari Zone Warden's House - Safari Zone Warden's Gift"),
             lambda state: state.has("Gold Teeth", player))
    set_rule(get_location("Safari Zone Warden's House - Item"), lambda state: can_strength(state))
    set_rule(get_entrance("Fuchsia City Backyard Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Safari Zone"), lambda state: state.has("Safari Pass", player) or not options.extra_key_items)

    # Safari Zone
    set_rule(get_entrance("Safari Zone Center Area South Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Safari Zone Center Area Northwest Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Safari Zone Center Area Northeast Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Safari Zone East Area Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Safari Zone North Area Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Safari Zone West Area North Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Safari Zone West Area South Surfing Spot"), lambda state: can_surf(state))

    # Saffron City
    set_rule(get_entrance("Silph Co."), lambda state: state.has_any(["Rescue Mr. Fuji", "Liberate Silph Co."], player))
    set_rule(get_entrance("Copycat's House"), lambda state: state.has("Liberate Silph Co.", player))
    set_rule(get_entrance("Saffron Gym"), lambda state: state.has("Liberate Silph Co.", player))
    set_rule(get_entrance("Saffron Pidgey House"), lambda state: state.has("Liberate Silph Co.", player))

    # Silph Co.
    set_rule(get_entrance("Silph Co. 2F Barrier (Northwest)"), lambda state: can_open_silph_door(2, state))
    set_rule(get_entrance("Silph Co. 2F Barrier (Southwest)"), lambda state: can_open_silph_door(2, state))
    set_rule(get_entrance("Silph Co. 2F Northwest Room Barrier"), lambda state: can_open_silph_door(2, state))
    set_rule(get_entrance("Silph Co. 2F Southwest Room Barrier"), lambda state: can_open_silph_door(2, state))
    set_rule(get_entrance("Silph Co. 3F Barrier"), lambda state: can_open_silph_door(3, state))
    set_rule(get_entrance("Silph Co. 3F Center Room Barrier (East)"), lambda state: can_open_silph_door(3, state))
    set_rule(get_entrance("Silph Co. 3F Center Room Barrier (West)"), lambda state: can_open_silph_door(3, state))
    set_rule(get_entrance("Silph Co. 3F West Room Barrier"), lambda state: can_open_silph_door(3, state))
    set_rule(get_entrance("Silph Co. 4F Barrier (West)"), lambda state: can_open_silph_door(4, state))
    set_rule(get_entrance("Silph Co. 4F Barrier (Center)"), lambda state: can_open_silph_door(4, state))
    set_rule(get_entrance("Silph Co. 4F North Room Barrier"), lambda state: can_open_silph_door(4, state))
    set_rule(get_entrance("Silph Co. 5F Barrier (Northwest)"), lambda state: can_open_silph_door(5, state))
    set_rule(get_entrance("Silph Co. 5F Barrier (Center)"), lambda state: can_open_silph_door(5, state))
    set_rule(get_entrance("Silph Co. 5F Barrier (Southwest)"), lambda state: can_open_silph_door(5, state))
    set_rule(get_entrance("Silph Co. 5F Southwest Room Barrier"), lambda state: can_open_silph_door(5, state))
    set_rule(get_entrance("Silph Co. 6F Barrier"), lambda state: can_open_silph_door(6, state))
    set_rule(get_entrance("Silph Co. 7F Barrier (Center)"), lambda state: can_open_silph_door(7, state))
    set_rule(get_entrance("Silph Co. 7F Barrier (East)"), lambda state: can_open_silph_door(7, state))
    set_rule(get_entrance("Silph Co. 7F East Room Barrier (North)"), lambda state: can_open_silph_door(7, state))
    set_rule(get_entrance("Silph Co. 7F East Room Barrier (South)"), lambda state: can_open_silph_door(7, state))
    set_rule(get_entrance("Silph Co. 7F Southeast Room Barrier"), lambda state: can_open_silph_door(7, state))
    set_rule(get_entrance("Silph Co. 8F Barrier"), lambda state: can_open_silph_door(8, state))
    set_rule(get_entrance("Silph Co. 8F West Room Barrier"), lambda state: can_open_silph_door(8, state))
    set_rule(get_entrance("Silph Co. 9F Barrier"), lambda state: can_open_silph_door(9, state))
    set_rule(get_entrance("Silph Co. 9F Northwest Room Barrier"), lambda state: can_open_silph_door(9, state))
    set_rule(get_entrance("Silph Co. 9F Southwest Room Barrier (East)"), lambda state: can_open_silph_door(9, state))
    set_rule(get_entrance("Silph Co. 9F Southwest Room Barrier (West)"), lambda state: can_open_silph_door(9, state))
    set_rule(get_entrance("Silph Co. 10F Barrier"), lambda state: can_open_silph_door(10, state))
    set_rule(get_entrance("Silph Co. 10F Southeast Room Barrier"), lambda state: can_open_silph_door(10, state))
    set_rule(get_entrance("Silph Co. 11F West Barrier"), lambda state: can_open_silph_door(11, state))

    # Route 19
    set_rule(get_entrance("Route 19 Surfing Spot"), lambda state: can_surf(state))

    # Route 20
    set_rule(get_entrance("Route 20 Near North Cave Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Route 20 Near South Cave Surfing Spot"), lambda state: can_surf(state))

    # Seafoam Islands
    set_rule(get_entrance("Seafoam Islands B3F West Surfing Spot"),
             lambda state: can_surf(state) and can_strength(state) and
                           state.can_reach_region("Seafoam Islands 1F", player))
    set_rule(get_entrance("Seafoam Islands B3F Southeast Surfing Spot"),
             lambda state: can_surf(state) and can_strength(state) and
                           state.can_reach_region("Seafoam Islands 1F", player))
    set_rule(get_entrance("Seafoam Islands B3F West Landing"),
             lambda state: can_strength(state) and state.can_reach_region("Seafoam Islands 1F", player))
    set_rule(get_entrance("Seafoam Islands B3F Southeast Landing"),
             lambda state: can_strength(state) and state.can_reach_region("Seafoam Islands 1F", player))
    set_rule(get_entrance("Seafoam Islands B4F Surfing Spot (West)"),
             lambda state: can_surf(state) and can_strength(state) and
                           state.can_reach_region("Seafoam Islands B3F West", player))
    set_rule(get_entrance("Seafoam Islands B4F Near Articuno Landing"),
             lambda state: can_strength(state) and state.can_reach_region("Seafoam Islands B3F West", player))

    for i in range(1, 6):
        set_rule(get_location(f"Seafoam Islands B3F - Water Encounter {i}"),
                 lambda state: can_strength(state) and state.can_reach_region("Seafoam Islands 1F", player))

    # Cinnabar Island
    set_rule(get_location("Pokemon Lab Lounge - Trade Raichu"), lambda state: state.has("Raichu", player))
    set_rule(get_location("Pokemon Lab Lounge - Trade Venonat"), lambda state: state.has("Venonat", player))
    set_rule(get_location("Pokemon Lab Experiment Room - Revive Helix Fossil"),
             lambda state: state.has("Helix Fossil", player))
    set_rule(get_location("Pokemon Lab Experiment Room - Revive Dome Fossil"),
             lambda state: state.has("Dome Fossil", player))
    set_rule(get_location("Pokemon Lab Experiment Room - Revive Old Amber"),
             lambda state: state.has("Old Amber", player))
    set_rule(get_location("Pokemon Lab Experiment Room - Trade Ponyta"),
             lambda state: state.has("Ponyta", player))
    set_rule(get_entrance("Cinnabar Island Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Cinnabar Gym"), lambda state: state.has("Secret Key", player))
    set_rule(get_entrance("Pokemon Mansion"), lambda state: state.has("Letter", player) or not options.extra_key_items)

    # Route 23
    set_rule(get_entrance("Route 23 South Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Route 23 Near Water Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Route 23 Center Guard Checkpoint"), lambda state: can_pass_route_523_guard(state))

    if "Route 23 Trees" in options.modify_world_state.value:
        set_rule(get_entrance("Route 23 Near Water Cuttable Trees"), lambda state: can_cut(state))
        set_rule(get_entrance("Route 23 Center Cuttable Trees"), lambda state: can_cut(state))

    if "Modify Route 23" in options.modify_world_state.value:
        set_rule(get_entrance("Route 23 Waterfall Ascend"), lambda state: can_waterfall(state))
        set_rule(get_entrance("Route 23 Waterfall Drop"), lambda state: can_waterfall(state))

    # Victory Road
    set_rule(get_location("Victory Road 1F - North Item (Left)"), lambda state: can_strength(state))
    set_rule(get_location("Victory Road 1F - North Item (Right)"), lambda state: can_strength(state))
    set_rule(get_entrance("Victory Road 1F North Strength Boulder"), lambda state: can_strength(state))
    set_rule(get_entrance("Victory Road 2F Center Rock Barrier"),
             lambda state: can_strength(state) and state.can_reach_region("Victory Road 3F Southwest", player))
    set_rule(get_entrance("Victory Road 2F Northwest Strength Boulder"), lambda state: can_strength(state))
    set_rule(get_entrance("Victory Road 3F Southwest Strength Boulder"), lambda state: can_strength(state))
    set_rule(get_entrance("Victory Road 3F Southeast Strength Boulder"), lambda state: can_strength(state))

    if "Victory Road Rocks" in options.modify_world_state.value:
        set_rule(get_entrance("Victory Road 1F South Rock Barrier"),
                 lambda state: can_strength(state) and can_rock_smash(state))
        set_rule(get_entrance("Victory Road 2F Southwest Rock Barrier"),
                 lambda state: can_strength(state) and can_rock_smash(state))
        set_rule(get_entrance("Victory Road 3F North Rock Barrier"),
                 lambda state: can_strength(state) and can_rock_smash(state))
    else:
        set_rule(get_entrance("Victory Road 1F South Rock Barrier"), lambda state: can_strength(state))
        set_rule(get_entrance("Victory Road 2F Southwest Rock Barrier"), lambda state: can_strength(state))
        set_rule(get_entrance("Victory Road 3F North Rock Barrier"), lambda state: can_strength(state))

    if "Victory Road" in options.additional_dark_caves.value:
        set_rule(get_entrance("Victory Road 1F Leave South Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Victory Road 1F Leave North Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Victory Road 2F Leave Southwest Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Victory Road 2F Leave Center Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Victory Road 2F Leave Northwest Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Victory Road 2F Leave Southeast Entry"), lambda state: dark_cave(state))
        set_rule(get_entrance("Victory Road 2F Leave East Entry (West)"), lambda state: dark_cave(state))
        set_rule(get_entrance("Victory Road 2F Leave East Entry (East)"), lambda state: dark_cave(state))
        set_rule(get_entrance("Victory Road 3F Leave North Entry (West)"), lambda state: dark_cave(state))
        set_rule(get_entrance("Victory Road 3F Leave North Entry (East)"), lambda state: dark_cave(state))
        set_rule(get_entrance("Victory Road 3F Leave Southeast Entry (North)"), lambda state: dark_cave(state))
        set_rule(get_entrance("Victory Road 3F Leave Southeast Entry (South)"), lambda state: dark_cave(state))

        for i in range(1, 9):
            set_rule(get_location(f"Victory Road 1F - Land Encounter {i}"), lambda state: dark_cave(state))
            set_rule(get_location(f"Victory Road 2F - Land Encounter {i}"), lambda state: dark_cave(state))
            set_rule(get_location(f"Victory Road 3F - Land Encounter {i}"), lambda state: dark_cave(state))
            if (options.flash_required == FlashRequired.option_required and
                    options.level_scaling != LevelScaling.option_off):
                set_rule(get_location(f"Victory Road 1F Land Scaling {i}"), lambda state: dark_cave(state))
                set_rule(get_location(f"Victory Road 2F Land Scaling {i}"), lambda state: dark_cave(state))
                set_rule(get_location(f"Victory Road 3F Land Scaling {i}"), lambda state: dark_cave(state))

        set_rule(get_location("Victory Road 2F - Land Encounter 9"), lambda state: dark_cave(state))
        if options.flash_required == FlashRequired.option_required and options.level_scaling != LevelScaling.option_off:
            set_rule(get_location("Victory Road 2F Land Scaling 9"), lambda state: dark_cave(state))

    # Indigo Plateau
    set_rule(get_entrance("Pokemon League"), lambda state: can_challenge_elite_four(state))

    # Cerulean Cave
    set_rule(get_location("Cerulean Cave 2F - East Item"), lambda state: can_rock_smash(state))
    set_rule(get_location("Cerulean Cave 2F - West Item"), lambda state: can_rock_smash(state))
    set_rule(get_location("Cerulean Cave 2F - Center Item"), lambda state: can_rock_smash(state))
    set_rule(get_entrance("Cerulean Cave 1F Southeast Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Cerulean Cave 1F Northeast Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Cerulean Cave 1F Surfing Spot"), lambda state: can_surf(state))
    set_rule(get_entrance("Cerulean Cave B1F Surfing Spot"), lambda state: can_surf(state))

    # Sevii Islands
    if not options.kanto_only:
        # Sky
        set_rule(get_entrance("One Island Fly Destination"), lambda state: state.has("Fly One Island", player))
        set_rule(get_entrance("Two Island Fly Destination"), lambda state: state.has("Fly Two Island", player))
        set_rule(get_entrance("Three Island Fly Destination"), lambda state: state.has("Fly Three Island", player))
        set_rule(get_entrance("Four Island Fly Destination"), lambda state: state.has("Fly Four Island", player))
        set_rule(get_entrance("Five Island Fly Destination"), lambda state: state.has("Fly Five Island", player))
        set_rule(get_entrance("Six Island Fly Destination"), lambda state: state.has("Fly Six Island", player))
        set_rule(get_entrance("Seven Island Fly Destination"), lambda state: state.has("Fly Seven Island", player))

        # Cinnabar Island
        set_rule(get_entrance("Follow Bill"), lambda state: state.has("Defeat Blaine", player))

        # One Island Town
        set_rule(get_location("One Island Pokemon Center 1F - Celio's Gift (Deliver Ruby)"),
                 lambda state: state.has_all(["Deliver Meteorite", "Ruby"], player))
        set_rule(get_location("One Island Pokemon Center 1F - Help Celio"),
                 lambda state: state.has_all(["Deliver Meteorite", "Ruby", "Free Captured Pokemon", "Sapphire"],
                                             player))
        set_rule(get_entrance("One Island Town Surfing Spot"), lambda state: can_surf(state))

        # Kindle Road
        set_rule(get_location("Kindle Road - Plateau Item"), lambda state: can_rock_smash(state))
        set_rule(get_location("Kindle Road - Item Behind Smashable Rock"), lambda state: can_rock_smash(state))
        set_rule(get_entrance("Kindle Road South Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Kindle Road Center Surfing Spot (South)"), lambda state: can_surf(state))
        set_rule(get_entrance("Kindle Road Center Surfing Spot (North)"), lambda state: can_surf(state))
        set_rule(get_entrance("Kindle Road North Surfing Spot"), lambda state: can_surf(state))

        # Mt. Ember
        set_rule(get_location("Mt. Ember Exterior - Item Near Summit"),
                 lambda state: can_strength(state) and can_rock_smash(state))
        set_rule(get_location("Mt. Ember Exterior - Eavesdrop on Team Rocket Grunts"),
                 lambda state: state.has("Deliver Meteorite", player))
        set_rule(get_entrance("Mt. Ember Exterior South Strength Boulders"), lambda state: can_strength(state))
        set_rule(get_entrance("Mt. Ember Ruby Path"), lambda state: state.has("Deliver Meteorite", player))
        set_rule(get_entrance("Mt. Ember Summit Strength Boulders"), lambda state: can_strength(state))
        set_rule(get_entrance("Mt. Ember Ruby Path B2F West Strength Boulders"), lambda state: can_strength(state))
        set_rule(get_entrance("Mt. Ember Ruby Path B2F East Strength Boulders"), lambda state: can_strength(state))
        set_rule(get_entrance("Mt. Ember Ruby Path B3F Northwest Strength Boulder (Southwest)"),
                 lambda state: can_strength(state))
        set_rule(get_entrance("Mt. Ember Ruby Path B3F Northwest Strength Boulder (Southeast)"),
                 lambda state: can_strength(state))
        set_rule(get_entrance("Mt. Ember Ruby Path B3F Southwest Strength Boulder (Northwest)"),
                 lambda state: can_strength(state))
        set_rule(get_entrance("Mt. Ember Ruby Path B3F Southwest Strength Boulder (Southeast)"),
                 lambda state: can_strength(state))
        set_rule(get_entrance("Mt. Ember Ruby Path B3F Southeast Strength Boulder (Northwest)"),
                 lambda state: can_strength(state))
        set_rule(get_entrance("Mt. Ember Ruby Path B3F Southeast Strength Boulder (Southwest)"),
                 lambda state: can_strength(state))

        # Two Island Town
        set_rule(get_location("Two Island Town - Item Behind Cuttable Tree"), lambda state: can_cut(state))
        set_rule(get_location("Two Island Game Corner - Lostelle's Dad's Gift"),
                 lambda state: state.has_all(["Rescue Lostelle", "Meteorite"], player))
        set_rule(get_location("Two Island Town - Market Stall"),
                 lambda state: state.has_all(["Rescue Lostelle", "Defeat Champion"], player) and can_grind_money(state))
        set_rule(get_location("Two Island Game Corner - Lostelle's Dad's Delivery"),
                 lambda state: state.has_all(["Rescue Lostelle", "Meteorite"], player))

        # Cape Brink
        set_rule(get_entrance("Cape Brink Surfing Spot"), lambda state: can_surf(state))

        # Three Island Town
        set_rule(get_entrance("Three Island Town Cuttable Tree"), lambda state: can_cut(state))

        # Bond Bridge
        set_rule(get_entrance("Bond Bridge Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Bond Bridge Cuttable Tree"), lambda state: can_cut(state))

        # Berry Forest
        set_rule(get_location("Berry Forest - Item Past Southwest Pond"), lambda state: can_cut(state))
        set_rule(get_entrance("Berry Forest Surfing Spot"), lambda state: can_surf(state))

        # Four Island Town
        set_rule(get_location("Four Island Town - Beach Item"), lambda state: can_rock_smash(state))
        set_rule(get_entrance("Four Island Town Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Four Island Town Near Cave Surfing Spot"), lambda state: can_surf(state))

        # Icefall Cave
        set_rule(get_entrance("Icefall Cave Front South Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Icefall Cave Front Waterfall Ascend"), lambda state: can_waterfall(state))
        set_rule(get_entrance("Icefall Cave Front Waterfall Drop"), lambda state: can_waterfall(state))
        set_rule(get_entrance("Icefall Cave Front Center Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Icefall Cave Front North Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Icefall Cave Back Surfing Spot"), lambda state: can_surf(state))

        # Five Island Town
        set_rule(get_entrance("Five Island Town Surfing Spot"), lambda state: can_surf(state))

        # Five Isle Meadow
        set_rule(get_location("Five Isle Meadow - Item Behind Cuttable Tree"), lambda state: can_cut(state))
        set_rule(get_entrance("Five Isle Meadow Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Rocket Warehouse"),
                 lambda state: state.has_all(["Learn Goldeen Need Log", "Learn Yes Nah Chansey"], player))

        # Memorial Pillar
        set_rule(get_location("Memorial Pillar - Memorial Man's Gift"),
                 lambda state: state.has("Buy Lemonade", player))

        # Resort Gorgeous
        set_rule(get_entrance("Resort Gorgeous Near Resort Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Resort Gorgeous Near Cave Surfing Spot"), lambda state: can_surf(state))

        # Water Path
        set_rule(get_entrance("Water Path South Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Water Path North Surfing Spot (South)"), lambda state: can_surf(state))
        set_rule(get_entrance("Water Path North Surfing Spot (North)"), lambda state: can_surf(state))

        # Ruin Valley
        set_rule(get_location("Ruin Valley - Plateau Item"), lambda state: can_strength(state))
        set_rule(get_location("Ruin Valley - Southwest Item"), lambda state: can_strength(state))
        set_rule(get_location("Ruin Valley - Southeast Item"), lambda state: can_strength(state))
        set_rule(get_entrance("Ruin Valley Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Dotted Hole"), lambda state: state.has("Help Lorelei", player) and can_cut(state))

        # Green Path
        set_rule(get_entrance("Green Path West Surfing Spot"), lambda state: can_surf(state))

        # Outcast Island
        set_rule(get_entrance("Outcast Island Surfing Spot"), lambda state: can_surf(state))

        # Sevault Canyon
        set_rule(get_location("Sevault Canyon - Item Behind Smashable Rocks"),
                 lambda state: can_strength(state) and can_rock_smash(state))

        # Tanoby Key
        set_rule(get_location("Tanoby Key - Solve Puzzle"), lambda state: can_strength(state))

        # Tanoby Ruins
        set_rule(get_location("Monean Chamber - Land Encounter 1"), lambda state: state.has("Spawn Unown", player))
        set_rule(get_location("Liptoo Chamber - Land Encounter 1"), lambda state: state.has("Spawn Unown", player))
        set_rule(get_location("Weepth Chamber - Land Encounter 1"), lambda state: state.has("Spawn Unown", player))
        set_rule(get_location("Dilford Chamber - Land Encounter 1"), lambda state: state.has("Spawn Unown", player))
        set_rule(get_location("Scufib Chamber - Land Encounter 1"), lambda state: state.has("Spawn Unown", player))
        set_rule(get_location("Rixy Chamber - Land Encounter 1"), lambda state: state.has("Spawn Unown", player))
        set_rule(get_location("Viapos Chamber - Land Encounter 1"), lambda state: state.has("Spawn Unown", player))
        set_rule(get_entrance("Tanoby Ruins Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Tanoby Ruins Viapois Island Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Tanoby Ruins Rixy Island Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Tanoby Ruins Scufib Island Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Tanoby Ruins Dilford Island Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Tanoby Ruins Weepth Island Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Tanoby Ruins Liptoo Island Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Tanoby Ruins Monean Island Surfing Spot"), lambda state: can_surf(state))

        # Trainer Tower
        set_rule(get_entrance("Trainer Tower Exterior South Surfing Spot"), lambda state: can_surf(state))
        set_rule(get_entrance("Trainer Tower Exterior North Surfing Spot"), lambda state: can_surf(state))

        # Indigo Plateau
        set_rule(get_location("Champion's Room - Champion Rematch Battle"),
                 lambda state: state.has_all(["Defeat Champion", "Restore Pokemon Network Machine"], player))

    # Hidden Items
    if options.shuffle_hidden != ShuffleHiddenItems.option_off:
        # Viridian Gym
        set_rule(get_location("Viridian Gym - Hidden Item Under Giovanni"),
                 lambda state: state.has("Itemfinder", player))

        # Route 10
        set_rule(get_location("Route 10 - Hidden Item Behind Cuttable Tree"), lambda state: can_cut(state))

        # Pokemon Tower
        set_rule(get_location("Pokemon Tower 7F - Hidden Item Under Mr. Fuji"),
                 lambda state: state.has("Itemfinder", player))

        # Route 12
        set_rule(get_location("Route 12 - Hidden Item Under Snorlax"), lambda state: state.has("Itemfinder", player))

        # Route 16
        set_rule(get_location("Route 16 - Hidden Item Under Snorlax"), lambda state: state.has("Itemfinder", player))

        # Navel Rock
        set_rule(get_location("Navel Rock - Hidden Item Near Ho-Oh"), lambda state: state.has("Itemfinder", player))

        # Sevii Islands
        if not options.kanto_only:
            # Cape Brink
            set_rule(get_location("Cape Brink - Hidden Item Across Pond"),
                     lambda state: state.has("Itemfinder", player))

        # Add rules for hidden items
        if world.options.itemfinder_required != ItemfinderRequired.option_off:
            for location in multiworld.get_locations(player):
                if location.tags is not None and ("Hidden" in location.tags):
                    add_rule(location, lambda state: state.has("Itemfinder", player))

    # Extra Key Items
    if options.extra_key_items:
        # Cerulean City
        set_rule(get_location("Cerulean Gym - Hidden Item in Water"),
                 lambda state: can_surf(state) and state.has("Itemfinder", player))

    # Trainersanity
    if options.trainersanity:
        # Route 22
        set_rule(get_location("Route 22 - Early Rival Reward"), lambda state: state.has("Deliver Oak's Parcel", player))
        set_rule(get_location("Route 22 - Late Rival Reward"),
                 lambda state: state.has_all(["Defeat Route 22 Rival", "Defeat Giovanni"], player))

        # Sevii Islands
        if not options.kanto_only:
            # Mt. Ember
            set_rule(get_location("Mt. Ember Exterior - Team Rocket Grunt Reward (Left)"),
                     lambda state: state.has("Deliver Meteorite", player))
            set_rule(get_location("Mt. Ember Exterior - Team Rocket Grunt Reward (Right)"),
                     lambda state: state.has("Deliver Meteorite", player))

            # Indigo Plateau
            set_rule(get_location("Lorelei's Room - Elite Four Lorelei Rematch Reward"),
                     lambda state: state.has_all(["Defeat Champion", "Restore Pokemon Network Machine"], player))
            set_rule(get_location("Bruno's Room - Elite Four Bruno Rematch Reward"),
                     lambda state: state.has_all(["Defeat Champion", "Restore Pokemon Network Machine"], player))
            set_rule(get_location("Agatha's Room - Elite Four Agatha Rematch Reward"),
                     lambda state: state.has_all(["Defeat Champion", "Restore Pokemon Network Machine"], player))
            set_rule(get_location("Lance's Room - Elite Four Lance Rematch Reward"),
                     lambda state: state.has_all(["Defeat Champion", "Restore Pokemon Network Machine"], player))
            set_rule(get_location("Champion's Room - Champion Rematch Reward"),
                     lambda state: state.has_all(["Defeat Champion", "Restore Pokemon Network Machine"], player))

    # Evolutions
    set_rule(get_location("Evolution - Nimbleaf"),
             lambda state: state.has("Nimbleaf", player) and evolve_level(state, 16))
    set_rule(get_location("Evolution - Leafrond"),
             lambda state: state.has("Leafrond", player) and evolve_level(state, 34))
    set_rule(get_location("Evolution - Peyero"),
             lambda state: state.has("Peyero", player) and evolve_level(state, 18))
    set_rule(get_location("Evolution - Infiris"),
             lambda state: state.has("Infiris", player) and evolve_level(state, 32))
    set_rule(get_location("Evolution - Liquiput"),
             lambda state: state.has("Liquiput", player) and evolve_level(state, 14))
    set_rule(get_location("Evolution - Hydrush"),
             lambda state: state.has("Hydrush", player) and evolve_level(state, 36))
    set_rule(get_location("Evolution - Taillow"),
             lambda state: state.has("Taillow", player) and evolve_level(state, 22))
    set_rule(get_location("Evolution - Riolu"),
             lambda state: state.has("Riolu", player))
    set_rule(get_location("Evolution - Houndour"),
             lambda state: state.has("Houndour", player) and evolve_level(state, 24))
    set_rule(get_location("Evolution - Diglett"),
             lambda state: state.has("Diglett", player) and evolve_level(state, 26))
    set_rule(get_location("Evolution - Togepi"),
             lambda state: state.has("Togepi", player))
    set_rule(get_location("Evolution - Togetic"),
             lambda state: state.has("Togetic", player)) # todo: what's the sun stone condition
    set_rule(get_location("Evolution - Glachild"),
             lambda state: state.has("Glachild", player) and evolve_level(state, 20))
    set_rule(get_location("Evolution - Frozaiden"),
             lambda state: state.has("Frozaiden", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Pichu"),
             lambda state: state.has("Pichu", player))
    set_rule(get_location("Evolution - Pikachu (Thunder Stone)"),
             lambda state: state.has("Pikachu", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Pikachu (Friendship)"),
             lambda state: state.has("Pikachu", player))
    set_rule(get_location("Evolution - Nidoran F"),
             lambda state: state.has("Nidoran F", player) and evolve_level(state, 16))
    set_rule(get_location("Evolution - Nidorina"),
             lambda state: state.has("Nidorina", player)) # todo: what's the moon stone condition
    set_rule(get_location("Evolution - Nidoran M"),
             lambda state: state.has("Nidoran M", player) and evolve_level(state, 16))
    set_rule(get_location("Evolution - Nidorino"),
             lambda state: state.has("Nidorino", player)) # todo: what's the moon stone condition
    set_rule(get_location("Evolution - Buizel"),
             lambda state: state.has("Buizel", player) and evolve_level(state, 26))
    set_rule(get_location("Evolution - Jamberree"),
             lambda state: state.has("Jamberree", player) and evolve_level(state, 25))
    set_rule(get_location("Evolution - Pineco"),
             lambda state: state.has("Pineco", player) and evolve_level(state, 31))
    set_rule(get_location("Evolution - Shellder"),
             lambda state: state.has("Shellder", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Psycolt (Moon Stone)"),
             lambda state: state.has("Psycolt", player)) # todo: what's the moon stone condition
    set_rule(get_location("Evolution - Psycolt (Sun Stone)"),
             lambda state: state.has("Psycolt", player)) # todo: what's the sun stone condition
    set_rule(get_location("Evolution - Tyrogue (Atk > Def)"),
             lambda state: state.has("Tyrogue", player) and evolve_level(state, 20))
    set_rule(get_location("Evolution - Tyrogue (Atk < Def)"),
             lambda state: state.has("Tyrogue", player) and evolve_level(state, 20))
    set_rule(get_location("Evolution - Tyrogue (Atk = Def)"),
             lambda state: state.has("Tyrogue", player) and evolve_level(state, 20))
    set_rule(get_location("Evolution - Rynos"),
             lambda state: state.has("Rynos", player) and evolve_level(state, 40))
    set_rule(get_location("Evolution - Absol"),
             lambda state: state.has("Absol", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Girafarig"),
             lambda state: state.has("Girafarig", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Willisp"),
             lambda state: state.has("Willisp", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Magnemite"),
             lambda state: state.has("Magnemite", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Magneton"),
             lambda state: state.has("Magneton", player))
    set_rule(get_location("Evolution - Staryu"),
             lambda state: state.has("Staryu", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Gastly"),
             lambda state: state.has("Gastly", player) and evolve_level(state, 25))
    set_rule(get_location("Evolution - Haunter"),
             lambda state: state.has("Haunter", player) and evolve_level(state, 38))
    set_rule(get_location("Evolution - Exeggcute"),
             lambda state: state.has("Exeggcute", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Velvelt"),
             lambda state: state.has("Velvelt", player) and evolve_level(state, 35))
    set_rule(get_location("Evolution - Rhyhorn"),
             lambda state: state.has("Rhyhorn", player) and evolve_level(state, 42))
    set_rule(get_location("Evolution - Rhydon"),
             lambda state: state.has("Rhydon", player)) # todo: what's the moon stone condition
    set_rule(get_location("Evolution - Porygon"),
             lambda state: state.has("Porygon", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Porygon2"),
             lambda state: state.has("Porygon2", player))
    set_rule(get_location("Evolution - Spheal"),
             lambda state: state.has("Spheal", player) and evolve_level(state, 32))
    set_rule(get_location("Evolution - Sealeo"),
             lambda state: state.has("Sealeo", player) and evolve_level(state, 44))
    set_rule(get_location("Evolution - Rollder"),
             lambda state: state.has("Rollder", player) and evolve_level(state, 25))
    set_rule(get_location("Evolution - Snalo"),
             lambda state: state.has("Snalo", player) and evolve_level(state, 40))
    set_rule(get_location("Evolution - Snover"),
             lambda state: state.has("Snover", player) and evolve_level(state, 40))
    set_rule(get_location("Evolution - Yucarlia"),
             lambda state: state.has("Yucarlia", player) and evolve_level(state, 35))
    set_rule(get_location("Evolution - Cupricorn"),
             lambda state: state.has("Cupricorn", player) and evolve_level(state, 18))
    set_rule(get_location("Evolution - Hornikel"),
             lambda state: state.has("Hornikel", player) and evolve_level(state, 32))
    set_rule(get_location("Evolution - Mornwing"),
             lambda state: state.has("Mornwing", player) and evolve_level(state, 36))
    set_rule(get_location("Evolution - Guldawn"),
             lambda state: state.has("Guldawn", player) and evolve_level(state, 45))
    set_rule(get_location("Evolution - Mintch"),
             lambda state: state.has("Mintch", player) and evolve_level(state, 18))
    set_rule(get_location("Evolution - Maneko"),
             lambda state: state.has("Maneko", player) and evolve_level(state, 18))
    set_rule(get_location("Evolution - Plasmox"),
             lambda state: state.has("Plasmox", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Cuppa"),
             lambda state: state.has("Cuppa", player) and evolve_level(state, 28))
    set_rule(get_location("Evolution - Clotaku"),
             lambda state: state.has("Clotaku", player) and evolve_level(state, 16))
    set_rule(get_location("Evolution - Ajarimus"),
             lambda state: state.has("Ajarimus", player) and evolve_level(state, 32))
    set_rule(get_location("Evolution - Hoothoot"),
             lambda state: state.has("Hoothoot", player) and evolve_level(state, 20))
    set_rule(get_location("Evolution - Elekid"),
             lambda state: state.has("Elekid", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Electabuzz"),
             lambda state: state.has("Electabuzz", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Magby"),
             lambda state: state.has("Magby", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Magmar"),
             lambda state: state.has("Magmar", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Lileep"),
             lambda state: state.has("Lileep", player) and evolve_level(state, 40))
    set_rule(get_location("Evolution - Grindon"),
             lambda state: state.has("Grindon", player) and evolve_level(state, 40))
    set_rule(get_location("Evolution - Larvitar"),
             lambda state: state.has("Larvitar", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Pupitar"),
             lambda state: state.has("Pupitar", player) and evolve_level(state, 55))
    set_rule(get_location("Evolution - Beldum"),
             lambda state: state.has("Beldum", player) and evolve_level(state, 20))
    set_rule(get_location("Evolution - Metang"),
             lambda state: state.has("Metang", player) and evolve_level(state, 45))
    set_rule(get_location("Evolution - Gible"),
             lambda state: state.has("Gible", player) and evolve_level(state, 24))
    set_rule(get_location("Evolution - Gabite"),
             lambda state: state.has("Gabite", player) and evolve_level(state, 48))
    set_rule(get_location("Evolution - Laquagon"),
             lambda state: state.has("Laquagon", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Dragune"),
             lambda state: state.has("Dragune", player) and evolve_level(state, 50))
    set_rule(get_location("Evolution - Bulbasaur"),
             lambda state: state.has("Bulbasaur", player) and evolve_level(state, 16))
    set_rule(get_location("Evolution - Ivysaur"),
             lambda state: state.has("Ivysaur", player) and evolve_level(state, 32))
    set_rule(get_location("Evolution - Charmander"),
             lambda state: state.has("Charmander", player) and evolve_level(state, 16))
    set_rule(get_location("Evolution - Charmeleon"),
             lambda state: state.has("Charmeleon", player) and evolve_level(state, 36))
    set_rule(get_location("Evolution - Squirtle"),
             lambda state: state.has("Squirtle", player) and evolve_level(state, 16))
    set_rule(get_location("Evolution - Wartortle"),
             lambda state: state.has("Wartortle", player) and evolve_level(state, 36))
    set_rule(get_location("Evolution - Basille"),
             lambda state: state.has("Basille", player) and evolve_level(state, 16))
    set_rule(get_location("Evolution - Basield"),
             lambda state: state.has("Basield", player) and evolve_level(state, 34))
    set_rule(get_location("Evolution - Patroleo"),
             lambda state: state.has("Patroleo", player) and evolve_level(state, 16))
    set_rule(get_location("Evolution - Gardleon"),
             lambda state: state.has("Gardleon", player) and evolve_level(state, 36))
    set_rule(get_location("Evolution - Katuna"),
             lambda state: state.has("Katuna", player) and evolve_level(state, 16))
    set_rule(get_location("Evolution - Maelstream"),
             lambda state: state.has("Maelstream", player) and evolve_level(state, 32))
    set_rule(get_location("Evolution - Cheshile (High Personality)"),
             lambda state: state.has("Cheshile", player) and evolve_level(state, 24))
    set_rule(get_location("Evolution - Cheshile (Low Personality)"),
             lambda state: state.has("Cheshile", player) and evolve_level(state, 24))
    set_rule(get_location("Evolution - Rivird"),
             lambda state: state.has("Rivird", player) and evolve_level(state, 23))
    set_rule(get_location("Evolution - Pachirisu"),
             lambda state: state.has("Pachirisu", player) and evolve_level(state, 26))
    set_rule(get_location("Evolution - Pumpkid"),
             lambda state: state.has("Pumpkid", player) and evolve_level(state, 31))
    set_rule(get_location("Evolution - Lunabitt"),
             lambda state: state.has("Lunabitt", player)) # todo: what's the moon stone condition
    set_rule(get_location("Evolution - Liepus"),
             lambda state: state.has("Liepus", player)) # todo: what's the sun stone condition
    set_rule(get_location("Evolution - Smoochum"),
             lambda state: state.has("Smoochum", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Jynx"),
             lambda state: state.has("Jynx", player) and evolve_level(state, 45))
    set_rule(get_location("Evolution - Takuni"),
             lambda state: state.has("Takuni", player) and evolve_level(state, 20))
    set_rule(get_location("Evolution - Percussoon"),
             lambda state: state.has("Percussoon", player) and evolve_level(state, 34))
    set_rule(get_location("Evolution - Shivermin"),
             lambda state: state.has("Shivermin", player) and evolve_level(state, 29))
    set_rule(get_location("Evolution - Chatot"),
             lambda state: state.has("Chatot", player) and evolve_level(state, 42))
    set_rule(get_location("Evolution - Ledyba"),
             lambda state: state.has("Ledyba", player) and evolve_level(state, 18))
    set_rule(get_location("Evolution - Ledian"),
             lambda state: state.has("Ledian", player) and evolve_level(state, 38))
    set_rule(get_location("Evolution - Bisos"),
             lambda state: state.has("Bisos", player))
    set_rule(get_location("Evolution - Lunatone"),
             lambda state: state.has("Lunatone", player)) # todo: what's the moon stone condition
    set_rule(get_location("Evolution - Solrock"),
             lambda state: state.has("Solrock", player)) # todo: what's the sun stone condition
    set_rule(get_location("Evolution - Stellith (Moon Stone)"),
             lambda state: state.has("Stellith", player)) # todo: what's the moon stone condition
    set_rule(get_location("Evolution - Stellith (Sun Stone)"),
             lambda state: state.has("Stellith", player)) # todo: what's the sun stone condition
    set_rule(get_location("Evolution - Modra"),
             lambda state: state.has("Modra", player) and evolve_level(state, 40))
    set_rule(get_location("Evolution - Remoraid"),
             lambda state: state.has("Remoraid", player) and evolve_level(state, 25))
    set_rule(get_location("Evolution - Tentacool"),
             lambda state: state.has("Tentacool", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Tentacruel"),
             lambda state: state.has("Tentacruel", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Lilynary"),
             lambda state: state.has("Lilynary", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Grieflame"),
             lambda state: state.has("Grieflame", player) and evolve_level(state, 38))
    set_rule(get_location("Evolution - Strawick"),
             lambda state: state.has("Strawick", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Voltorb"),
             lambda state: state.has("Voltorb", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Electrode"),
             lambda state: state.has("Electrode", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Murkrow"),
             lambda state: state.has("Murkrow", player)) # todo: what's the moon stone condition
    set_rule(get_location("Evolution - Whismur"),
             lambda state: state.has("Whismur", player) and evolve_level(state, 20))
    set_rule(get_location("Evolution - Loudred"),
             lambda state: state.has("Loudred", player) and evolve_level(state, 40))
    set_rule(get_location("Evolution - Krabby"),
             lambda state: state.has("Krabby", player) and evolve_level(state, 28))
    set_rule(get_location("Evolution - Puffume"),
             lambda state: state.has("Puffume", player) and evolve_level(state, 31))
    set_rule(get_location("Evolution - Yolkid (Water Stone)"),
             lambda state: state.has("Yolkid", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Yolkid (Leaf Stone)"),
             lambda state: state.has("Yolkid", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Yolkid (Sun Stone)"),
             lambda state: state.has("Yolkid", player)) # todo: what's the sun stone condition
    set_rule(get_location("Evolution - Yolkid (Moon Stone)"),
             lambda state: state.has("Yolkid", player)) # todo: what's the moon stone condition
    set_rule(get_location("Evolution - Lizzle"),
             lambda state: state.has("Lizzle", player) and evolve_level(state, 33))
    set_rule(get_location("Evolution - Droudrop"),
             lambda state: state.has("Droudrop", player) and evolve_level(state, 33))
    set_rule(get_location("Evolution - Clouff"),
             lambda state: state.has("Clouff", player) and evolve_level(state, 33))
    set_rule(get_location("Evolution - Sneasel"),
             lambda state: state.has("Sneasel", player) and evolve_level(state, 38))
    set_rule(get_location("Evolution - Shroomish"),
             lambda state: state.has("Shroomish", player) and evolve_level(state, 23))
    set_rule(get_location("Evolution - Sableye"),
             lambda state: state.has("Sableye", player) and evolve_level(state, 36))
    set_rule(get_location("Evolution - Mawile"),
             lambda state: state.has("Mawile", player) and evolve_level(state, 36))
    set_rule(get_location("Evolution - Scyther"),
             lambda state: state.has("Scyther", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Pinsir"),
             lambda state: state.has("Pinsir", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Ekans"),
             lambda state: state.has("Ekans", player) and evolve_level(state, 22))
    set_rule(get_location("Evolution - Arbok"),
             lambda state: state.has("Arbok", player) and evolve_level(state, 44))
    set_rule(get_location("Evolution - Koffing"),
             lambda state: state.has("Koffing", player) and evolve_level(state, 35))
    set_rule(get_location("Evolution - Weezing"),
             lambda state: state.has("Weezing", player) and evolve_level(state, 45))
    set_rule(get_location("Evolution - Duskull"),
             lambda state: state.has("Duskull", player) and evolve_level(state, 37))
    set_rule(get_location("Evolution - Dusclops"),
             lambda state: state.has("Dusclops", player) and evolve_level(state, 48))
    set_rule(get_location("Evolution - Lickitung"),
             lambda state: state.has("Lickitung", player) and evolve_level(state, 33))
    set_rule(get_location("Evolution - Spinarak"),
             lambda state: state.has("Spinarak", player) and evolve_level(state, 22))
    set_rule(get_location("Evolution - Joltik"),
             lambda state: state.has("Joltik", player) and evolve_level(state, 36))
    set_rule(get_location("Evolution - Nincada"),
             lambda state: state.has("Nincada", player) and evolve_level(state, 20))
    set_rule(get_location("Evolution - Nincada (Extra)"),
             lambda state: state.has("Nincada", player) and evolve_level(state, 20))
    set_rule(get_location("Evolution - Guppyre"),
             lambda state: state.has("Guppyre", player) and evolve_level(state, 28))
    set_rule(get_location("Evolution - Relicanth"),
             lambda state: state.has("Relicanth", player) and evolve_level(state, 48))
    set_rule(get_location("Evolution - Punchild"),
             lambda state: state.has("Punchild", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Shuppet"),
             lambda state: state.has("Shuppet", player) and evolve_level(state, 37))
    set_rule(get_location("Evolution - Banette"),
             lambda state: state.has("Banette", player) and evolve_level(state, 47))
    set_rule(get_location("Evolution - Ralts (Level)"),
             lambda state: state.has("Ralts", player) and evolve_level(state, 20))
    set_rule(get_location("Evolution - Ralts (Friendship)"),
             lambda state: state.has("Ralts", player))
    set_rule(get_location("Evolution - Kirlia (Atk != Def)"),
             lambda state: state.has("Kirlia", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Kirlia (Atk = Def)"),
             lambda state: state.has("Kirlia", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Dwebble"),
             lambda state: state.has("Dwebble", player) and evolve_level(state, 34))
    set_rule(get_location("Evolution - Cacnea"),
             lambda state: state.has("Cacnea", player) and evolve_level(state, 32))
    set_rule(get_location("Evolution - Piloswine"),
             lambda state: state.has("Piloswine", player))
    set_rule(get_location("Evolution - Pressie"),
             lambda state: state.has("Pressie", player))
    set_rule(get_location("Evolution - Shretainer"),
             lambda state: state.has("Shretainer", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Skorupi"),
             lambda state: state.has("Skorupi", player) and evolve_level(state, 40))
    set_rule(get_location("Evolution - Carnivine"),
             lambda state: state.has("Carnivine", player) and evolve_level(state, 35))
    set_rule(get_location("Evolution - Toxroach"),
             lambda state: state.has("Toxroach", player) and evolve_level(state, 25))
    set_rule(get_location("Evolution - Dorfin (Low Personality)"),
             lambda state: state.has("Dorfin", player) and evolve_level(state, 25))
    set_rule(get_location("Evolution - Dorfin (High Personality)"),
             lambda state: state.has("Dorfin", player) and evolve_level(state, 25))
    set_rule(get_location("Evolution - Dislichen"),
             lambda state: state.has("Dislichen", player) and evolve_level(state, 33))
    set_rule(get_location("Evolution - Swinub"),
             lambda state: state.has("Swinub", player) and evolve_level(state, 33))
    set_rule(get_location("Evolution - Dunsparce"),
             lambda state: state.has("Dunsparce", player) and evolve_level(state, 42))
    set_rule(get_location("Evolution - Farfetch'd"),
             lambda state: state.has("Farfetch'd", player) and evolve_level(state, 35))
    set_rule(get_location("Evolution - Lephan"),
             lambda state: state.has("Lephan", player) and evolve_level(state, 40))
    set_rule(get_location("Evolution - Torkoal"),
             lambda state: state.has("Torkoal", player) and evolve_level(state, 45))
    set_rule(get_location("Evolution - Luvdisc"),
             lambda state: state.has("Luvdisc", player))
    set_rule(get_location("Evolution - Rooten"),
             lambda state: state.has("Rooten", player) and evolve_level(state, 29))
    set_rule(get_location("Evolution - Klink"),
             lambda state: state.has("Klink", player) and evolve_level(state, 38))
    set_rule(get_location("Evolution - Tynamo"),
             lambda state: state.has("Tynamo", player) and evolve_level(state, 39))
    set_rule(get_location("Evolution - Geodude"),
             lambda state: state.has("Geodude", player) and evolve_level(state, 25))
    set_rule(get_location("Evolution - Happiny"),
             lambda state: state.has("Happiny", player) and evolve_level(state, 20))
    set_rule(get_location("Evolution - Chansey"),
             lambda state: state.has("Chansey", player))
    set_rule(get_location("Evolution - Graveler"),
             lambda state: state.has("Graveler", player) and evolve_level(state, 38))
    set_rule(get_location("Evolution - Eelektrik"),
             lambda state: state.has("Eelektrik", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Sandshrew"),
             lambda state: state.has("Sandshrew", player) and evolve_level(state, 22))
    set_rule(get_location("Evolution - Sandslash"),
             lambda state: state.has("Sandslash", player) and evolve_level(state, 36))
    set_rule(get_location("Evolution - Scraggy"),
             lambda state: state.has("Scraggy", player) and evolve_level(state, 39))
    set_rule(get_location("Evolution - Delibird"),
             lambda state: state.has("Delibird", player) and evolve_level(state, 30))
    set_rule(get_location("Evolution - Ferroseed"),
             lambda state: state.has("Ferroseed", player) and evolve_level(state, 40))
    set_rule(get_location("Evolution - Klang"),
             lambda state: state.has("Klang", player) and evolve_level(state, 49))
    set_rule(get_location("Evolution - Petilil"),
             lambda state: state.has("Petilil", player)) # todo: what's the sun stone condition
    set_rule(get_location("Evolution - Kirgicia"),
             lambda state: state.has("Kirgicia", player)) # todo: what's the moon stone condition
    set_rule(get_location("Evolution - Sealkie"),
             lambda state: state.has("Sealkie", player) and evolve_level(state, 35))
    set_rule(get_location("Evolution - Ptervus"),
             lambda state: state.has("Ptervus", player) and evolve_level(state, 40))
    set_rule(get_location("Evolution - Ambilade (Low Personality)"),
             lambda state: state.has("Ambilade", player) and evolve_level(state, 38))
    set_rule(get_location("Evolution - Ambilade (High Personality)"),
             lambda state: state.has("Ambilade", player) and evolve_level(state, 38))
    set_rule(get_location("Evolution - Fujinel"),
             lambda state: state.has("Fujinel", player) and evolve_level(state, 24))
    set_rule(get_location("Evolution - Smalmon"),
             lambda state: state.has("Smalmon", player) and evolve_level(state, 34))
    set_rule(get_location("Evolution - Mienfoo"),
             lambda state: state.has("Mienfoo", player) and evolve_level(state, 50))
    set_rule(get_location("Evolution - Sandile"),
             lambda state: state.has("Sandile", player) and evolve_level(state, 29))
    set_rule(get_location("Evolution - Krokorok"),
             lambda state: state.has("Krokorok", player) and evolve_level(state, 40))
    set_rule(get_location("Evolution - Lukewran"),
             lambda state: state.has("Lukewran", player) and
                           state.has("Buy Evo Stones", player) and # todo: check if evo stones elsewhere in vega
                           can_grind_money(state))
    set_rule(get_location("Evolution - Aldina"),
             lambda state: state.has("Aldina", player))
