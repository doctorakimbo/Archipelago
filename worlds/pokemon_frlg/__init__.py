"""
Archipelago World definition for Pokémon Vega
"""
import copy
import logging
import os.path
import threading
import settings
import pkgutil

from typing import Any, ClassVar, Dict, List, Set, TextIO, Tuple

from BaseClasses import Tutorial, MultiWorld, ItemClassification, LocationProgressType
from Fill import fill_restrictive, FillError
from worlds.AutoWorld import WebWorld, World
from .client import PokemonVegaClient
from .data import (data as vega_data, ALL_SPECIES, LEGENDARY_POKEMON, EventData, MapData, MiscPokemonData, SpeciesData,
                   StarterData, TrainerData)
from .items import (ITEM_GROUPS, create_item_name_to_id_map, get_random_item, get_item_classification,
                    reverse_offset_item_value, PokemonVegaItem)
from .level_scaling import ScalingData, create_scaling_data, level_scaling
from .locations import (LOCATION_GROUPS, create_location_name_to_id_map, create_locations_from_tags, set_free_fly,
                        PokemonVegaLocation)
from .options import (PokemonVegaOptions, CeruleanCaveRequirement, Dexsanity, FlashRequired, FreeFlyLocation,
                      Goal, RandomizeLegendaryPokemon, RandomizeMiscPokemon, RandomizeWildPokemon,
                      ShuffleHiddenItems, ShuffleBadges, ShuffleRunningShoes, TownMapFlyLocation, Trainersanity)
from .pokemon import (randomize_abilities, randomize_legendaries, randomize_misc_pokemon, randomize_moves,
                      randomize_starters, randomize_tm_hm_compatibility, randomize_tm_moves,
                      randomize_trainer_parties, randomize_types, randomize_wild_encounters)
from .rom import get_tokens, PokemonVegaProcedurePatch
from .util import int_to_bool_array, HM_TO_COMPATIBILITY_ID


class PokemonVegaWebWorld(WebWorld):
    """
    Webhost info for Pokémon Vega
    """
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to playing Pokémon Vega with Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Dr. Akimbo"]
    )

    tutorials = [setup_en]


class PokemonVegaSettings(settings.Group):
    class PokemonVegaRomFile(settings.UserFilePath):
        """File name of your English Pokémon Vega ROM"""
        description = "Pokemon Vega ROM File"
        copy_to = "Pokemon Vega.gba"
        md5s = [PokemonVegaProcedurePatch.hash]

    vega_rom_file: PokemonVegaRomFile = PokemonVegaRomFile(PokemonVegaRomFile.copy_to)


class PokemonVegaWorld(World):
    """
    SUMMARY OF VEGA GOES HERE
    """
    game = "Pokemon Vega"
    web = PokemonVegaWebWorld()
    topology_present = True

    settings_key = "pokemon_vega_settings"
    settings: ClassVar[PokemonVegaSettings]

    options_dataclass = PokemonVegaOptions
    options: PokemonVegaOptions

    item_name_to_id = create_item_name_to_id_map()
    location_name_to_id = create_location_name_to_id_map()
    item_name_groups = ITEM_GROUPS
    location_name_groups = LOCATION_GROUPS

    required_client_version = (0, 5, 0)

    free_fly_location_id: int
    town_map_fly_location_id: int
    modified_species: Dict[int, SpeciesData]
    modified_maps: Dict[str, MapData]
    modified_starters: Dict[str, StarterData]
    modified_events: Dict[str, EventData]
    modified_legendary_pokemon: Dict[str, MiscPokemonData]
    modified_misc_pokemon: Dict[str, MiscPokemonData]
    modified_trainers: Dict[str, TrainerData]
    modified_tmhm_moves: List[int]
    hm_compatibility: Dict[str, List[str]]
    per_species_tmhm_moves: Dict[int, List[int]]
    trade_pokemon: List[Tuple[str, str]]
    blacklisted_wild_pokemon: Set[int]
    blacklisted_starters: Set[int]
    blacklisted_trainer_pokemon: Set[int]
    blacklisted_abilities: Set[int]
    blacklisted_moves: Set[int]
    trainer_name_level_dict: Dict[str, int]
    trainer_name_list: List[str]
    trainer_level_list: List[int]
    encounter_name_level_dict: Dict[str, int]
    encounter_name_list: List[str]
    encounter_level_list: List[int]
    scaling_data: List[ScalingData]
    filler_items: List[PokemonVegaItem]
    auth: bytes

    def __init__(self, multiworld, player):
        super(PokemonVegaWorld, self).__init__(multiworld, player)
        self.free_fly_location_id = 0
        self.town_map_fly_location_id = 0
        self.modified_species = copy.deepcopy(vega_data.species)
        self.modified_maps = copy.deepcopy(vega_data.maps)
        self.modified_starters = copy.deepcopy(vega_data.starters)
        self.modified_events = copy.deepcopy(vega_data.events)
        self.modified_legendary_pokemon = copy.deepcopy(vega_data.legendary_pokemon)
        self.modified_misc_pokemon = copy.deepcopy(vega_data.misc_pokemon)
        self.modified_trainers = copy.deepcopy(vega_data.trainers)
        self.modified_tmhm_moves = copy.deepcopy(vega_data.tmhm_moves)
        self.hm_compatibility = {}
        self.per_species_tmhm_moves = {}
        self.trade_pokemon = []
        self.trainer_name_level_dict = {}
        self.trainer_name_list = []
        self.trainer_level_list = []
        self.encounter_name_level_dict = {}
        self.encounter_name_list = []
        self.encounter_level_list = []
        self.scaling_data = []
        self.filler_items = []
        self.finished_level_scaling = threading.Event()

    @classmethod
    def stage_assert_generate(cls, multiworld: MultiWorld) -> None:
        from .sanity_check import validate_regions

        assert validate_regions()

    def get_filler_item_name(self) -> str:
        return get_random_item(self, ItemClassification.filler)

    def generate_early(self) -> None:
        self.blacklisted_wild_pokemon = {
            species.species_id for species in self.modified_species.values()
            if species.name in self.options.wild_pokemon_blacklist.value
        }
        if "Legendaries" in self.options.wild_pokemon_blacklist.value:
            self.blacklisted_wild_pokemon |= LEGENDARY_POKEMON

        self.blacklisted_starters = {
            species.species_id for species in self.modified_species.values()
            if species.name in self.options.starter_blacklist.value
        }
        if "Legendaries" in self.options.starter_blacklist.value:
            self.blacklisted_starters |= LEGENDARY_POKEMON

        self.blacklisted_trainer_pokemon = {
            species.species_id for species in self.modified_species.values()
            if species.name in self.options.trainer_blacklist.value
        }
        if "Legendaries" in self.options.trainer_blacklist.value:
            self.blacklisted_trainer_pokemon |= LEGENDARY_POKEMON

        self.blacklisted_abilities = {vega_data.abilities[name] for name in self.options.ability_blacklist.value}
        self.blacklisted_moves = {vega_data.moves[name] for name in self.options.move_blacklist.value}

        # Modify options that are incompatible with each other
        if self.options.exclude_sphere_ruins:
            if self.options.goal == Goal.option_asphere:
                logging.warning("Pokemon Vega: Goal for Player %s (%s) incompatible with Exclude Sphere Ruins. "
                                "Setting goal to Distant Island.", self.player, self.player_name)
                self.options.goal.value = Goal.option_distant_island

        create_scaling_data(self)
        randomize_types(self)
        randomize_abilities(self)
        randomize_moves(self)
        randomize_wild_encounters(self)
        randomize_starters(self)
        randomize_legendaries(self)
        randomize_misc_pokemon(self)
        randomize_tm_hm_compatibility(self)
        self.create_hm_compatibility_dict()

    def create_regions(self) -> None:
        from .regions import create_indirect_conditions, create_regions

        regions = create_regions(self)

        tags = {"Badge", "HM", "KeyItem", "FlyUnlock", "Overworld", "NPCGift", "RunningShoes"}
        if self.options.shuffle_hidden == ShuffleHiddenItems.option_all:
            tags.add("Hidden")
            tags.add("Recurring")
        elif self.options.shuffle_hidden == ShuffleHiddenItems.option_nonrecurring:
            tags.add("Hidden")
        if self.options.extra_key_items:
            tags.add("ExtraKeyItem")
        if self.options.trainersanity != Trainersanity.special_range_names["none"]:
            tags.add("Trainer")
        if self.options.dexsanity != Dexsanity.special_range_names["none"]:
            tags.add("Pokedex")
        create_locations_from_tags(self, regions, tags)

        self.multiworld.regions.extend(regions.values())

        create_indirect_conditions(self)

        def exclude_locations(locations: List[str]):
            for location in locations:
                try:
                    self.multiworld.get_location(location, self.player).progress_type = LocationProgressType.EXCLUDED
                except KeyError:
                    continue

        if self.options.goal == Goal.option_elite_four:
            exclude_locations("Champion's Room - Champion Reward")

    def create_items(self) -> None:
        item_locations: List[PokemonVegaLocation] = [
            location for location in self.multiworld.get_locations(self.player) if location.address is not None
        ]

        if not self.options.shuffle_badges:
            item_locations = [location for location in item_locations if "Badge" not in location.tags]
        if not self.options.shuffle_fly_destination_unlocks:
            item_locations = [location for location in item_locations if "FlyUnlock" not in location.tags]
        if self.options.shuffle_running_shoes == ShuffleRunningShoes.option_vanilla:
            item_locations = [location for location in item_locations if "RunningShoes" not in location.tags]

        itempool = [self.create_item_by_id(location.default_item_id) for location in item_locations]

        for item, quantity in self.options.start_inventory.value.items():
            if "Unique" in vega_data.items[reverse_offset_item_value(self.item_name_to_id[item])].tags:
                removed_items_count = 0
                for _ in range(quantity):
                    try:
                        item_to_remove = next(i for i in itempool if i.name == item)
                        itempool.remove(item_to_remove)
                        removed_items_count += 1
                    except StopIteration:
                        break
                while removed_items_count > 0:
                    itempool.append(self.create_item(get_random_item(self, ItemClassification.filler)))
                    removed_items_count -= 1

        self.filler_items = [item for item in itempool if item.classification == ItemClassification.filler]
        self.random.shuffle(self.filler_items)
        self.multiworld.itempool += itempool

    def set_rules(self) -> None:
        from .rules import set_rules
        set_rules(self)

    def generate_basic(self) -> None:
        # Create auth
        self.auth = self.random.getrandbits(16 * 8).to_bytes(16, "little")

        set_free_fly(self)

        def create_events_for_unrandomized_items(tag: str) -> None:
            locations = [location for location in self.multiworld.get_locations(self.player)
                         if tag in location.tags]
            for location in locations:
                location.place_locked_item(PokemonVegaItem(self.item_id_to_name[location.default_item_id],
                                                           ItemClassification.progression,
                                                           None,
                                                           self.player))
                location.progress_type = LocationProgressType.DEFAULT
                location.address = None
                location.show_in_spoiler = False

        if not self.options.shuffle_fly_destination_unlocks:
            create_events_for_unrandomized_items("FlyUnlock")
        if self.options.shuffle_running_shoes == ShuffleRunningShoes.option_vanilla:
            create_events_for_unrandomized_items("RunningShoes")

        collection_state = self.multiworld.get_all_state(False)

        # Delete evolutions that are not in logic in an all_state so that the accessibility check doesn't fail
        evolution_region = self.multiworld.get_region("Evolutions", self.player)
        for location in evolution_region.locations.copy():
            if not collection_state.can_reach(location, player=self.player):
                evolution_region.locations.remove(location)

        # Delete trades that are not in logic in an all_state so that the accessibility check doesn't fail
        for trade in self.trade_pokemon:
            location = self.multiworld.get_location(trade[1], self.player)
            if not collection_state.can_reach(location, player=self.player):
                region = self.multiworld.get_region(trade[0], self.player)
                region.locations.remove(location)

        # Delete trainersanity locations if there are more than the amount specified in the settings
        trainer_locations = [loc for loc in self.multiworld.get_locations(self.player)
                             if "Trainer" in loc.tags
                             and not loc.is_event]
        locs_to_remove = len(trainer_locations) - self.options.trainersanity.value
        if locs_to_remove > 0:
            self.random.shuffle(trainer_locations)
            for location in trainer_locations:
                region = location.parent_region
                region.locations.remove(location)
                item_to_remove = self.filler_items.pop(0)
                self.multiworld.itempool.remove(item_to_remove)
                locs_to_remove -= 1
                if locs_to_remove <= 0:
                    break

        # Delete dexsanity locations that are not in logic in an all_state since they aren't accessible
        pokedex_region = self.multiworld.get_region("Pokedex", self.player)
        for location in pokedex_region.locations.copy():
            if not collection_state.can_reach(location, player=self.player):
                pokedex_region.locations.remove(location)
                item_to_remove = self.filler_items.pop(0)
                self.multiworld.itempool.remove(item_to_remove)

        # Delete dexsanity locations if there are more than the amount specified in the settings
        if len(pokedex_region.locations) > self.options.dexsanity.value:
            pokedex_region_locations = pokedex_region.locations.copy()
            self.random.shuffle(pokedex_region_locations)
            for location in pokedex_region_locations:
                pokedex_region.locations.remove(location)
                item_to_remove = self.filler_items.pop(0)
                self.multiworld.itempool.remove(item_to_remove)
                if len(pokedex_region.locations) <= self.options.dexsanity.value:
                    break

    def pre_fill(self) -> None:
        # If badges aren't shuffled among all locations, shuffle them among themselves
        if not self.options.shuffle_badges:
            badge_locations: List[PokemonVegaLocation] = [
                location for location in self.multiworld.get_locations(self.player) if "Badge" in location.tags
            ]
            badge_items: List[PokemonVegaItem] = [
                self.create_item_by_id(location.default_item_id) for location in badge_locations
            ]

            collection_state = self.multiworld.get_all_state(False)

            attempts_remaining = 2
            while attempts_remaining > 0:
                attempts_remaining -= 1
                self.random.shuffle(badge_locations)
                try:
                    fill_restrictive(self.multiworld, collection_state, badge_locations, badge_items,
                                     single_player_placement=True, lock=True, allow_excluded=True)
                    break
                except FillError as exc:
                    if attempts_remaining == 0:
                        raise exc

    @classmethod
    def stage_post_fill(cls, multiworld):
        # Change all but one instance of a Pokémon in each sphere to useful classification
        # This cuts down on time calculating the playthrough
        found_mons = set()
        pokemon = {species.name for species in vega_data.species.values()}
        for sphere in multiworld.get_spheres():
            for location in sphere:
                if (location.game == "Pokemon Vega" and
                        location.item.game == "Pokemon Vega" and
                        (location.item.name in pokemon or "Static " in location.item.name)
                        and location.item.advancement):
                    key = (location.player, location.item.name)
                    if key in found_mons:
                        location.item.classification = ItemClassification.useful
                    else:
                        found_mons.add(key)

    @classmethod
    def stage_generate_output(cls, multiworld, output_directory):
        level_scaling(multiworld)

    def generate_output(self, output_directory: str) -> None:
        # Modify catch rate
        min_catch_rate = min(self.options.min_catch_rate.value, 255)
        for species in self.modified_species.values():
            species.catch_rate = max(species.catch_rate, min_catch_rate)

        self.finished_level_scaling.wait()

        randomize_tm_moves(self)
        randomize_trainer_parties(self)

        patch = PokemonVegaProcedurePatch(player=self.player, player_name=self.player_name)
        patch.write_file("base_patch.bsdiff4", pkgutil.get_data(__name__, "data/base_patch.bsdiff4"))

        tokens = get_tokens(self)

        patch.write_file("token_data.bin", tokens.get_token_binary())

        # Write output
        out_file_name = self.multiworld.get_out_file_name_base(self.player)
        patch.write(os.path.join(output_directory, f"{out_file_name}{patch.patch_file_ending}"))

        del self.modified_species
        del self.modified_maps
        del self.modified_starters
        del self.modified_events
        del self.modified_legendary_pokemon
        del self.modified_misc_pokemon
        del self.trade_pokemon
        del self.trainer_name_level_dict
        del self.trainer_name_list
        del self.trainer_level_list
        del self.encounter_name_level_dict
        del self.encounter_name_list
        del self.encounter_level_list
        del self.scaling_data

    def write_spoiler_header(self, spoiler_handle: TextIO) -> None:
        if self.options.free_fly_location != FreeFlyLocation.option_off:
            free_fly_location = self.multiworld.get_location("Free Fly Location", self.player)
            spoiler_handle.write(f"Free Fly Location:               {free_fly_location.item.name[4:]}\n")
        if self.options.town_map_fly_location != TownMapFlyLocation.option_off:
            town_map_fly_location = self.multiworld.get_location("Town Map Fly Location", self.player)
            spoiler_handle.write(f"Town Map Fly Location:           {town_map_fly_location.item.name[4:]}\n")

    def write_spoiler(self, spoiler_handle: TextIO) -> None:
        # Add Pokémon locations to the spoiler log if they are not vanilla
        if (self.options.wild_pokemon != RandomizeWildPokemon.option_vanilla or
                self.options.misc_pokemon != RandomizeMiscPokemon.option_vanilla or
                self.options.legendary_pokemon != RandomizeLegendaryPokemon.option_vanilla):
            spoiler_handle.write(f"\n\nPokemon Locations ({self.multiworld.player_name[self.player]}):\n\n")

            from collections import defaultdict

            species_locations = defaultdict(set)

            if self.options.wild_pokemon != RandomizeWildPokemon.option_vanilla:
                pokemon_locations: List[PokemonVegaLocation] = [
                    location for location in self.multiworld.get_locations(self.player)
                    if "Pokemon" in location.tags and "Wild" in location.tags
                ]
                for location in pokemon_locations:
                    species_locations[location.item.name].add(location.spoiler_name)

            if self.options.misc_pokemon != RandomizeMiscPokemon.option_vanilla:
                pokemon_locations: List[PokemonVegaLocation] = [
                    location for location in self.multiworld.get_locations(self.player)
                    if "Pokemon" in location.tags and "Misc" in location.tags
                ]
                for location in pokemon_locations:
                    if location.item.name.startswith("Missable"):
                        continue
                    species_locations[location.item.name.replace("Static ", "")].add(location.spoiler_name)

            if self.options.legendary_pokemon != RandomizeLegendaryPokemon.option_vanilla:
                pokemon_locations: List[PokemonVegaLocation] = [
                    location for location in self.multiworld.get_locations(self.player)
                    if "Pokemon" in location.tags and "Legendary" in location.tags
                ]
                for location in pokemon_locations:
                    if location.item.name.startswith("Missable"):
                        continue
                    species_locations[location.item.name.replace("Static ", "")].add(location.spoiler_name)

            lines = [f"{species}: {', '.join(sorted(locations))}\n"
                     for species, locations in species_locations.items()]
            lines.sort()
            for line in lines:
                spoiler_handle.write(line)

    def extend_hint_information(self, hint_data):
        if self.options.dexsanity != Dexsanity.special_range_names["none"]:
            from collections import defaultdict

            species_locations = defaultdict(set)

            pokemon_locations: List[PokemonVegaLocation] = [
                location for location in self.multiworld.get_locations(self.player)
                if "Pokemon" in location.tags and "Wild" in location.tags
            ]
            for location in pokemon_locations:
                species_locations[location.item.name].add(location.spoiler_name)

            pokemon_locations: List[PokemonVegaLocation] = [
                location for location in self.multiworld.get_locations(self.player)
                if "Pokemon" in location.tags and "Misc" in location.tags
            ]
            for location in pokemon_locations:
                if location.item.name.startswith("Missable"):
                    continue
                species_locations[location.item.name.replace("Static ", "")].add(location.spoiler_name)

            pokemon_locations: List[PokemonVegaLocation] = [
                location for location in self.multiworld.get_locations(self.player)
                if "Pokemon" in location.tags and "Legendary" in location.tags
            ]
            for location in pokemon_locations:
                if location.item.name.startswith("Missable"):
                    continue
                species_locations[location.item.name.replace("Static ", "")].add(location.spoiler_name)

            hint_data[self.player] = {
                self.location_name_to_id[f"Pokedex - {species}"]: ", ".join(sorted(maps))
                for species, maps in species_locations.items()
            }

    def modify_multidata(self, multidata: Dict[str, Any]):
        import base64
        multidata["connect_names"][base64.b64encode(self.auth).decode("ascii")] = \
            multidata["connect_names"][self.player_name]

    def fill_slot_data(self) -> Dict[str, Any]:
        slot_data = self.options.as_dict(
            "goal",
            "exclude_sphere_ruins",
            "shuffle_badges",
            "shuffle_hidden",
            "extra_key_items",
            "shuffle_fly_destination_unlocks",
            "itemfinder_required",
            "flash_required",
            "remove_badge_requirement",
            "junopsis_city_roadblock",
            "modify_world_state",
            "additional_dark_caves",
            "route523_guard_requirement",
            "route523_guard_count",
            "elite_four_requirement",
            "elite_four_count",
            "elite_four_rematch_count",
            "cerulean_cave_requirement",
            "cerulean_cave_count",
            "provide_hints"
        )
        slot_data["trainersanity"] = 1 if self.options.trainersanity != Trainersanity.special_range_names["none"] else 0
        slot_data["elite_four_rematch_requirement"] = self.options.elite_four_requirement.value
        slot_data["free_fly_location_id"] = self.free_fly_location_id
        slot_data["town_map_fly_location_id"] = self.town_map_fly_location_id
        return slot_data

    def create_item(self, name: str) -> "PokemonVegaItem":
        return self.create_item_by_id(self.item_name_to_id[name])

    def create_item_by_id(self, item_id: int):
        return PokemonVegaItem(
            self.item_id_to_name[item_id],
            get_item_classification(item_id),
            item_id,
            self.player
        )

    def create_hm_compatibility_dict(self):
        hms = frozenset({"Cut", "Fly", "Surf", "Strength", "Flash", "Rock Smash", "Waterfall"})
        for hm in hms:
            self.hm_compatibility[hm] = list()
            for species in self.modified_species.values():
                combatibility_array = int_to_bool_array(species.tm_hm_compatibility)
                if combatibility_array[HM_TO_COMPATIBILITY_ID[hm]] == 1:
                    self.hm_compatibility[hm].append(species.name)
