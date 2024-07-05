"""
Classes and functions related to creating a ROM patch
"""
import struct

import logging
from typing import TYPE_CHECKING, List, Tuple, Union
from worlds.Files import APProcedurePatch, APTokenMixin, APTokenTypes
from settings import get_settings
from .data import data
from .items import reverse_offset_item_value
from .options import GameRevision, ItemfinderRequired, ShuffleHiddenItems, ViridianCityRoadblock
if TYPE_CHECKING:
    from . import PokemonFRLGWorld


class PokemonFireRedProcedurePatch(APProcedurePatch, APTokenMixin):
    game = "Pokemon FireRed and LeafGreen"
    hash = "e26ee0d44e809351c8ce2d73c7400cdd"
    patch_file_ending = ".apfirered"
    result_file_ending = ".gba"

    procedure = [
        ("apply_bsdiff4", ["base_patch_firered.bsdiff4"]),
        ("apply_tokens", ["token_data.bin"])
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        with open(get_settings().pokemon_frlg_settings.firered_rom_file, "rb") as infile:
            base_rom_bytes = bytes(infile.read())

        return base_rom_bytes


class PokemonFireRedRev1ProcedurePatch(APProcedurePatch, APTokenMixin):
    game = "Pokemon FireRed and LeafGreen"
    hash = "51901a6e40661b3914aa333c802e24e8"
    patch_file_ending = ".apfireredrev1"
    result_file_ending = ".gba"

    procedure = [
        ("apply_bsdiff4", ["base_patch_firered_rev1.bsdiff4"]),
        ("apply_tokens", ["token_data.bin"])
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        with open(get_settings().pokemon_frlg_settings.firered_rev1_rom_file, "rb") as infile:
            base_rom_bytes = bytes(infile.read())

        return base_rom_bytes


class PokemonLeafGreenProcedurePatch(APProcedurePatch, APTokenMixin):
    game = "Pokemon FireRed and LeafGreen"
    hash = "612ca9473451fa42b51d1711031ed5f6"
    patch_file_ending = ".apleafgreen"
    result_file_ending = ".gba"

    procedure = [
        ("apply_bsdiff4", ["base_patch_leafgreen.bsdiff4"]),
        ("apply_tokens", ["token_data.bin"])
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        with open(get_settings().pokemon_frlg_settings.leafgreen_rom_file, "rb") as infile:
            base_rom_bytes = bytes(infile.read())

        return base_rom_bytes


class PokemonLeafGreenRev1ProcedurePatch(APProcedurePatch, APTokenMixin):
    game = "Pokemon FireRed and LeafGreen"
    hash = "9d33a02159e018d09073e700e1fd10fd"
    patch_file_ending = ".apleafgreenrev1"
    result_file_ending = ".gba"

    procedure = [
        ("apply_bsdiff4", ["base_patch_leafgreen_rev1.bsdiff4"]),
        ("apply_tokens", ["token_data.bin"])
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        with open(get_settings().pokemon_frlg_settings.leafgreen_rev1_rom_file, "rb") as infile:
            base_rom_bytes = bytes(infile.read())

        return base_rom_bytes


def write_tokens(world: "PokemonFRLGWorld",
                 patch: Union[PokemonFireRedProcedurePatch,
                              PokemonFireRedRev1ProcedurePatch,
                              PokemonLeafGreenProcedurePatch,
                              PokemonLeafGreenRev1ProcedurePatch]) -> None:
    game_version = world.options.game_version.current_key
    if world.options.game_revision == GameRevision.option_rev0:
        game_version_revision = game_version
    else:
        game_version_revision = f'{game_version}_rev1'

    # Set free fly location
    if world.options.free_fly_location:
        patch.write_token(
            APTokenTypes.WRITE,
            data.rom_addresses[game_version_revision]["gArchipelagoOptions"] + 0x18,
            struct.pack("<B", world.free_fly_location_id)
        )

    # Set item values
    for location in world.multiworld.get_locations(world.player):
        if location.address is None:
            continue

        if location.item.player == world.player:
            patch.write_token(
                APTokenTypes.WRITE,
                location.item_address[game_version_revision],
                struct.pack("<H", reverse_offset_item_value(location.item.code))
            )
        else:
            patch.write_token(
                APTokenTypes.WRITE,
                location.item_address[game_version_revision],
                struct.pack("<H", data.constants["ITEM_ARCHIPELAGO_PROGRESSION"])
            )

    # Set starting items
    start_inventory = world.options.start_inventory.value.copy()

    starting_badges = 0
    if start_inventory.pop("Boulder Badge", 0) > 0:
        starting_badges |= (1 << 0)
    if start_inventory.pop("Cascade Badge", 0) > 0:
        starting_badges |= (1 << 1)
    if start_inventory.pop("Thunder Badge", 0) > 0:
        starting_badges |= (1 << 2)
    if start_inventory.pop("Rainbow Badge", 0) > 0:
        starting_badges |= (1 << 3)
    if start_inventory.pop("Soul Badge", 0) > 0:
        starting_badges |= (1 << 4)
    if start_inventory.pop("Marsh Badge", 0) > 0:
        starting_badges |= (1 << 5)
    if start_inventory.pop("Volcano Badge", 0) > 0:
        starting_badges |= (1 << 6)
    if start_inventory.pop("Earth Badge", 0) > 0:
        starting_badges |= (1 << 7)

    pc_slots: List[Tuple[str, int]] = []
    for item, quantity in start_inventory.items():
        if len(pc_slots) >= 19:
            break
        if quantity > 999:
            logging.info(
                f"{world.multiworld.get_file_safe_player_name(world.player)} cannot have more than 999 of an item"
                f"Changing amount to 999"
            )
            quantity = 999
        pc_slots.append([item, quantity])

    for i, slot in enumerate(pc_slots, 1):
        address = data.rom_addresses[game_version_revision]["gNewGamePCItems"] + (i * 4)
        item = reverse_offset_item_value(world.item_name_to_id[slot[0]])
        patch.write_token(APTokenTypes.WRITE, address, struct.pack("<H", item))
        patch.write_token(APTokenTypes.WRITE, address + 2, struct.pack("<H", slot[1]))

    # Set species data
    for species in world.modified_species.values():
        if species is not None:
            address = species.address[game_version_revision]
            patch.write_token(APTokenTypes.WRITE, address + 8, struct.pack("<B", species.catch_rate))

    # Options
    # struct
    # ArchipelagoOptions
    # {
    # / *0x00* / bool8 advanceTextWithHoldA;
    # / *0x01* / u8 receivedItemMessageFilter; // 0 = Show All, 1 = Show Progression Only, 2 = Show None
    # / *0x02* / bool8 betterShopsEnabled;
    # / *0x03* / bool8 reusableTms;
    # / *0x04* / bool8 guaranteedCatch;
    #
    # / *0x05* / bool8 areTrainersBlind;
    # / *0x06* / u16 expMultiplierNumerator;
    # / *0x08* / u16 expMultiplierDenominator;
    #
    # / *0x0A* / bool8 openViridianCity;
    # / *0x0B* / u8 route3Requirement; // 0 = Open, 1 = Defeat Brock, 2 = Defeat Any Gym Leader,
    #                                     3 = Boulder Badge, 4 = Any Badge
    # / *0x0C* / bool8 saveBillRequired;
    # / *0x0D* / bool8 giovanniRequiresGyms;
    # / *0x0E* / u8 giovanniRequiredCount;
    # / *0x0F* / bool8 route22GateRequiresGyms;
    # / *0x10* / u8 route22GateRequiredCount;
    # / *0x11* / bool8 route23GuardRequiresGyms;
    # / *0x12* / u8 route23GuardRequiredCount;
    # / *0x13* / bool8 eliteFourRequiresGyms;
    # / *0x14* / u8 eliteFourRequiredCount;
    # / *0x15* / u8 ceruleanCaveRequirement; // 0 = Vanilla, 1 = Become Champion, 2 = Restore Network Center,
    #                                           3 = Badges, 4 = Gyms
    # / *0x16* / u8 ceruleanCaveRequiredCount;
    #
    # / *0x17* / u8 startingBadges;
    # / *0x18* / u8 freeFlyLocation;
    #
    # / *0x19* / bool8 itemfinderRequired;
    # / *0x1A* / bool8 reccuringHiddenItems;
    #
    # / *0x1B* / u8 oaksAideRequiredCounts[5]; // Route 2, Route 10, Route 11, Route 16, Route 15
    # }
    options_address = data.rom_addresses[game_version_revision]["gArchipelagoOptions"]

    # Set hold A to advance text
    turbo_a = 1 if world.options.turbo_a else 0
    patch.write_token(APTokenTypes.WRITE, options_address + 0x00, struct.pack("<B", turbo_a))

    # Set received item message types
    receive_item_messages = world.options.receive_item_messages.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x01, struct.pack("<B", receive_item_messages))

    # Set better shops
    better_shops = 1 if world.options.better_shops else 0
    patch.write_token(APTokenTypes.WRITE, options_address + 0x02, struct.pack("<B", better_shops))

    # Set reusable TMs and Move Tutors
    reusable_tm_tutors = 1 if world.options.reusable_tm_tutors else 0
    patch.write_token(APTokenTypes.WRITE, options_address + 0x03, struct.pack("<B", reusable_tm_tutors))

    # Set guaranteed catch
    guaranteed_catch = 1 if world.options.guaranteed_catch else 0
    patch.write_token(APTokenTypes.WRITE, options_address + 0x04, struct.pack("<B", guaranteed_catch))

    # Set blind trainers
    blind_trainers = 1 if world.options.blind_trainers else 0
    patch.write_token(APTokenTypes.WRITE, options_address + 0x05, struct.pack("<B", blind_trainers))

    # Set exp multiplier
    numerator = world.options.exp_modifier.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x06, struct.pack("<H", numerator))
    patch.write_token(APTokenTypes.WRITE, options_address + 0x08, struct.pack("<H", 100))

    # Set Viridian City roadblock
    open_viridian = 1 if world.options.viridian_city_roadblock.value == ViridianCityRoadblock.option_open else 0
    patch.write_token(APTokenTypes.WRITE, options_address + 0x0A, struct.pack("<B", open_viridian))

    # Set Pewter City roadblock
    route_3_condition = world.options.pewter_city_roadblock.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x0B, struct.pack("<B", route_3_condition))

    # Set Cerulean City roadblocs
    save_bill = 1 if world.options.cerulean_city_roadblocks else 0
    patch.write_token(APTokenTypes.WRITE, options_address + 0x0C, struct.pack("<B", save_bill))

    # Set Viridian Gym Rrquirement
    viridian_gym_requirement = world.options.viridian_gym_requirement.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x0D, struct.pack("<B", viridian_gym_requirement))

    # Set Viridian Gym count
    viridian_gym_count = world.options.viridian_gym_count.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x0E, struct.pack("<B", viridian_gym_count))

    # Set Route 22 requirement
    route_22_requirement = world.options.route22_gate_requirement.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x0F, struct.pack("<B", route_22_requirement))

    # Set Route 22 count
    route_22_count = world.options.route22_gate_count.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x10, struct.pack("<B", route_22_count))

    # Set Route 23 requirement
    route_23_requirement = world.options.route23_guard_requirement.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x11, struct.pack("<B", route_23_requirement))

    # Set Route 23 count
    route_23_count = world.options.route23_guard_count.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x12, struct.pack("<B", route_23_count))

    # Set Elite Four requirement
    elite_four_requirement = world.options.elite_four_requirement.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x13, struct.pack("<B", elite_four_requirement))

    # Set Elite Four count
    elite_four_count = world.options.elite_four_count.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x14, struct.pack("<B", elite_four_count))

    # Set Cerulean Cave requirement
    cerulean_cave_requirement = world.options.cerulean_cave_requirement.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x15, struct.pack("<B", cerulean_cave_requirement))

    # Set Cerulean Cave count
    cerulean_cave_count = world.options.cerulean_cave_count.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x16, struct.pack("<B", cerulean_cave_count))

    # Set starting badges
    patch.write_token(APTokenTypes.WRITE, options_address + 0x17, struct.pack("<B", starting_badges))

    # Set itemfinder required
    itemfinder_required = 1 if world.options.itemfinder_required.value == ItemfinderRequired.option_required else 0
    patch.write_token(APTokenTypes.WRITE, options_address + 0x19, struct.pack("<B", itemfinder_required))

    # Set recurring hidden items shuffled
    recurring_hidden_items = 1 if world.options.shuffle_hidden.value == ShuffleHiddenItems.option_all else 0
    patch.write_token(APTokenTypes.WRITE, options_address + 0x1A, struct.pack("<B", recurring_hidden_items))

    # Set Oak's Aides counts
    oaks_aide_route_2 = world.options.oaks_aide_route_2.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x1B, struct.pack("<B", oaks_aide_route_2))
    oaks_aide_route_10 = world.options.oaks_aide_route_10.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x1C, struct.pack("<B", oaks_aide_route_10))
    oaks_aide_route_11 = world.options.oaks_aide_route_11.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x1D, struct.pack("<B", oaks_aide_route_11))
    oaks_aide_route_16 = world.options.oaks_aide_route_16.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x1E, struct.pack("<B", oaks_aide_route_16))
    oaks_aide_route_15 = world.options.oaks_aide_route_15.value
    patch.write_token(APTokenTypes.WRITE, options_address + 0x1F, struct.pack("<B", oaks_aide_route_15))

    # Set slot auth
    patch.write_token(APTokenTypes.WRITE, data.rom_addresses[game_version_revision]["gArchipelagoInfo"], world.auth)

    patch.write_file("token_data.bin", patch.get_token_binary())
