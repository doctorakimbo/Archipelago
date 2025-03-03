"""
Classes and functions related to creating a ROM patch
"""
import bsdiff4
import struct
from typing import TYPE_CHECKING, Dict, List, Tuple

from worlds.Files import APPatchExtension, APProcedurePatch, APTokenMixin, APTokenTypes
from settings import get_settings
from .data import data, EvolutionMethodEnum, TrainerPokemonDataTypeEnum
from .locations import PokemonVegaLocation
from .options import (Dexsanity, FlashRequired, ForceFullyEvolved, ItemfinderRequired, HmCompatibility, LevelScaling,
                      RandomizeLegendaryPokemon, RandomizeMiscPokemon, RandomizeStarters, RandomizeTrainerParties,
                      RandomizeWildPokemon, ShuffleHiddenItems, TmTutorCompatibility)
from .pokemon import randomize_tutor_moves
from .util import bool_array_to_int, bound, encode_string

if TYPE_CHECKING:
    from . import PokemonVegaWorld

VEGA_HASH = "e26ee0d44e809351c8ce2d73c7400cdd"


# todo: vega
_LOOPING_MUSIC = [
    "MUS_RS_VS_GYM_LEADER", "MUS_RS_VS_TRAINER", "MUS_SCHOOL", "MUS_FOLLOW_ME", "MUS_GAME_CORNER", "MUS_ROCKET_HIDEOUT",
    "MUS_GYM", "MUS_CINNABAR", "MUS_LAVENDER", "MUS_CYCLING", "MUS_ENCOUNTER_ROCKET", "MUS_ENCOUNTER_GIRL",
    "MUS_ENCOUNTER_BOY", "MUS_HALL_OF_FAME", "MUS_VIRIDIAN_FOREST", "MUS_MT_MOON", "MUS_POKE_MANSION", "MUS_ROUTE1",
    "MUS_ROUTE24", "MUS_ROUTE3", "MUS_ROUTE11", "MUS_VICTORY_ROAD", "MUS_VS_GYM_LEADER", "MUS_VS_TRAINER",
    "MUS_VS_WILD", "MUS_VS_CHAMPION", "MUS_PALLET", "MUS_OAK_LAB", "MUS_OAK", "MUS_POKE_CENTER", "MUS_SS_ANNE",
    "MUS_SURF", "MUS_POKE_TOWER", "MUS_SILPH", "MUS_FUCHSIA", "MUS_CELADON", "MUS_VICTORY_TRAINER", "MUS_VICTORY_WILD",
    "MUS_VICTORY_GYM_LEADER", "MUS_VERMILLION", "MUS_PEWTER", "MUS_ENCOUNTER_RIVAL", "MUS_RIVAL_EXIT", "MUS_CAUGHT",
    "MUS_POKE_JUMP", "MUS_UNION_ROOM", "MUS_NET_CENTER", "MUS_MYSTERY_GIFT", "MUS_BERRY_PICK", "MUS_SEVII_CAVE",
    "MUS_TEACHY_TV_SHOW", "MUS_SEVII_ROUTE", "MUS_SEVII_DUNGEON", "MUS_SEVII_123", "MUS_SEVII_45", "MUS_SEVII_67",
    "MUS_VS_DEOXYS", "MUS_VS_MEWTWO", "MUS_VS_LEGEND", "MUS_ENCOUNTER_GYM_LEADER", "MUS_ENCOUNTER_DEOXYS",
    "MUS_TRAINER_TOWER", "MUS_SLOW_PALLET", "MUS_TEACHY_TV_MENU"
]


_FANFARES: Dict[str, int] = {
    "MUS_LEVEL_UP": 80,
    "MUS_OBTAIN_ITEM": 160,
    "MUS_EVOLVED": 220,
    "MUS_OBTAIN_TMHM": 220,
    "MUS_HEAL": 160,
    "MUS_OBTAIN_BADGE": 340,
    "MUS_MOVE_DELETED": 180,
    "MUS_OBTAIN_BERRY": 120,
    "MUS_SLOTS_JACKPOT": 250,
    "MUS_SLOTS_WIN": 150,
    "MUS_TOO_BAD": 160,
    "MUS_POKE_FLUTE": 450,
    "MUS_OBTAIN_KEY_ITEM": 170,
    "MUS_DEX_RATING": 196
}
_EVOLUTION_FANFARE_INDEX = list(_FANFARES.keys()).index("MUS_EVOLVED")


class PokemonVegaPatchExtension(APPatchExtension):
    game = "Pokemon Vega"

    @staticmethod
    def apply_bsdiff4(caller: APProcedurePatch, rom: bytes, patch: str) -> bytes:
        return bsdiff4.patch(rom, caller.get_file(patch))

    @staticmethod
    def apply_tokens(caller: APProcedurePatch, rom: bytes, token_file: str) -> bytes:
        rom_data = bytearray(rom)
        token_data = caller.get_file(token_file)
        token_count = int.from_bytes(token_data[0:4], "little")
        bpr = 4
        for _ in range(token_count):
            token_type = token_data[bpr:bpr + 1][0]
            offset = int.from_bytes(token_data[bpr + 1:bpr + 5], "little")
            size = int.from_bytes(token_data[bpr + 5:bpr + 9], "little")
            data = token_data[bpr + 9:bpr + 9 + size]
            if token_type in [APTokenTypes.AND_8, APTokenTypes.OR_8, APTokenTypes.XOR_8]:
                arg = data[0]
                if token_type == APTokenTypes.AND_8:
                    rom_data[offset] = rom_data[offset] & arg
                elif token_type == APTokenTypes.OR_8:
                    rom_data[offset] = rom_data[offset] | arg
                else:
                    rom_data[offset] = rom_data[offset] ^ arg
            elif token_type in [APTokenTypes.COPY, APTokenTypes.RLE]:
                length = int.from_bytes(data[:4], "little")
                value = int.from_bytes(data[4:], "little")
                if token_type == APTokenTypes.COPY:
                    rom_data[offset: offset + length] = rom_data[value: value + length]
                else:
                    rom_data[offset: offset + length] = bytes([value] * length)
            else:
                rom_data[offset:offset + len(data)] = data
            bpr += 9 + size
        return bytes(rom_data)


class PokemonVegaProcedurePatch(APProcedurePatch, APTokenMixin):
    game = "Pokemon Vega"
    hash = VEGA_HASH
    patch_file_ending = ".apvega"
    result_file_ending = ".gba"

    procedure = [
        ("apply_bsdiff4", ["base_patch.bsdiff4"]),
        ("apply_tokens", ["token_data.bin"])
    ]

    @classmethod
    def get_source_data(cls) -> bytes:
        with open(get_settings().pokemon_vega_settings.vega_rom_file, "rb") as infile:
            base_rom_bytes = bytes(infile.read())
        return base_rom_bytes


def get_tokens(world: "PokemonVegaWorld") -> APTokenMixin:
    tokens: APTokenMixin = APTokenMixin()

    # Set item values
    location_info: List[Tuple[int, int, str]] = []
    for location in world.multiworld.get_locations(world.player):
        assert isinstance(location, PokemonFRLGLocation)
        if location.address is None:
            continue

        if location.item is None:
            continue

        item_address = location.item_address

        if location.item.player == world.player:
            if type(item_address) is int:
                tokens.write_token(
                    APTokenTypes.WRITE,
                    item_address,
                    struct.pack("<H", location.item.code)
                )
            elif type(item_address) is list:
                for address in item_address:
                    tokens.write_token(
                        APTokenTypes.WRITE,
                        address,
                        struct.pack("<H", location.item.code)
                    )
        else:
            if type(item_address) is int:
                tokens.write_token(
                    APTokenTypes.WRITE,
                    item_address,
                    struct.pack("<H", data.constants["ITEM_ARCHIPELAGO_PROGRESSION"])
                )
            elif type(item_address) is list:
                for address in item_address:
                    tokens.write_token(
                        APTokenTypes.WRITE,
                        address,
                        struct.pack("<H", data.constants["ITEM_ARCHIPELAGO_PROGRESSION"])
                    )

        # Creates a list of item information to store in tables later. Those tables are used to display the item and
        # player name in a text box. In the case of not enough space, the game will default to "found an ARCHIPELAGO
        # ITEM"
        location_info.append((location.address, location.item.player, location.item.name))

    if world.options.trainersanity:
        # Sphere Ruins rival left his starter in the PC, and Mirage System isn't part of Trainersanity
        rival_rewards = ["RIVAL_HOLLYS_LAB", "RIVAL_SEAFIN", "MOS_RANGER_SQUAD", "RIVAL_ORPIMENCE",
                         "RIVAL_RAVENPLUME", "RIVAL_VICTORY_ROAD"]
        for trainer in rival_rewards:
            try:
                location = world.multiworld.get_location(data.locations[f"TRAINER_{trainer}_NIMBLEAF_REWARD"].name,
                                                         world.player)
                alternates = [
                    f"TRAINER_{trainer}_PEYERO",
                    f"TRAINER_{trainer}_LIQUIPUT"
                ]

                location_info.extend(
                    (
                        data.constants["TRAINER_FLAGS_START"] + data.constants[alternate],
                        location.item.player,
                        location.item.name
                    ) for alternate in alternates)
            except KeyError:
                continue

    player_name_ids: Dict[str, int] = {world.player_name: 0}
    item_name_offsets: Dict[str, int] = {}
    next_item_name_offset = 0
    for i, (flag, item_player, item_name) in enumerate(sorted(location_info, key=lambda t: t[0])):
        player_name = world.multiworld.get_player_name(item_player)

        if player_name not in player_name_ids:
            # Only space for 250 player names
            if len(player_name_ids) >= 250:
                continue

            player_name_ids[player_name] = len(player_name_ids)
            player_name_address = data.rom_addresses["gArchipelagoPlayerNames"]
            for j, b in enumerate(encode_string(player_name, 17)):
                tokens.write_token(
                    APTokenTypes.WRITE,
                    player_name_address + (player_name_ids[player_name] * 17) + j,
                    struct.pack("<B", b)
                )

        if item_name not in item_name_offsets:
            if len(item_name) > 35:
                item_name = item_name[:34] + "…"

            # Only 36 * 1500 bytes for item names
            if next_item_name_offset + len(item_name) + 1 > 36 * 1500:
                continue

            item_name_offsets[item_name] = next_item_name_offset
            next_item_name_offset += len(item_name) + 1
            item_name_address = data.rom_addresses["gArchipelagoItemNames"]
            tokens.write_token(
                APTokenTypes.WRITE,
                item_name_address + (item_name_offsets[item_name]),
                encode_string(item_name) + b"\xFF"
            )

        # There should always be enough space for one entry per location
        name_table_address = data.rom_addresses["gArchipelagoNameTable"]
        tokens.write_token(
            APTokenTypes.WRITE,
            name_table_address + (i * 5) + 0,
            struct.pack("<H", flag)
        )
        tokens.write_token(
            APTokenTypes.WRITE,
            name_table_address + (i * 5) + 2,
            struct.pack("<H", item_name_offsets[item_name])
        )
        tokens.write_token(
            APTokenTypes.WRITE,
            name_table_address + (i * 5) + 4,
            struct.pack("<B", player_name_ids[player_name])
        )

    # Set starting items
    start_inventory = world.options.start_inventory.value.copy()

    starting_items: List[Tuple[str, int]] = []
    for item, quantity in start_inventory.items():
        if "Unique" in data.items[world.item_name_to_id[item]].tags:
            quantity = 1
        if quantity > 999:
            quantity = 999
        starting_items.append([item, quantity])

    for i, starting_item in enumerate(starting_items, 1):
        item_address = data.rom_addresses["gArchipelagoStartingItems"] + (i * 2)
        count_address = data.rom_addresses["gArchipelagoStartingItemsCount"] + (i * 2)
        item = world.item_name_to_id[starting_item[0]]
        tokens.write_token(APTokenTypes.WRITE, item_address, struct.pack("<H", item))
        tokens.write_token(APTokenTypes.WRITE, count_address, struct.pack("<H", starting_item[1]))

    # Set species data
    _set_species_info(world, tokens)

    # Set wild encounters
    _set_wild_encounters(world, tokens)

    # Set starters
    _set_starters(world, tokens)

    # Set legendaries
    _set_legendaries(world, tokens)

    # Set misc pokemon
    _set_misc_pokemon(world, tokens)

    # Set trainer parties
    _set_trainer_parties(world, tokens)

    # Set TM/HM compatibility
    _set_tmhm_compatibility(world, tokens)

    # Set TM Moves
    _set_tm_moves(world, tokens)

    # Randomize move tutors
    _randomize_move_tutors(world, tokens)

    # Options
    # struct
    # ArchipelagoOptions
    # {
    # /* 0x00 */ bool8 advanceTextWithHoldA;
    # /* 0x01 */ u8 receivedItemMessageFilter; // 0 = Show All, 1 = Show Progression Only, 2 = Show None
    # /* 0x02 */ bool8 betterShopsEnabled;
    # /* 0x03 */ bool8 reusableTms;
    # /* 0x04 */ bool8 guaranteedCatch;
    # /* 0x05 */ bool8 areTrainersBlind;
    # /* 0x06 */ u16 expMultiplierNumerator;
    # /* 0x08 */ u16 expMultiplierDenominator;
    # /* 0x0A */ bool8 normalizeEncounterRates;
    # /* 0x0B */ bool8 canSkipFanfares;
    # /* 0x0C */ bool8 unlockSeenDexInfo;
    #
    # /* 0x0D */ bool8 openViridianCity;
    # /* 0x0E */ u8 route503Requirement; // 0 = Open, 1 = Defeat Annette, 2 = Defeat Any Gym Leader,
    #                                     3 = Elnath Badge, 4 = Any Badge
    # /* 0x0F */ bool8 openCeruleanCity;
    # /* 0x10 */ bool8 modifyRoute2;
    # /* 0x11 */ bool8 modifyRoute9;
    # /* 0x12 */ bool8 blockUndergroundTunnels;
    # /* 0x13 */ bool8 route12Boulders;
    # /* 0x14 */ bool8 modifyRoute10;
    # /* 0x15 */ bool8 modifyRoute12;
    # /* 0x16 */ bool8 modifyRoute16;
    # /* 0x17 */ bool8 openSilphCo;
    # /* 0x18 */ bool8 removeSaffronRockets;
    # /* 0x19 */ bool8 modifyRoute23;
    # /* 0x1A */ bool8 route23Trees;
    # /* 0x1B */ bool8 blockPokemonTower;
    # /* 0x1C */ bool8 victoryRoadRocks;
    # /* 0x1D */ bool8 earlyFameGossip;
    # /* 0x1E */ bool8 blockVermilionSailing;
    #
    # /* 0x1F */ bool8 giovanniRequiresGyms;
    # /* 0x20 */ u8 giovanniRequiredCount;
    # /* 0x21 */ bool8 route22GateRequiresGyms;
    # /* 0x22 */ u8 route22GateRequiredCount;
    # /* 0x23 */ bool8 route523GuardRequiresGyms;
    # /* 0x24 */ u8 route523GuardRequiredCount;
    # /* 0x25 */ bool8 eliteFourRequiresGyms;
    # /* 0x26 */ u8 eliteFourRequiredCount;
    # /* 0x27 */ bool8 eliteFourRematchRequiresGyms;
    # /* 0x28 */ u8 eliteFourRematchRequiredCount;
    # /* 0x29 */ u8 ceruleanCaveRequirement; // 0 = Vanilla, 1 = Become Champion, 2 = Restore Network Center,
    #                                           3 = Badges, 4 = Gyms
    # /* 0x2A */ u8 ceruleanCaveRequiredCount;
    #
    # /* 0x2B */ u32 startingMoney;
    #
    # /* 0x2F */ bool8 itemfinderRequired;
    # /* 0x30 */ bool8 flashRequired;
    # /* 0x31 */ bool8 fameCheckerRequired;
    #
    # /* 0x32 */ u8 oaksAideRequiredCounts[5]; // Route 2, Route 10, Route 11, Route 16, Route 15
    #
    # /* 0x36 */ bool8 reccuringHiddenItems;
    # /* 0x37 */ bool8 isTrainersanity;
    # /* 0x38 */ bool8 extraKeyItems;
    # /* 0x39 */ bool8 excludeSphereRuins;
    # /* 0x3A */ bool8 flyUnlocks;
    # /* 0x3B */ bool8 isFamesanity;
    # /* 0x37 */ bool8 reccuringHiddenItems;
    # /* 0x38 */ bool8 isTrainersanity;
    # /* 0x39 */ bool8 isDexsanity;
    # /* 0x3A */ bool8 extraKeyItems;
    # /* 0x3B */ bool8 excludeSphereRuins;
    # /* 0x3C */ bool8 flyUnlocks;
    # /* 0x3D */ bool8 isFamesanity;
    #
    # /* 0x3E */ u8 removeBadgeRequirement; // Flash, Cut, Fly, Strength, Surf, Rock Smash, Waterfall
    # /* 0x3F */ u8 additionalDarkCaves; // Mt. Moon, Diglett's Cave, Victory Road
    #
    # /* 0x40 */ bool8 passesSplit;
    # /* 0x41 */ bool8 cardKeysSplit;
    # /* 0x42 */ bool8 teasSplit;
    #
    # /* 0x43 */ u8 startingLocation;
    # /* 0x44 */ u8 free_fly_id;
    # /* 0x45 */ u8 town_free_fly_id;
    # /* 0x46 */ u16 resortGorgeousMon;
    # /* 0x48 */ u16 introSpecies;
    # /* 0x4A */ u16 pcItemId;
    # }
    options_address = data.rom_addresses["gArchipelagoOptions"]

    # Set hold A to advance text
    turbo_a = 1 if world.options.turbo_a else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x00, struct.pack("<B", turbo_a))

    # Set received item message types
    receive_item_messages = world.options.receive_item_messages.value
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x01, struct.pack("<B", receive_item_messages))

    # Set better shops
    better_shops = 1 if world.options.better_shops else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x02, struct.pack("<B", better_shops))

    # Set reusable TMs and Move Tutors
    reusable_tm_tutors = 1 if world.options.reusable_tm_tutors else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x03, struct.pack("<B", reusable_tm_tutors))

    # Set guaranteed catch
    guaranteed_catch = 1 if world.options.guaranteed_catch else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x04, struct.pack("<B", guaranteed_catch))

    # Set blind trainers
    blind_trainers = 1 if world.options.blind_trainers else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x05, struct.pack("<B", blind_trainers))

    # Set exp multiplier
    numerator = world.options.exp_modifier.value
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x06, struct.pack("<H", numerator))
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x08, struct.pack("<H", 100))

    # Set normalize encounter rates
    normalize_encounter_rates = 1 if world.options.normalize_encounter_rates else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x0A, struct.pack("<B", normalize_encounter_rates))

    # Set skipping fanfares
    skip_fanfares = 1 if world.options.randomize_fanfares else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x0B, struct.pack("<B", skip_fanfares))

    # Set unlock seen dex info
    all_pokemon_seen = 1 if world.options.all_pokemon_seen else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x0C, struct.pack("<B", all_pokemon_seen))

    # Set Junopsis City roadblock
    route_503_condition = world.options.junopsis_city_roadblock.value
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x0E, struct.pack("<B", route_503_condition))

    # Set Cerulean City roadblocks
    open_cerulean = 1 if "Remove Cerulean Roadblocks" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x0F, struct.pack("<B", open_cerulean))

    # Set Route 2 modification
    route_2_modified = 1 if "Modify Route 2" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x10, struct.pack("<B", route_2_modified))

    # Set Route 9 modification
    route_9_modified = 1 if "Modify Route 9" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x11, struct.pack("<B", route_9_modified))

    # Set Underground Tunnels blocked
    block_tunnels = 1 if "Block Tunnels" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x12, struct.pack("<B", block_tunnels))

    # Set Route 12 boulders
    route_12_boulders = 1 if "Route 12 Boulders" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x13, struct.pack("<B", route_12_boulders))

    # Set Route 10 modification
    route_10_modified = 1 if "Modify Route 10" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x14, struct.pack("<B", route_10_modified))

    # Set Route 12 modification
    route_12_modified = 1 if "Modify Route 12" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x15, struct.pack("<B", route_12_modified))

    # Set Route 16 modification
    route_16_modified = 1 if "Modify Route 16" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x16, struct.pack("<B", route_16_modified))

    # Set open Silph Co.
    open_silph = 1 if "Open Silph" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x17, struct.pack("<B", open_silph))

    # Set remove Saffron Rockets
    remove_saffron_rockets = 1 if "Remove Saffron Rockets" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x18, struct.pack("<B", remove_saffron_rockets))

    # Set Route 23 modification
    route_23_modified = 1 if "Modify Route 23" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x19, struct.pack("<B", route_23_modified))

    # Set Route 23 trees
    route_23_trees = 1 if "Route 23 Trees" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x1A, struct.pack("<B", route_23_trees))

    # Set Pokémon Tower blocked
    block_tower = 1 if "Block Tower" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x1B, struct.pack("<B", block_tower))

    # Set Victory Road rocks
    victory_road_rocks = 1 if "Victory Road Rocks" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x1C, struct.pack("<B", victory_road_rocks))

    # Set early gossipers
    early_gossipers = 1 if "Early Gossipers" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x1D, struct.pack("<B", early_gossipers))

    # Set block Vermilion sailing
    block_vermilion_sailing = 1 if "Block Vermilion Sailing" in world.options.modify_world_state.value else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x1E, struct.pack("<B", block_vermilion_sailing))

    # Set Route 523 requirement
    route_523_requirement = world.options.route523_guard_requirement.value
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x23, struct.pack("<B", route_523_requirement))

    # Set Route 523 count
    route_523_count = world.options.route523_guard_count.value
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x24, struct.pack("<B", route_523_count))

    # Set Elite Four requirement
    elite_four_requirement = world.options.elite_four_requirement.value
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x25, struct.pack("<B", elite_four_requirement))

    # Set Elite Four count
    elite_four_count = world.options.elite_four_count.value
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x26, struct.pack("<B", elite_four_count))

    # Set Elite Four Rematch requirement
    elite_four_rematch_requirement = world.options.elite_four_requirement.value
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x27, struct.pack("<B", elite_four_rematch_requirement))

    # Set Elite Four Rematch count
    elite_four_rematch_count = world.options.elite_four_rematch_count.value
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x28, struct.pack("<B", elite_four_rematch_count))

    # Set Cerulean Cave requirement
    cerulean_cave_requirement = world.options.cerulean_cave_requirement.value
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x29, struct.pack("<B", cerulean_cave_requirement))

    # Set Cerulean Cave count
    cerulean_cave_count = world.options.cerulean_cave_count.value
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x2A, struct.pack("<B", cerulean_cave_count))

    # Set starting money
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x2B, struct.pack("<I",
                                                                               world.options.starting_money.value))
    # Set itemfinder required
    itemfinder_required = 1 if world.options.itemfinder_required.value == ItemfinderRequired.option_required else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x2F, struct.pack("<B", itemfinder_required))

    # Set flash required
    flash_required = 1 if world.options.flash_required.value == FlashRequired.option_required else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x30, struct.pack("<B", flash_required))

    # Set recurring hidden items shuffled
    recurring_hidden_items = 1 if world.options.shuffle_hidden.value == ShuffleHiddenItems.option_all else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x37, struct.pack("<B", recurring_hidden_items))

    # Set trainersanity
    trainersanity = 1 if world.options.trainersanity else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x38, struct.pack("<B", trainersanity))

    # Set dexsanity
    dexsanity = 1 if world.options.dexsanity != Dexsanity.special_range_names["none"] else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x39, struct.pack("<B", dexsanity))

    # Set extra key items
    extra_key_items = 1 if world.options.extra_key_items else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x3A, struct.pack("<B", extra_key_items))

    # Set exclude sphere ruins
    exclude_sphere_ruins = 1 if world.options.exclude_sphere_ruins else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x3B, struct.pack("<B", exclude_sphere_ruins))

    # Set fly unlocks
    fly_unlocks = 1 if world.options.shuffle_fly_destination_unlocks else 0
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x3C, struct.pack("B", fly_unlocks))

    # Set remove badge requirements
    hms = ["Flash", "Cut", "Fly", "Strength", "Surf", "Rock Smash", "Waterfall"]
    remove_badge_requirements = 0
    for i, hm in enumerate(hms):
        if hm in world.options.remove_badge_requirement.value:
            remove_badge_requirements |= (1 << i)
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x3E, struct.pack("<B", remove_badge_requirements))

    # Set additional dark caves
    dark_caves = ["Mt. Moon", "Diglett's Cave", "Victory Road"]
    map_ids = [["MAP_MT_MOON_1F", "MAP_MT_MOON_B1F", "MAP_MT_MOON_B2F"],
               ["MAP_DIGLETTS_CAVE_B1F"],
               ["MAP_VICTORY_ROAD_1F", "MAP_VICTORY_ROAD_2F", "MAP_VICTORY_ROAD_3F"]]
    additional_dark_caves = 0
    for i, dark_cave in enumerate(dark_caves):
        if dark_cave in world.options.additional_dark_caves.value:
            additional_dark_caves |= (1 << i)
            for map_id in map_ids[i]:
                map_data = world.modified_maps[map_id]
                header_address = map_data.header_address
                tokens.write_token(APTokenTypes.WRITE, header_address + 21, struct.pack("<B", 1))
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x3F, struct.pack("<B", additional_dark_caves))

    # Set starting town
    starting_town = data.constants[world.starting_town]
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x43, struct.pack("<B", starting_town))

    # Set free fly location
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x44, struct.pack("<B", world.free_fly_location_id))

    # Set town map fly location
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x45, struct.pack("<B", world.town_map_fly_location_id))

    # Set intro species
    species_id = world.random.choice(list(data.species.keys()))
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x48, struct.pack("<H", species_id))

    # Set PC item ID
    pc_item_location = world.get_location("Player's PC - Starting Item")
    if pc_item_location.item.player == world.player:
        item_id = pc_item_location.item.code
    else:
        item_id = data.constants["ITEM_ARCHIPELAGO_PROGRESSION"]
    tokens.write_token(APTokenTypes.WRITE, options_address + 0x4A, struct.pack("<H", item_id))

    # Set total darkness
    if "Total Darkness" in world.options.modify_world_state.value:
        flash_level_address = data.rom_addresses["sFlashLevelToRadius"]
        tokens.write_token(APTokenTypes.WRITE, flash_level_address + 8, struct.pack("<H", 0))

    # Randomize music
    if world.options.randomize_music:
        # The "randomized sound table" is a patchboard that redirects sounds just before they get played
        randomized_looping_music = _LOOPING_MUSIC.copy()
        world.random.shuffle(randomized_looping_music)
        sound_table_address = data.rom_addresses[game_version_revision]["gRandomizedSoundTable"]
        for original_music, randomized_music in zip(_LOOPING_MUSIC, randomized_looping_music):
            tokens.write_token(
                APTokenTypes.WRITE,
                sound_table_address + (data.constants[original_music] * 2),
                struct.pack("<H", data.constants[randomized_music])
            )

    # Randomize fanfares
    if world.options.randomize_fanfares:
        # Shuffle the lists, pair new tracks with original tracks, set the new track ids, and set new fanfare durations
        randomized_fanfares = [fanfare_name for fanfare_name in _FANFARES]
        world.random.shuffle(randomized_fanfares)
        sound_table_address = data.rom_addresses[game_version_revision]["gRandomizedSoundTable"]
        fanfares_address = data.rom_addresses[game_version_revision]["sFanfares"]

        # Prevent the evolution fanfare from receiving the poke flute by swapping it with something else.
        # The poke flute sound causes the evolution scene to get stuck for like 40 seconds
        if randomized_fanfares[_EVOLUTION_FANFARE_INDEX] == "MUS_POKE_FLUTE":
            swap_index = (_EVOLUTION_FANFARE_INDEX + 1) % len(_FANFARES)
            temp = randomized_fanfares[_EVOLUTION_FANFARE_INDEX]
            randomized_fanfares[_EVOLUTION_FANFARE_INDEX] = randomized_fanfares[swap_index]
            randomized_fanfares[swap_index] = temp

        for i, fanfare_data in enumerate(zip(_FANFARES.keys(), randomized_fanfares)):
            tokens.write_token(
                APTokenTypes.WRITE,
                sound_table_address + (data.constants[fanfare_data[0]] * 2),
                struct.pack("<H", data.constants[fanfare_data[1]])
            )
            tokens.write_token(
                APTokenTypes.WRITE,
                fanfares_address + (i * 4) + 2,
                struct.pack("<H", data.constants[fanfare_data[1]])
            )

    # Set slot auth
    tokens.write_token(APTokenTypes.WRITE, data.rom_addresses["gArchipelagoInfo"], world.auth)

    return tokens


def _set_species_info(world: "PokemonVegaWorld", tokens: APTokenMixin) -> None:
    for species in world.modified_species.values():
        address = species.address

        tokens.write_token(APTokenTypes.WRITE, address + 0x06, struct.pack("<B", species.types[0]))
        tokens.write_token(APTokenTypes.WRITE, address + 0x07, struct.pack("<B", species.types[1]))
        tokens.write_token(APTokenTypes.WRITE, address + 0x08, struct.pack("<B", species.catch_rate))
        tokens.write_token(APTokenTypes.WRITE, address + 0x16, struct.pack("<B", species.abilities[0]))
        tokens.write_token(APTokenTypes.WRITE, address + 0x17, struct.pack("<B", species.abilities[1]))

        for i, learnset_move in enumerate(species.learnset):
            learnset_address = species.learnset_address
            level_move = learnset_move.level << 9 | learnset_move.move_id
            tokens.write_token(APTokenTypes.WRITE, learnset_address + (i * 2), struct.pack("<H", level_move))


def _set_wild_encounters(world: "PokemonVegaWorld", tokens: APTokenMixin) -> None:
    if (world.options.level_scaling == LevelScaling.option_off and
            world.options.wild_pokemon == RandomizeWildPokemon.option_vanilla):
        return

    """
        Encounter tables are lists of
        struct {
            min_level:  uint8,
            max_level:  uint8,
            species_id: uint16
        }
    """
    for map_data in world.modified_maps.values():
        tables = [map_data.land_encounters,
                  map_data.water_encounters,
                  map_data.fishing_encounters]
        for table in tables:
            if table is not None:
                for i, species_data in enumerate(table.slots):
                    address = table.address + (i * 4)
                    tokens.write_token(APTokenTypes.WRITE, address, struct.pack("<B", species_data.min_level))
                    tokens.write_token(APTokenTypes.WRITE, address + 0x01, struct.pack("<B", species_data.max_level))
                    tokens.write_token(APTokenTypes.WRITE, address + 0x02, struct.pack("<H", species_data.species_id))


def _set_starters(world: "PokemonVegaWorld", tokens: APTokenMixin) -> None:
    if world.options.starters == RandomizeStarters.option_vanilla:
        return

    for name, starter in world.modified_starters.items():
        tokens.write_token(APTokenTypes.WRITE,
                           starter.address,
                           struct.pack("<H", starter.species_id))


def _set_legendaries(world: "PokemonVegaWorld", tokens: APTokenMixin) -> None:
    if (world.options.level_scaling == LevelScaling.option_off and
            world.options.legendary_pokemon == RandomizeLegendaryPokemon.option_vanilla):
        return

    for name, legendary in world.modified_legendary_pokemon.items():
        tokens.write_token(APTokenTypes.WRITE,
                           legendary.address,
                           struct.pack("<H", legendary.species_id))
        tokens.write_token(APTokenTypes.WRITE,
                           legendary.level_address,
                           struct.pack("<B", legendary.level))


def _set_misc_pokemon(world: "PokemonVegaWorld", tokens: APTokenMixin) -> None:
    if (world.options.level_scaling == LevelScaling.option_off and
            world.options.misc_pokemon == RandomizeMiscPokemon.option_vanilla):
        return

    for name, misc_pokemon in world.modified_misc_pokemon.items():
        tokens.write_token(APTokenTypes.WRITE,
                           misc_pokemon.address,
                           struct.pack("<H", misc_pokemon.species_id))
        if misc_pokemon.level != 0:
            tokens.write_token(APTokenTypes.WRITE,
                               misc_pokemon.level_address,
                               struct.pack("<B", misc_pokemon.level))


def _set_trainer_parties(world: "PokemonVegaWorld", tokens: APTokenMixin) -> None:
    if (world.options.level_scaling == LevelScaling.option_off and
            world.options.trainers == RandomizeTrainerParties.option_vanilla and
            world.options.starters == RandomizeStarters.option_vanilla and
            world.options.modify_trainer_levels.value == 0):
        return

    for trainer in world.modified_trainers.values():
        party_address = trainer.party.address

        if trainer.party.pokemon_data_type in {TrainerPokemonDataTypeEnum.NO_ITEM_DEFAULT_MOVES,
                                               TrainerPokemonDataTypeEnum.ITEM_DEFAULT_MOVES}:
            pokemon_data_size = 8
        else:
            pokemon_data_size = 16

        for i, pokemon in enumerate(trainer.party.pokemon):
            pokemon_address = party_address + (i * pokemon_data_size)

            pokemon.level = round(pokemon.level + (pokemon.level * (world.options.modify_trainer_levels.value / 100)))
            pokemon.level = bound(pokemon.level, 1, 100)

            if world.options.force_fully_evolved != ForceFullyEvolved.special_range_names["never"]:
                evolve = True
                if world.options.force_fully_evolved == ForceFullyEvolved.special_range_names["species"]:
                    while evolve:
                        evolve = False
                        species_data = world.modified_species[pokemon.species_id]
                        evolutions = species_data.evolutions.copy()
                        world.random.shuffle(evolutions)
                        for evolution in evolutions:
                            if evolution.method in range(EvolutionMethodEnum.LEVEL, EvolutionMethodEnum.ITEM):
                                if pokemon.level >= evolution.param:
                                    pokemon.species_id = evolution.species_id
                                    evolve = True
                                    break
                            else:
                                evolution_data = world.modified_species[evolution.species_id]
                                evolution_level = sum(evolution_data.base_stats) / 15
                                if pokemon.level > evolution_level:
                                    pokemon.species_id = evolution.species_id
                                    evolve = True
                                    break
                elif pokemon.level >= world.options.force_fully_evolved.value:
                    while evolve:
                        species_data = world.modified_species[pokemon.species_id]
                        if len(species_data.evolutions) > 0:
                            evolution = world.random.choice(species_data.evolutions)
                            pokemon.species_id = evolution.species_id
                        else:
                            evolve = False

            tokens.write_token(APTokenTypes.WRITE, pokemon_address + 0x02, struct.pack("<B", pokemon.level))
            tokens.write_token(APTokenTypes.WRITE, pokemon_address + 0x04, struct.pack("<H", pokemon.species_id))

            if trainer.party.pokemon_data_type in {TrainerPokemonDataTypeEnum.NO_ITEM_CUSTOM_MOVES,
                                                   TrainerPokemonDataTypeEnum.ITEM_CUSTOM_MOVES}:
                offset = 2 if trainer.party.pokemon_data_type == TrainerPokemonDataTypeEnum.ITEM_CUSTOM_MOVES else 0
                tokens.write_token(APTokenTypes.WRITE,
                                   pokemon_address + 0x06 + offset,
                                   struct.pack("<H", pokemon.moves[0]))
                tokens.write_token(APTokenTypes.WRITE,
                                   pokemon_address + 0x08 + offset,
                                   struct.pack("<H", pokemon.moves[1]))
                tokens.write_token(APTokenTypes.WRITE,
                                   pokemon_address + 0x0A + offset,
                                   struct.pack("<H", pokemon.moves[2]))
                tokens.write_token(APTokenTypes.WRITE,
                                   pokemon_address + 0x0C + offset,
                                   struct.pack("<H", pokemon.moves[3]))


def _set_tmhm_compatibility(world: "PokemonVegaWorld", tokens: APTokenMixin) -> None:
    if (world.options.hm_compatibility == HmCompatibility.special_range_names["vanilla"] and
            world.options.tm_tutor_compatibility == TmTutorCompatibility.special_range_names["vanilla"]):
        return

    learnsets_address = data.rom_addresses["sTMHMLearnsets"]

    for species in world.modified_species.values():
        tokens.write_token(
            APTokenTypes.WRITE,
            learnsets_address + (species.species_id * 8),
            struct.pack("<Q", species.tm_hm_compatibility)
        )


def _set_tm_moves(world: "PokemonVegaWorld", tokens: APTokenMixin) -> None:
    if not world.options.tm_tutor_moves:
        return

    address = data.rom_addresses["sTMHMMoves"]

    for i, move in enumerate(world.modified_tmhm_moves):
        # Don't modify HMs
        if i >= 50:
            break

        tokens.write_token(APTokenTypes.WRITE, address + (i * 2), struct.pack("<H", move))


def _randomize_move_tutors(world: "PokemonVegaWorld", tokens: APTokenMixin) -> None:
    if world.options.tm_tutor_moves:
        new_tutor_moves = randomize_tutor_moves(world)
        address = data.rom_addresses["gTutorMoves"]

        for i, move in enumerate(new_tutor_moves):
            tokens.write_token(APTokenTypes.WRITE, address + (i * 2), struct.pack("<H", move))

    if world.options.tm_tutor_compatibility != TmTutorCompatibility.special_range_names["vanilla"]:
        learnsets_address = data.rom_addresses["sTutorLearnsets"]

        for species in world.modified_species.values():
            tokens.write_token(
                APTokenTypes.WRITE,
                learnsets_address + (species.species_id * 2),
                struct.pack("<H", bool_array_to_int([
                    world.random.randrange(0, 100) < world.options.tm_tutor_compatibility.value
                    for _ in range(16)
                ]))
            )
