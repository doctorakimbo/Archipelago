"""
Archipelago World definition for Pokemon FireRed/LeafGreen
"""
import copy
import settings
import pkgutil
from typing import ClassVar, List, Dict, Any
from BaseClasses import Tutorial, MultiWorld, ItemClassification
from Fill import fill_restrictive, FillError
from worlds.AutoWorld import WebWorld, World
from .client import PokemonFRLGClient
from .data import data as frlg_data, SpeciesData
from .items import create_item_name_to_id_map, get_item_classification, PokemonFRLGItem
from .locations import create_location_name_to_id_map, create_locations_from_tags, set_free_fly, PokemonFRLGLocation
from .options import (PokemonFRLGOptions, GameVersion, GameRevision, ShuffleHiddenItems, ShuffleBadges,
                      ViridianCityRoadblock)
from .rom import (generate_output, PokemonFireRedProcedurePatch, PokemonFireRedRev1ProcedurePatch,
                  PokemonLeafGreenProcedurePatch, PokemonLeafGreenRev1ProcedurePatch)
from .util import int_to_bool_array, HM_TO_COMPATABILITY_ID


class PokemonFRLGWebWorld(WebWorld):
    """
    Webhost info for Pokemon FireRed and LeafGreen
    """
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to playing Pokémon FireRed and LeafGreen with Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Vyneras"]
    )

    tutorials = [setup_en]


class PokemonFRLGSettings(settings.Group):
    class PokemonFireRedRomFile(settings.UserFilePath):
        """File name of your English Pokemon FireRed ROM"""
        description = "Pokemon FireRed ROM File"
        copy_to = "Pokemon - FireRed Version (USA, Europe).gba"
        md5s = [PokemonFireRedProcedurePatch.hash]

    class PokemonFireRedRev1RomFile(settings.UserFilePath):
        """File name of your English Pokemon FireRed (Rev 1) ROM"""
        description = "Pokemon FireRed (Rev 1) ROM File"
        copy_to = "Pokemon - FireRed Version (USA, Europe) (Rev 1).gba"
        md5s = [PokemonFireRedRev1ProcedurePatch.hash]

    class PokemonLeafGreenRomFile(settings.UserFilePath):
        """File name of your English Pokemon LeafGreen ROM"""
        description = "Pokemon LeafGreen ROM File"
        copy_to = "Pokemon - LeafGreen Version (USA, Europe).gba"
        md5s = [PokemonLeafGreenProcedurePatch.hash]

    class PokemonLeafGreenRev1RomFile(settings.UserFilePath):
        """File name of your English Pokemon LeafGreen (Rev 1) ROM"""
        description = "Pokemon LeafGreen (Rev 1) ROM File"
        copy_to = "Pokemon - LeafGreen Version (USA, Europe) (Rev 1).gba"
        md5s = [PokemonLeafGreenRev1ProcedurePatch.hash]

    firered_rom_file: PokemonFireRedRomFile = PokemonFireRedRomFile(PokemonFireRedRomFile.copy_to)
    firered_rev1_rom_file: PokemonFireRedRev1RomFile = PokemonFireRedRev1RomFile(PokemonFireRedRev1RomFile.copy_to)
    leafgreen_rom_file: PokemonLeafGreenRomFile = PokemonLeafGreenRomFile(PokemonLeafGreenRomFile.copy_to)
    leafgreen_rev1_rom_file: PokemonLeafGreenRev1RomFile = PokemonLeafGreenRev1RomFile(PokemonLeafGreenRev1RomFile.copy_to)


class PokemonFRLGWorld(World):
    """
    Pokémon FireRed and LeafGreen are remakes of the very first Pokémon games.
    Experience the Kanto region with several updated features from Gen III.
    Catch, train, and battle Pokémon, face off against the evil organization Team Rocket, challenge Gyms in order to
    earn Badges, help resolve the many crises on the Sevii Islands, and become the Pokémon Champion!
    """
    game = "Pokemon FireRed and LeafGreen"
    web = PokemonFRLGWebWorld()
    topology_present = True

    settings_key = "pokemon_frlg_settings"
    settings: ClassVar[PokemonFRLGSettings]

    options_dataclass = PokemonFRLGOptions
    options: PokemonFRLGOptions

    item_name_to_id = create_item_name_to_id_map()
    location_name_to_id = create_location_name_to_id_map()

    required_client_version = (0, 5, 0)

    free_fly_location_id: int
    modified_species: Dict[int, SpeciesData]
    hm_compatability: Dict[str, List[str]]
    auth: bytes

    def __init__(self, multiworld, player):
        super(PokemonFRLGWorld, self).__init__(multiworld, player)
        self.free_fly_location_id = 0
        self.modified_species = copy.deepcopy(frlg_data.species)
        self.hm_compatability = {}

    @classmethod
    def stage_assert_generate(cls, multiworld: MultiWorld) -> None:
        from .sanity_check import validate_regions

        assert validate_regions()

    def get_filler_item_name(self) -> str:
        return "Poke Ball"

    def create_regions(self) -> None:
        from .regions import create_regions

        regions = create_regions(self)

        tags = {"Badge", "HM", "KeyItem", "Overworld", "NPCGift"}
        if self.options.shuffle_hidden == ShuffleHiddenItems.option_all:
            tags.add("Hidden")
            tags.add("HiddenRecurring")
        elif self.options.shuffle_hidden == ShuffleHiddenItems.option_nonrecurring:
            tags.add("Hidden")
        create_locations_from_tags(self, regions, tags)

        self.multiworld.regions.extend(regions.values())

    def create_items(self) -> None:
        item_locations: List[PokemonFRLGLocation] = [
            location for location in self.multiworld.get_locations(self.player) if location.address is not None
        ]

        if not self.options.shuffle_badges:
            item_locations = [location for location in item_locations if "Badge" not in location.tags]

        itempool = [self.create_item_by_id(location.default_item_id) for location in item_locations]
        self.multiworld.itempool += itempool

    def generate_early(self) -> None:
        self.create_hm_compatability_dict()

    def set_rules(self) -> None:
        from .rules import set_rules
        set_rules(self)

    def generate_basic(self) -> None:
        # Create auth
        self.auth = self.random.getrandbits(16 * 8).to_bytes(16, "little")

        set_free_fly(self)

    def pre_fill(self) -> None:
        # If badges aren't shuffled among all locations, shuffle them among themselves
        if not self.options.shuffle_badges:
            badge_locations: List[PokemonFRLGLocation] = [
                location for location in self.multiworld.get_locations(self.player) if "Badge" in location.tags
            ]
            badge_items: List[PokemonFRLGItem] = [
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

        if self.options.viridian_city_roadblock == ViridianCityRoadblock.option_early_parcel:
            self.multiworld.local_early_items[self.player]["Oak's Parcel"] = 1

        # Delete evolutions that are not in logic in an all_state so that the accessibility check doesn't fail
        collection_state = self.multiworld.get_all_state(False)
        evolution_region = self.multiworld.get_region("Evolution", self.player)
        for location in evolution_region.locations.copy():
            if not collection_state.can_reach(location, player=self.player):
                evolution_region.locations.remove(location)

        # Delete trades that are not in logic in an all_state so that the accessibility check doesn't fail
        electrode_trade_location = self.multiworld.get_location("Cinnabar Pokemon Lab Lounge - Trade Raichu",
                                                                self.player)
        if not collection_state.can_reach(electrode_trade_location, player=self.player):
            region = self.multiworld.get_region("Cinnabar Pokemon Lab Lounge", self.player)
            region.locations.remove(electrode_trade_location)

        if self.options.game_version == GameVersion.option_firered:
            lickitung_trade_location = self.multiworld.get_location("Route 18 East Entrance 2F - Trade Golduck",
                                                                    self.player)
        else:
            lickitung_trade_location = self.multiworld.get_location("Route 18 East Entrance 2F - Trade Slowbro",
                                                                    self.player)
        if not collection_state.can_reach(lickitung_trade_location, player=self.player):
            region = self.multiworld.get_region("Route 18 East Entrance 2F", self.player)
            region.locations.remove(lickitung_trade_location)

    def generate_output(self, output_directory: str) -> None:
        # Modify catch rate
        min_catch_rate = min(self.options.min_catch_rate.value, 255)
        for species in self.modified_species.values():
            species.catch_rate = max(species.catch_rate, min_catch_rate)

        if self.options.game_version == GameVersion.option_firered:
            if self.options.game_revision == GameRevision.option_rev0:
                patch = PokemonFireRedProcedurePatch(player=self.player, player_name=self.player_name)
                patch.write_file("base_patch_firered.bsdiff4",
                                 pkgutil.get_data(__name__, "data/base_patch_firered.bsdiff4"))
            else:
                patch = PokemonFireRedRev1ProcedurePatch(player=self.player, player_name=self.player_name)
                patch.write_file("base_patch_firered_rev1.bsdiff4",
                                 pkgutil.get_data(__name__, "data/base_patch_firered_rev1.bsdiff4"))
        else:
            if self.options.game_revision == GameRevision.option_rev0:
                patch = PokemonLeafGreenProcedurePatch(player=self.player, player_name=self.player_name)
                patch.write_file("base_patch_leafgreen.bsdiff4",
                                 pkgutil.get_data(__name__, "data/base_patch_leafgreen.bsdiff4"))
            else:
                patch = PokemonLeafGreenRev1ProcedurePatch(player=self.player, player_name=self.player_name)
                patch.write_file("base_patch_leafgreen_rev1.bsdiff4",
                                 pkgutil.get_data(__name__, "data/base_patch_leafgreen_rev1.bsdiff4"))

        generate_output(self, patch, output_directory)

    @classmethod
    def stage_post_fill(cls, multiworld):
        # Change all but one instance of a pokemon in each sphere to useful classification
        # This cuts down on time calculating the playthrough
        found_mons = set()
        pokemon = set()
        for species in frlg_data.species.values():
            pokemon.add(species.name)
        for sphere in multiworld.get_spheres():
            for location in sphere:
                if (location.game == "Pokemon FireRed and LeafGreen" and
                        (location.item.name in pokemon or "Static " in location.item.name)
                        and location.item.advancement):
                    key = (location.player, location.item.name)
                    if key in found_mons:
                        location.item.classification = ItemClassification.useful
                    else:
                        found_mons.add(key)

    def modify_multidata(self, multidata: Dict[str, Any]):
        import base64
        multidata["connect_names"][base64.b64encode(self.auth).decode("ascii")] = \
            multidata["connect_names"][self.player_name]

    def fill_slot_data(self) -> Dict[str, Any]:
        slot_data = self.options.as_dict(
            "game_version",
            "shuffle_badges",
            "shuffle_hidden",
            "itemfinder_required",
            "flash_required",
            "oaks_aide_route_2",
            "oaks_aide_route_10",
            "oaks_aide_route_11",
            "oaks_aide_route_16",
            "oaks_aide_route_15",
            "viridian_city_roadblock",
            "pewter_city_roadblock",
            "cerulean_city_roadblocks",
            "viridian_gym_requirement",
            "viridian_gym_count",
            "route22_gate_requirement",
            "route22_gate_count",
            "route23_guard_requirement",
            "route23_guard_count",
            "elite_four_requirement",
            "elite_four_count",
            "cerulean_cave_requirement",
            "cerulean_cave_count",
        )
        slot_data["free_fly_location_id"] = self.free_fly_location_id
        return slot_data

    def create_item(self, name: str) -> "PokemonFRLGItem":
        return self.create_item_by_id(self.item_name_to_id[name])

    def create_item_by_id(self, item_id: int):
        return PokemonFRLGItem(
            self.item_id_to_name[item_id],
            get_item_classification(item_id),
            item_id,
            self.player
        )

    def create_hm_compatability_dict(self):
        hms = frozenset(["Cut", "Fly", "Surf", "Strength", "Flash", "Rock Smash", "Waterfall"])
        for hm in hms:
            self.hm_compatability[hm] = list()
            for species in frlg_data.species.values():
                combatibility_array = int_to_bool_array(species.tm_hm_compatibility)
                if combatibility_array[HM_TO_COMPATABILITY_ID[hm]] == 1:
                    self.hm_compatability[hm].append(species.name)
