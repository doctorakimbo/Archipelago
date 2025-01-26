"""
Pulls data from JSON files in worlds/pokemon_vega/data/ into classes.
This also includes marrying automatically extracted data with manually
defined data (like location names or usable Pokémon species), some cleanup
and sorting, and Warp methods.
"""
import orjson
import pkgutil
from pkg_resources import resource_listdir, resource_isdir
from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, NamedTuple, Optional, Set, FrozenSet, Any, Union, Tuple
from BaseClasses import ItemClassification

BASE_OFFSET = 6420000
NUM_REAL_SPECIES = 386


class Warp:
    """
    Represents warp events in the game like doorways or warp pads
    """
    is_one_way: bool
    source_map: str
    source_ids: List[str]
    dest_map: str
    dest_ids: List[str]
    name: Optional[str]
    parent_region_id: Optional[str]

    def __init__(self, encoded_string: Optional[str] = None,
                 name: Optional[str] = None,
                 parent_region_id: Optional[str] = None) -> None:
        if encoded_string is not None:
            decoded_warp = Warp.decode(encoded_string)
            self.is_one_way = decoded_warp.is_one_way
            self.source_map = decoded_warp.source_map
            self.source_ids = decoded_warp.source_ids
            self.dest_map = decoded_warp.dest_map
            self.dest_ids = decoded_warp.dest_ids
        self.name = name
        self.parent_region_id = parent_region_id

    def connects_to(self, other: "Warp") -> bool:
        """
        Returns true if this warp sends the player to `other`
        """
        return self.dest_map == other.source_map and set(self.dest_ids) <= set(other.source_ids)

    @staticmethod
    def decode(encoded_string: str) -> "Warp":
        """
        Create a Warp object from an encoded string
        """
        warp = Warp()
        warp.is_one_way = encoded_string.endswith("!")
        if warp.is_one_way:
            encoded_string = encoded_string[:-1]

        warp_source, warp_dest = encoded_string.split("/")
        warp_source_map, warp_source_indices = warp_source.split(":")
        warp_dest_map, warp_dest_indices = warp_dest.split(":")

        warp.source_map = warp_source_map
        warp.dest_map = warp_dest_map

        warp.source_ids = [int(index) for index in warp_source_indices.split(",")]
        warp.dest_ids = [int(index) for index in warp_dest_indices.split(",")]

        return warp


class ItemData(NamedTuple):
    name: str
    item_id: int
    classification: ItemClassification
    tags: FrozenSet[str]


class LocationData(NamedTuple):
    id: str
    name: str
    parent_region_id: str
    default_item: int
    address: Dict[str, Union[int, List[int]]]
    flag: int
    tags: FrozenSet[str]


@dataclass
class EncounterSpeciesData:
    species_id: int
    min_level: int
    max_level: int


class EncounterTableData(NamedTuple):
    slots: Dict[str, List[EncounterSpeciesData]]
    address: Dict[str, int]


@dataclass
class MapData:
    name: str
    header_address: Dict[str, int]
    land_encounters: Optional[EncounterTableData]
    water_encounters: Optional[EncounterTableData]
    fishing_encounters: Optional[EncounterTableData]
    sphere_ruins: bool


class EventData(NamedTuple):
    id: str
    name: Union[str, List[str]]
    item: Union[str, List[str]]
    parent_region_id: str
    tags: FrozenSet[str]


class RegionData:
    id: str
    name: str
    parent_map: Optional[MapData]
    encounter_region: str
    has_land: bool
    has_water: bool
    has_fishing: bool
    sphere_ruins: bool
    exits: Dict[str, str]
    warps: List[str]
    locations: List[str]
    events: List[str]

    def __init__(self, region_id: str, name: str, parent_map: Optional[MapData], encounter_region: str,
                 has_land: bool, has_water: bool, has_fishing: bool, sphere_ruins: bool):
        self.id = region_id
        self.name = name
        self.parent_map = parent_map
        self.encounter_region = encounter_region
        self.has_land = has_land
        self.has_water = has_water
        self.has_fishing = has_fishing
        self.sphere_ruins = sphere_ruins
        self.exits = []
        self.warps = []
        self.locations = []
        self.events = []


class BaseStats(NamedTuple):
    hp: int
    attack: int
    defense: int
    speed: int
    special_attack: int
    special_defense: int


class LearnsetMove(NamedTuple):
    level: int
    move_id: int


class EvolutionMethodEnum(IntEnum):
    LEVEL = 0
    LEVEL_ATK_LT_DEF = 1
    LEVEL_ATK_EQ_DEF = 2
    LEVEL_ATK_GT_DEF = 3
    LEVEL_SILCOON = 4
    LEVEL_CASCOON = 5
    LEVEL_NINJASK = 6
    LEVEL_SHEDINJA = 7
    ITEM = 8
    FRIENDSHIP = 9


EVOLUTION_METHOD_TYPE: Dict[str, EvolutionMethodEnum] = {
    "LEVEL": EvolutionMethodEnum.LEVEL,
    "LEVEL_ATK_LT_DEF": EvolutionMethodEnum.LEVEL_ATK_LT_DEF,
    "LEVEL_ATK_EQ_DEF": EvolutionMethodEnum.LEVEL_ATK_EQ_DEF,
    "LEVEL_ATK_GT_DEF": EvolutionMethodEnum.LEVEL_ATK_GT_DEF,
    "LEVEL_SILCOON": EvolutionMethodEnum.LEVEL_SILCOON,
    "LEVEL_CASCOON": EvolutionMethodEnum.LEVEL_CASCOON,
    "LEVEL_NINJASK": EvolutionMethodEnum.LEVEL_NINJASK,
    "LEVEL_SHEDINJA": EvolutionMethodEnum.LEVEL_SHEDINJA,
    "ITEM": EvolutionMethodEnum.ITEM,
    "FRIENDSHIP": EvolutionMethodEnum.FRIENDSHIP
}


class EvolutionData(NamedTuple):
    param: int
    species_id: int
    method: EvolutionMethodEnum


@dataclass
class SpeciesData:
    species_id_name: str
    name: str
    species_id: int
    national_dex_number: int
    base_stats: BaseStats
    types: Tuple[int, int]
    abilities: Tuple[int, int]
    evolutions: List[EvolutionData]
    pre_evolution: Optional[int]
    catch_rate: int
    friendship: int
    learnset: List[LearnsetMove]
    tm_hm_compatibility: int
    learnset_address: Dict[str, int]
    address: Dict[str, int]


@dataclass
class StarterData:
    species_id: int
    player_address: Dict[str, int]
    rival_address: Dict[str, int]


@dataclass
class MiscPokemonData:
    species_id: Dict[str, int]
    level: [str, int]
    address: Dict[str, int]
    level_address: Dict[str, int]


class TrainerPokemonDataTypeEnum(IntEnum):
    NO_ITEM_DEFAULT_MOVES = 0
    NO_ITEM_CUSTOM_MOVES = 1
    ITEM_DEFAULT_MOVES = 2
    ITEM_CUSTOM_MOVES = 3


POKEMON_DATA_TYPE: Dict[str, TrainerPokemonDataTypeEnum] = {
    "NO_ITEM_DEFAULT_MOVES": TrainerPokemonDataTypeEnum.NO_ITEM_DEFAULT_MOVES,
    "NO_ITEM_CUSTOM_MOVES": TrainerPokemonDataTypeEnum.NO_ITEM_CUSTOM_MOVES,
    "ITEM_DEFAULT_MOVES": TrainerPokemonDataTypeEnum.ITEM_DEFAULT_MOVES,
    "ITEM_CUSTOM_MOVES": TrainerPokemonDataTypeEnum.ITEM_CUSTOM_MOVES
}


@dataclass
class TrainerPokemonData:
    species_id: int
    level: int
    moves: Optional[Tuple[int, int, int, int]]
    locked: bool


@dataclass
class TrainerPartyData:
    pokemon: List[TrainerPokemonData]
    pokemon_data_type: TrainerPokemonDataTypeEnum
    address: Dict[str, int]


@dataclass
class TrainerData:
    party: TrainerPartyData
    address: Dict[str, int]


class PokemonVegaData:
    rom_name: str
    constants: Dict[str, int]
    ram_addresses: Dict[str, Dict[str, int]]
    rom_addresses: Dict[str, Dict[str, int]]
    regions: Dict[str, RegionData]
    locations: Dict[str, LocationData]
    events: Dict[str, EventData]
    items: Dict[int, ItemData]
    maps: Dict[str, MapData]
    warps: Dict[str, Warp]
    warp_map: Dict[str, Optional[str]]
    species: Dict[int, SpeciesData]
    evolutions: Dict[str, EvolutionData]
    starters: Dict[str, StarterData]
    legendary_pokemon: Dict[str, MiscPokemonData]
    misc_pokemon: Dict[str, MiscPokemonData]
    trainers: Dict[str, TrainerData]
    tmhm_moves: List[int]
    abilities: Dict[str, int]
    moves: Dict[str, int]

    def __init__(self) -> None:
        self.constants = {}
        self.ram_addresses = {}
        self.rom_addresses = {}
        self.regions = {}
        self.locations = {}
        self.events = {}
        self.items = {}
        self.maps = {}
        self.warps = {}
        self.warp_map = {}
        self.species = {}
        self.evolutions = {}
        self.starters = {}
        self.legendary_pokemon = {}
        self.misc_pokemon = {}
        self.trainers = {}
        self.tmhm_moves = []
        self.abilities = {}
        self.moves = {}


# Excludes extras like copies of Unown and special species values like SPECIES_EGG

# TODO: not here, but wanted to note: randomize Mewtwo and Final Turner's pokemon by just ability and type;
# moveset is handled by giving them random four moves (80+ base power) in the trainer data, and species should never be randomized
ALL_SPECIES: List[Tuple[str, str, int]] = [
    ("SPECIES_NIMBLEAF", "Nimbleaf", 1),
    ("SPECIES_LEAFROND", "Leafrond", 2),
    ("SPECIES_SYLEAFID", "Syleafid", 3),
    ("SPECIES_PEYERO", "Peyero", 4),
    ("SPECIES_INFIRIS", "Infiris", 5),
    ("SPECIES_ASTIGNITE", "Astignite", 6),
    ("SPECIES_LIQUIPUT", "Liquiput", 7),
    ("SPECIES_HYDRUSH", "Hydrush", 8),
    ("SPECIES_CORRENCID", "Correncid", 9),
    ("SPECIES_TAILLOW", "Taillow", 10),
    ("SPECIES_SWELLOW", "Swellow", 11),
    ("SPECIES_RIOLU", "Riolu", 12),
    ("SPECIES_LUCARIO", "Lucario", 13),
    ("SPECIES_HOUNDOUR", "Houndour", 14),
    ("SPECIES_HOUNDOOM", "Houndoom", 15),
    ("SPECIES_DIGLETT", "Diglett", 16),
    ("SPECIES_DUGTRIO", "Dugtrio", 17),
    ("SPECIES_TOGEPI", "Togepi", 18),
    ("SPECIES_TOGETIC", "Togetic", 19),
    ("SPECIES_TOGEKISS", "Togekiss", 20),
    ("SPECIES_GLACHILD", "Glachild", 21),
    ("SPECIES_FROZAIDEN", "Frozaiden", 22),
    ("SPECIES_AUROSTICE", "Aurostice", 23),
    ("SPECIES_PICHU", "Pichu", 24),
    ("SPECIES_PIKACHU", "Pikachu", 25),
    ("SPECIES_RAICHU", "Raichu", 26),
    ("SPECIES_MACHU", "Machu", 27),
    ("SPECIES_SKARMORY", "Skarmory", 28),
    ("SPECIES_NIDORAN_F", "Nidoran F", 29),
    ("SPECIES_NIDORINA", "Nidorina", 30),
    ("SPECIES_NIDOQUEEN", "Nidoqueen", 31),
    ("SPECIES_NIDORAN_M", "Nidoran M", 32),
    ("SPECIES_NIDORINO", "Nidorino", 33),
    ("SPECIES_NIDOKING", "Nidoking", 34),
    ("SPECIES_BUIZEL", "Buizel", 35),
    ("SPECIES_FLOATZEL", "Floatzel", 36),
    ("SPECIES_JAMBERREE", "Jamberree", 37),
    ("SPECIES_STRAWNA", "Strawna", 38),
    ("SPECIES_PINECO", "Pineco", 39),
    ("SPECIES_FORRETRESS", "Forretress", 40),
    ("SPECIES_SHELLDER", "Shellder", 41),
    ("SPECIES_CLOYSTER", "Cloyster", 42),
    ("SPECIES_PSYCOLT", "Psycolt", 43),
    ("SPECIES_KINEGASUS", "Kinegasus", 44),
    ("SPECIES_YUNESIS", "Yunesis", 45),
    ("SPECIES_TYROGUE", "Tyrogue", 46),
    ("SPECIES_HITMONLEE", "Hitmonlee", 47),
    ("SPECIES_HITMONCHAN", "Hitmonchan", 48),
    ("SPECIES_HITMONTOP", "Hitmontop", 49),
    ("SPECIES_RYNOS", "Rynos", 50),
    ("SPECIES_FEROCEROS", "Feroceros", 51),
    ("SPECIES_ABSOL", "Absol", 52),
    ("SPECIES_DIZASOL", "Dizasol", 53),
    ("SPECIES_GIRAFARIG", "Girafarig", 54),
    ("SPECIES_FOLIFARIG", "Folifarig", 55),
    ("SPECIES_WILLISP", "Willisp", 56),
    ("SPECIES_WISPLODE", "Wisplode", 57),
    ("SPECIES_MAGNEMITE", "Magnemite", 58),
    ("SPECIES_MAGNETON", "Magneton", 59),
    ("SPECIES_MAGNEZONE", "Magnezone", 60),
    ("SPECIES_STARYU", "Staryu", 61),
    ("SPECIES_STARMIE", "Starmie", 62),
    ("SPECIES_GASTLY", "Gastly", 63),
    ("SPECIES_HAUNTER", "Haunter", 64),
    ("SPECIES_GENGAR", "Gengar", 65),
    ("SPECIES_EXEGGCUTE", "Exeggcute", 66),
    ("SPECIES_EXEGGUTOR", "Exeggutor", 67),
    ("SPECIES_VELVELT", "Velvelt", 68),
    ("SPECIES_GRISSLY", "Grissly", 69),
    ("SPECIES_HANTAMA", "Hantama", 70),
    ("SPECIES_RHYHORN", "Rhyhorn", 71),
    ("SPECIES_RHYDON", "Rhydon", 72),
    ("SPECIES_RHYPERIOR", "Rhyperior", 73),
    ("SPECIES_TROPIUS", "Tropius", 74),
    ("SPECIES_PORYGON", "Porygon", 75),
    ("SPECIES_PORYGON2", "Porygon2", 76),
    ("SPECIES_PORYGONZ", "Porygon-Z", 77),
    ("SPECIES_SPHEAL", "Spheal", 78),
    ("SPECIES_SEALEO", "Sealeo", 79),
    ("SPECIES_WALREIN", "Walrein", 80),
    ("SPECIES_ROLLDER", "Rollder", 81),
    ("SPECIES_ROTILLO", "Rotillo", 82),
    ("SPECIES_SNALO", "Snalo", 83),
    ("SPECIES_SERPLANT", "Serplant", 84),
    ("SPECIES_SNOVER", "Snover", 85),
    ("SPECIES_ABOMASNOW", "Abomasnow", 86),
    ("SPECIES_YUCARLIA", "Yucarlia", 87),
    ("SPECIES_NECROSIA", "Necrosia", 88),
    ("SPECIES_CUPRICORN", "Cupricorn", 89),
    ("SPECIES_HORNIKEL", "Hornikel", 90),
    ("SPECIES_GOABALT", "Goabalt", 91),
    ("SPECIES_MILTANK", "Miltank", 92),
    ("SPECIES_SHUCKLE", "Shuckle", 93),
    ("SPECIES_MORNWING", "Mornwing", 94),
    ("SPECIES_GULDAWN", "Guldawn", 95),
    ("SPECIES_SOLARISEN", "Solarisen", 96),
    ("SPECIES_MINTCH", "Mintch", 97),
    ("SPECIES_BLAKJAK", "Blakjak", 98),
    ("SPECIES_MANEKO", "Maneko", 99),
    ("SPECIES_BAKEKO", "Bakeko", 100),
    ("SPECIES_PLASMOX", "Plasmox", 101),
    ("SPECIES_BLITZUNE", "Blitzune", 102),
    ("SPECIES_CUPPA", "Cuppa", 103),
    ("SPECIES_KAPWONDO", "Kapwondo", 104),
    ("SPECIES_SPELVEN", "Spelven", 105),
    ("SPECIES_CLOTAKU", "Clotaku", 106),
    ("SPECIES_AJARIMUS", "Ajarimus", 107),
    ("SPECIES_JARMIT", "Jarmit", 108),
    ("SPECIES_HOOTHOOT", "Hoothoot", 109),
    ("SPECIES_NOCTOWL", "Noctowl", 110),
    ("SPECIES_BAIZEAST", "Baizeast", 111),
    ("SPECIES_ELEKID", "Elekid", 112),
    ("SPECIES_ELECTABUZZ", "Electabuzz", 113),
    ("SPECIES_ELECTIVIRE", "Electivire", 114),
    ("SPECIES_MAGBY", "Magby", 115),
    ("SPECIES_MAGMAR", "Magmar", 116),
    ("SPECIES_MAGMORTAR", "Magmortar", 117),
    ("SPECIES_KANGASKHAN", "Kangaskhan", 118),
    ("SPECIES_LILEEP", "Lileep", 119),
    ("SPECIES_CRADILY", "Cradily", 120),
    ("SPECIES_GRINDON", "Grindon", 121),
    ("SPECIES_SCIMITOOTH", "Scimitooth", 122),
    ("SPECIES_AERODACTYL", "Aerodactyl", 123),
    ("SPECIES_LARVITAR", "Larvitar", 124),
    ("SPECIES_PUPITAR", "Pupitar", 125),
    ("SPECIES_TYRANITAR", "Tyranitar", 126),
    ("SPECIES_BELDUM", "Beldum", 127),
    ("SPECIES_METANG", "Metang", 128),
    ("SPECIES_METAGROSS", "Metagross", 129),
    ("SPECIES_GIBLE", "Gible", 130),
    ("SPECIES_GABITE", "Gabite", 131),
    ("SPECIES_GARCHOMP", "Garchomp", 132),
    ("SPECIES_LAQUAGON", "Laquagon", 133),
    ("SPECIES_DRAGUNE", "Dragune", 134),
    ("SPECIES_NOSTRATOS", "Nostratos", 135),
    ("SPECIES_ARTICUNO", "Articuno", 136),
    ("SPECIES_ZAPDOS", "Zapdos", 137),
    ("SPECIES_MOLTRES", "Moltres", 138),
    ("SPECIES_RAIKOU", "Raikou", 139),
    ("SPECIES_ENTEI", "Entei", 140),
    ("SPECIES_SUICUNE", "Suicune", 141),
    ("SPECIES_LYLAPSE", "Lylapse", 142),
    ("SPECIES_GANIMEDE", "Ganimede", 143),
    ("SPECIES_NEMEA", "Nemea", 144),
    ("SPECIES_DIALGA", "Dialga", 145),
    ("SPECIES_PALKIA", "Palkia", 146),
    ("SPECIES_DARKRAI", "Darkrai", 147),
    ("SPECIES_LUGIA", "Lugia", 148),
    ("SPECIES_HO-OH", "Ho-Oh", 149),
    ("SPECIES_MEWTWO", "Mewtwo", 150),
    ("SPECIES_MEW", "Mew", 151),
    ("SPECIES_BULBASAUR", "Bulbasaur", 152),
    ("SPECIES_IVYSAUR", "Ivysaur", 153),
    ("SPECIES_VENUSAUR", "Venusaur", 154),
    ("SPECIES_CHARMANDER", "Charmander", 155),
    ("SPECIES_CHARMELEON", "Charmeleon", 156),
    ("SPECIES_CHARIZARD", "Charizard", 157),
    ("SPECIES_SQUIRTLE", "Squirtle", 158),
    ("SPECIES_WARTORTLE", "Wartortle", 159),
    ("SPECIES_BLASTOISE", "Blastoise", 160),
    ("SPECIES_BASILLE", "Basille", 161),
    ("SPECIES_BASIELD", "Basield", 162),
    ("SPECIES_BASILUX", "Basilux", 163),
    ("SPECIES_PATROLEO", "Patroleo", 164),
    ("SPECIES_GARDLEON", "Gardleon", 165),
    ("SPECIES_ROYALERT", "Royalert", 166),
    ("SPECIES_KATUNA", "Katuna", 167),
    ("SPECIES_MAELSTREAM", "Maelstream", 168),
    ("SPECIES_SKELACHONE", "Skelachone", 169),
    ("SPECIES_CHESHILE", "Cheshile", 170),
    ("SPECIES_CHESHESS", "Cheshess", 171),
    ("SPECIES_CHESSIRE", "Chessire", 172),
    ("SPECIES_RIVIRD", "Rivird", 173),
    ("SPECIES_MINGOLA", "Mingola", 174),
    ("SPECIES_PACHIRISU", "Pachirisu", 175),
    ("SPECIES_PACHIRIKKU", "Pachirikku", 176),
    ("SPECIES_PUMPKID", "Pumpkid", 177),
    ("SPECIES_WIKKIN", "Wikkin", 178),
    ("SPECIES_LUNABITT", "Lunabitt", 179),
    ("SPECIES_LUNABAIN", "Lunabain", 180),
    ("SPECIES_LIEPUS", "Liepus", 181),
    ("SPECIES_LIEDORO", "Liedoro", 182),
    ("SPECIES_DITTO", "Ditto", 183),
    ("SPECIES_SMOOCHUM", "Smoochum", 184),
    ("SPECIES_JYNX", "Jynx", 185),
    ("SPECIES_ROUGELLA", "Rougella", 186),
    ("SPECIES_TAKUNI", "Takuni", 187),
    ("SPECIES_PERCUSSOON", "Percussoon", 188),
    ("SPECIES_TANUKING", "Tanuking", 189),
    ("SPECIES_SWITZA", "Switza", 190),
    ("SPECIES_SHIVERMIN", "Shivermin", 191),
    ("SPECIES_NYMPHROST", "Nymphrost", 192),
    ("SPECIES_CHATOT", "Chatot", 193),
    ("SPECIES_CONDUCTOT", "Conductot", 194),
    ("SPECIES_VIOLO", "Violo", 195),
    ("SPECIES_RUMPET", "Rumpet", 196),
    ("SPECIES_PIANON", "Pianon", 197),
    ("SPECIES_LEDYBA", "Ledyba", 198),
    ("SPECIES_LEDIAN", "Ledian", 199),
    ("SPECIES_LEDYBULK", "Ledybulk", 200),
    ("SPECIES_UNOWN", "Unown", 201),
    ("SPECIES_BISOS", "Bisos", 202),
    ("SPECIES_TAUROS", "Tauros", 203),
    ("SPECIES_LUNATONE", "Lunatone", 204),
    ("SPECIES_SOLROCK", "Solrock", 205),
    ("SPECIES_STELLITH", "Stellith", 206),
    ("SPECIES_PLANITE", "Planite", 207),
    ("SPECIES_MODRA", "Modra", 208),
    ("SPECIES_KOMORAGON", "Komoragon", 209),
    ("SPECIES_REMORAID", "Remoraid", 210),
    ("SPECIES_OCTILLERY", "Octillery", 211),
    ("SPECIES_TENTACOOL", "Tentacool", 212),
    ("SPECIES_TENTACRUEL", "Tentacruel", 213),
    ("SPECIES_TENTYRANT", "Tentyrant", 214),
    ("SPECIES_LILYNARY", "Lilynary", 215),
    ("SPECIES_KAMINARY", "Kaminary", 216),
    ("SPECIES_GRIEFLAME", "Grieflame", 217),
    ("SPECIES_SCORMENT", "Scorment", 218),
    ("SPECIES_RUBBALL", "Rubball", 219),
    ("SPECIES_PHANTONATE", "Phantonate", 220),
    ("SPECIES_STRAWICK", "Strawick", 221),
    ("SPECIES_STRAWICKED", "Strawicked", 222),
    ("SPECIES_VOLTORB", "Voltorb", 223),
    ("SPECIES_ELECTRODE", "Electrode", 224),
    ("SPECIES_SPHERICOIL", "Sphericoil", 225),
    ("SPECIES_MURKROW", "Murkrow", 226),
    ("SPECIES_HONCHKROW", "Honchkrow", 227),
    ("SPECIES_WHISMUR", "Whismur", 228),
    ("SPECIES_LOUDRED", "Loudred", 229),
    ("SPECIES_EXPLOUD", "Exploud", 230),
    ("SPECIES_KRABBY", "Krabby", 231),
    ("SPECIES_KINGLER", "Kingler", 232),
    ("SPECIES_PUFFUME", "Puffume", 233),
    ("SPECIES_TURBLIMP", "Turblimp", 234),
    ("SPECIES_YOLKID", "Yolkid", 235),
    ("SPECIES_CORENOM", "Corenom", 236),
    ("SPECIES_COROPPER", "Coropper", 237),
    ("SPECIES_CORUDA", "Coruda", 238),
    ("SPECIES_CORAGA", "Coraga", 239),
    ("SPECIES_LIZZLE", "Lizzle", 240),
    ("SPECIES_DRIZZLOB", "Drizzlob", 241),
    ("SPECIES_DROUDROP", "Droudrop", 242),
    ("SPECIES_DROUDRUM", "Droudrum", 243),
    ("SPECIES_CLOUFF", "Clouff", 244),
    ("SPECIES_CLOUBUS", "Cloubus", 245),
    ("SPECIES_DVAARAK", "Dvaarak", 246),
    ("SPECIES_SNEASEL", "Sneasel", 247),
    ("SPECIES_WEAVILE", "Weavile", 248),
    ("SPECIES_SHROOMISH", "Shroomish", 249),
    ("SPECIES_BRELOOM", "Breloom", 250),
    ("SPECIES_DOODLOO", "Doodloo", 251),
    ("SPECIES_BILLSERK", "Billserk", 252),
    ("SPECIES_SABLEYE", "Sableye", 253),
    ("SPECIES_SABLEATER", "Sableater", 254),
    ("SPECIES_MAWILE", "Mawile", 255),
    ("SPECIES_JAWILE", "Jawile", 256),
    ("SPECIES_SCYTHER", "Scyther", 257),
    ("SPECIES_SCIZOR", "Scizor", 258),
    ("SPECIES_PINSIR", "Pinsir", 259),
    ("SPECIES_PINCHOR", "Pinchor", 260),
    ("SPECIES_EKANS", "Ekans", 261),
    ("SPECIES_ARBOK", "Arbok", 262),
    ("SPECIES_ADNOKANA", "Adnokana", 263),
    ("SPECIES_KOFFING", "Koffing", 264),
    ("SPECIES_WEEZING", "Weezing", 265),
    ("SPECIES_CHEAUKING", "Cheauking", 266),
    ("SPECIES_DUSKULL", "Duskull", 267),
    ("SPECIES_DUSCLOPS", "Dusclops", 268),
    ("SPECIES_DUSKNOIR", "Dusknoir", 269),
    ("SPECIES_LICKITUNG", "Lickitung", 270),
    ("SPECIES_LICKILICKY", "Lickilicky", 271),
    ("SPECIES_SPINARAK", "Spinarak", 272),
    ("SPECIES_ARIADOS", "Ariados", 273),
    ("SPECIES_JOLTIK", "Joltik", 274),
    ("SPECIES_GALVANTULA", "Galvantula", 275),
    ("SPECIES_NINCADA", "Nincada", 290),
    ("SPECIES_NINJASK", "Ninjask", 291),
    ("SPECIES_SHEDINJA", "Shedinja", 292),
    ("SPECIES_GUPPYRE", "Guppyre", 276),
    ("SPECIES_DIADUNA", "Diaduna", 277),
    ("SPECIES_COMBOUND", "Combound", 285),
    ("SPECIES_WOMBATON", "Wombaton", 286),
    ("SPECIES_SPINDA", "Spinda", 327),
    ("SPECIES_RELICANTH", "Relicanth", 278),
    ("SPECIES_RELICORE", "Relicore", 279),
    ("SPECIES_TROJALMON", "Trojalmon", 283),
    ("SPECIES_PUNCHILD", "Punchild", 284),
    ("SPECIES_SHUPPET", "Shuppet", 320),
    ("SPECIES_BANETTE", "Banette", 321),
    ("SPECIES_RALTS", "Ralts", 300),
    ("SPECIES_KIRLIA", "Kirlia", 301),
    ("SPECIES_DWEBBLE", "Dwebble", 352),
    ("SPECIES_CACNEA", "Cacnea", 343),
    ("SPECIES_CACTURNE", "Cacturne", 344),
    ("SPECIES_NARWHAIL", "Narwhail", 299),
    ("SPECIES_PILOSWINE", "Piloswine", 324),
    ("SPECIES_GARDEVOIR", "Gardevoir", 302),
    ("SPECIES_PRESSIE", "Pressie", 339),
    ("SPECIES_LAPRAS", "Lapras", 340),
    ("SPECIES_LILLIGANT", "Lilligant", 370),
    ("SPECIES_SHRETAINER", "Shretainer", 341),
    ("SPECIES_SAMUSHRAI", "Samushrai", 342),
    ("SPECIES_MANDIBLADE", "Mandiblade", 349),
    ("SPECIES_MERCENADE", "Mercenade", 350),
    ("SPECIES_SKORUPI", "Skorupi", 318),
    ("SPECIES_DRAPION", "Drapion", 319),
    ("SPECIES_CARNIVINE", "Carnivine", 328),
    ("SPECIES_CARNIVICE", "Carnivice", 329),
    ("SPECIES_TOXROACH", "Toxroach", 330),
    ("SPECIES_YULFOE", "Yulfoe", 296),
    ("SPECIES_DORFIN", "Dorfin", 297),
    ("SPECIES_RUDEBARB", "Rudebarb", 309),
    ("SPECIES_DISLICHEN", "Dislichen", 310),
    ("SPECIES_RANCONETTE", "Ranconette", 322),
    ("SPECIES_SWINUB", "Swinub", 323),
    ("SPECIES_DUNSPARCE", "Dunsparce", 363),
    ("SPECIES_AULDSPARCE", "Auldsparce", 364),
    ("SPECIES_FARFETCHD", "Farfetch'd", 365),
    ("SPECIES_COCROGUE", "Cocrogue", 331),
    ("SPECIES_LEPHAN", "Lephan", 332),
    ("SPECIES_TORKOAL", "Torkoal", 361),
    ("SPECIES_GALAVAGOS", "Galavagos", 362),
    ("SPECIES_LUVDISC", "Luvdisc", 337),
    ("SPECIES_VALENTIDE", "Valentide", 338),
    ("SPECIES_DARCA", "Darca", 298),
    ("SPECIES_MAMOSWINE", "Mamoswine", 325),
    ("SPECIES_STUNFISK", "Stunfisk", 326),
    ("SPECIES_LUMOSS", "Lumoss", 311),
    ("SPECIES_CRYOGONAL", "Cryogonal", 312),
    ("SPECIES_GALLADE", "Gallade", 303),
    ("SPECIES_SELODY", "Selody", 307),
    ("SPECIES_ROOTEN", "Rooten", 308),
    ("SPECIES_GANERTH", "Ganerth", 333),
    ("SPECIES_KLINK", "Klink", 334),
    ("SPECIES_BLIZENTORK", "Blizentork", 360),
    ("SPECIES_FERROTHORN", "Ferrothorn", 355),
    ("SPECIES_TYNAMO", "Tynamo", 356),
    ("SPECIES_GEODUDE", "Geodude", 315),
    ("SPECIES_HAPPINY", "Happiny", 287),
    ("SPECIES_CHANSEY", "Chansey", 288),
    ("SPECIES_BLISSEY", "Blissey", 289),
    ("SPECIES_GRAVELER", "Graveler", 316),
    ("SPECIES_GOLEM", "Golem", 317),
    ("SPECIES_EELEKTRIK", "Eelektrik", 357),
    ("SPECIES_SANDSHREW", "Sandshrew", 293),
    ("SPECIES_SANDSLASH", "Sandslash", 294),
    ("SPECIES_SANDRILL", "Sandrill", 295),
    ("SPECIES_RDUCKULUS", "R'duckulus", 366),
    ("SPECIES_SCRAGGY", "Scraggy", 367),
    ("SPECIES_SCRAFTY", "Scrafty", 368),
    ("SPECIES_DELIBIRD", "Delibird", 359),
    ("SPECIES_CRUSTLE", "Crustle", 353),
    ("SPECIES_FERROSEED", "Ferroseed", 354),
    ("SPECIES_KLINKLANG", "Klinklang", 336),
    ("SPECIES_KLANG", "Klang", 335),
    ("SPECIES_PETILIL", "Petilil", 369),
    ("SPECIES_KIRGICIA", "Kirgicia", 304),
    ("SPECIES_GLAMARDE", "Glamarde", 305),
    ("SPECIES_SEALKIE", "Sealkie", 306),
    ("SPECIES_TERUBIM", "Terubim", 351),
    ("SPECIES_COMBANT", "Combant", 313),
    ("SPECIES_ARINCESS", "Arincess", 314),
    ("SPECIES_PTERVUS", "Ptervus", 345),
    ("SPECIES_PTERIARCH", "Pteriarch", 346),
    ("SPECIES_TYRANOS", "Tyranos", 347),
    ("SPECIES_AMBILADE", "Ambilade", 348),
    ("SPECIES_FUJINEL", "Fujinel", 280),
    ("SPECIES_SABRINEL", "Sabrinel", 281),
    ("SPECIES_SMALMON", "Smalmon", 282),
    ("SPECIES_MIENFOO", "Mienfoo", 371),
    ("SPECIES_MIENSHAO", "Mienshao", 372),
    ("SPECIES_SANDILE", "Sandile", 373),
    ("SPECIES_KROKOROK", "Krokorok", 374),
    ("SPECIES_KROOKODILE", "Krookodile", 375),
    ("SPECIES_ROYTSAR", "Roytsar", 376),
    ("SPECIES_GATANOIA", "Gatanoia", 377),
    ("SPECIES_LUKEWRAN", "Lukewran", 378),
    ("SPECIES_HEATRAN", "Heatran", 379),
    ("SPECIES_PHIONE", "Phione", 382),
    ("SPECIES_MANAPHY", "Manaphy", 383),
    ("SPECIES_ALDINA", "Aldina", 384),
    ("SPECIES_LATIAS", "Latias", 380),
    ("SPECIES_LATIOS", "Latios", 381),
    ("SPECIES_ALMARIA", "Almaria", 385),
    ("SPECIES_ASPHERE", "Asphere", 386),
    ("SPECIES_EELEKTROSS", "Eelektross", 358),
]


def load_json_data(data_name: str) -> Union[List[Any], Dict[str, Any]]:
    return orjson.loads(pkgutil.get_data(__name__, "data/" + data_name).decode("utf-8-sig"))


def _init() -> None:
    extracted_data: Dict[str, Any] = load_json_data("extracted_data.json")
    data.rom_name = extracted_data["rom_name"]
    data.constants = extracted_data["constants"]
    data.ram_addresses = extracted_data["misc_ram_addresses"]
    data.rom_addresses = extracted_data["misc_rom_addresses"]

    location_data = load_json_data("locations.json")
    event_data = load_json_data("events.json")
    item_data = load_json_data("items.json")

    # Create map data
    for map_name, map_json in extracted_data["maps"].items():
        land_encounters = None
        water_encounters = None
        fishing_encounters = None

        if "land_encounters" in map_json:
            land_slots: List[EncounterSpeciesData] = []
            for slot_data in map_json["land_encounters"]["slots"]:
                land_slots.append(EncounterSpeciesData(
                    slot_data["default_species"],
                    slot_data["min_level"],
                    slot_data["max_level"]
                ))
            land_encounters = EncounterTableData(
                land_slots,
                map_json["land_encounters"]["address"]
            )
        if "water_encounters" in map_json:
            water_slots: List[EncounterSpeciesData] = []
            for slot_data in map_json["water_encounters"]["slots"]:
                water_slots.append(EncounterSpeciesData(
                    slot_data["default_species"],
                    slot_data["min_level"],
                    slot_data["max_level"]
                ))
            water_encounters = EncounterTableData(
                water_slots,
                map_json["water_encounters"]["address"]
            )
        if "fishing_encounters" in map_json:
            fishing_slots: List[EncounterSpeciesData] = []
            for slot_data in map_json["fishing_encounters"]["slots"]:
                fishing_slots.append(EncounterSpeciesData(
                    slot_data["default_species"],
                    slot_data["min_level"],
                    slot_data["max_level"]
                ))
            fishing_encounters = EncounterTableData(
                fishing_slots,
                map_json["fishing_encounters"]["address"]
            )

        data.maps[map_name] = MapData(
            map_name,
            map_json["header_address"],
            land_encounters,
            water_encounters,
            fishing_encounters,
            True
        )

    # Load/merge region json files
    region_json_list = []
    for file in resource_listdir(__name__, "data/regions"):
        if not resource_isdir(__name__, "data/regions/" + file):
            region_json_list.append(load_json_data("regions/" + file))

    regions_json = {}
    for region_subset in region_json_list:
        for region_name, region_json in region_subset.items():
            if region_name in regions_json:
                raise AssertionError("Pokemon Vega: Region [{region_name}] was defined multiple times")
            regions_json[region_name] = region_json

    # Create region data
    claimed_locations: Set[str] = set()
    claimed_warps: Set[str] = set()

    data.regions = {}
    for region_id, region_json in regions_json.items():
        parent_map = data.maps[region_json["parent_map"]] if region_json["parent_map"] is not None else None

        if parent_map is not None:
            parent_map.sphere_ruins = region_json["sphere_ruins"]

        new_region = RegionData(
            region_id,
            region_json["name"],
            parent_map,
            region_json["encounter_region"],
            region_json["has_land"],
            region_json["has_water"],
            region_json["has_fishing"],
            region_json["sphere_ruins"]
        )

        # Locations
        for location_id in region_json["locations"]:
            if location_id in claimed_locations:
                raise AssertionError(f"Pokemon Vega: Location [{location_id}] was claimed by multiple regions")

            location_json = extracted_data["locations"][location_id]

            if "NIMBLEAF_REWARD" in location_id:
                import re
                trainer = re.match("TRAINER_([A-Z0-9_]+)_NIMBLEAF_REWARD", location_id).group(1)
                alternate_rival_jsons = [extracted_data["locations"][alternate] for alternate in [
                    f"TRAINER_{trainer}_PEYERO_REWARD",
                    f"TRAINER_{trainer}_LIQUIPUT_REWARD"
                ]]

                location_address: List[int] = []

                location_address = [location_json["address"]]

                for alternate_rival_json in alternate_rival_jsons:
                    location_address.append(alternate_rival_json["address"])

                new_location = LocationData(
                    location_id,
                    location_data[location_id]["name"],
                    region_id,
                    location_json["default_item"],
                    location_address,
                    location_json["flag"],
                    frozenset(location_data[location_id]["tags"])
                )
            else:
                new_location = LocationData(
                    location_id,
                    location_data[location_id]["name"],
                    region_id,
                    location_json["default_item"],
                    location_json["address"],
                    location_json["flag"],
                    frozenset(location_data[location_id]["tags"])
                )

            new_region.locations.append(location_id)
            data.locations[location_id] = new_location
            claimed_locations.add(location_id)

        # Events
        for event_id in region_json["events"]:
            new_event = EventData(
                event_id,
                event_data[event_id]["name"],
                event_data[event_id]["item"],
                region_id,
                frozenset(event_data[event_id]["tags"])
            )
            new_region.events.append(event_id)
            data.events[event_id] = new_event

        # Exits
        new_region.exits = region_json["exits"]

        # Warps
        for encoded_warp, name in region_json["warps"].items():
            if encoded_warp in claimed_warps:
                raise AssertionError(f"Pokemon Vega: Warp [{encoded_warp}] was claimed by multiple regions")
            new_region.warps.append(encoded_warp)
            data.warps[encoded_warp] = Warp(encoded_warp, name, region_id)
            claimed_warps.add(encoded_warp)

        new_region.warps.sort()

        data.regions[region_id] = new_region

    # Create item data
    data.items = {}
    for item_id_name, attributes in item_data.items():
        if attributes["classification"] == "PROGRESSION":
            item_classification = ItemClassification.progression
        elif attributes["classification"] == "USEFUL":
            item_classification = ItemClassification.useful
        elif attributes["classification"] == "FILLER":
            item_classification = ItemClassification.filler
        elif attributes["classification"] == "TRAP":
            item_classification = ItemClassification.trap
        else:
            raise ValueError(f"Unknown classification {attributes['classification']} for item {item_id_name}")

        data.items[data.constants[item_id_name]] = ItemData(
            attributes["name"],
            data.constants[item_id_name],
            item_classification,
            frozenset(attributes["tags"])
        )

    # Create warp map
    for warp, destination in extracted_data["warps"].items():
        data.warp_map[warp] = None if destination == "" else destination

    # Create species data
    max_species_id = 0
    evo_item_map: Dict[int, int] = {
        data.constants["ITEM_KINGS_ROCK_EVO"]: data.constants["ITEM_KINGS_ROCK"],
        data.constants["ITEM_METAL_COAT_EVO"]: data.constants["ITEM_METAL_COAT"],
        data.constants["ITEM_DEEP_SEA_SCALE_EVO"]: data.constants["ITEM_DEEP_SEA_SCALE"],
        data.constants["ITEM_DEEP_SEA_TOOTH_EVO"]: data.constants["ITEM_DEEP_SEA_TOOTH"]
    }
    for species_id_name, species_name, species_dex_number in ALL_SPECIES:
        species_id = data.constants[species_id_name]
        max_species_id = max(species_id, max_species_id)
        species_data = extracted_data["species"][species_id]
        num_evolutions = len(species_data["evolutions"])
        evolution_index = 1

        learnset = [LearnsetMove(item["level"], item["move_id"]) for item in species_data["learnset"]["moves"]]

        data.species[species_id] = SpeciesData(
            species_id_name,
            species_name,
            species_id,
            species_dex_number,
            BaseStats(
                species_data["base_stats"][0],
                species_data["base_stats"][1],
                species_data["base_stats"][2],
                species_data["base_stats"][3],
                species_data["base_stats"][4],
                species_data["base_stats"][5]
            ),
            (species_data["types"][0], species_data["types"][1]),
            (species_data["abilities"][0], species_data["abilities"][1]),
            [EvolutionData(
                evo_item_map[evolution_data["param"]]
                if evolution_data["param"] in evo_item_map else evolution_data["param"],
                evolution_data["species"],
                EVOLUTION_METHOD_TYPE[evolution_data["method"]]
            ) for evolution_data in species_data["evolutions"]],
            None,
            species_data["catch_rate"],
            species_data["friendship"],
            learnset,
            int(species_data["tmhm_learnset"], 16),
            species_data["learnset"]["address"],
            species_data["address"]
        )

        for evolution_data in data.species[species_id].evolutions:
            if num_evolutions > 1:
                data.evolutions[f"{species_name} {evolution_index}"] = EvolutionData(
                    evolution_data.param,
                    evolution_data.species_id,
                    evolution_data.method
                )
                evolution_index += 1
            else:
                data.evolutions[species_name] = EvolutionData(
                    evolution_data.param,
                    evolution_data.species_id,
                    evolution_data.method
                )

    for species in data.species.values():
        for evolution in species.evolutions:
            data.species[evolution.species_id].pre_evolution = species.species_id

    # Create starter data
    for name, starter_data in extracted_data["starter_pokemon"].items():
        data.starters[name] = StarterData(
            starter_data["species"],
            starter_data["player_address"],
            starter_data["rival_address"]
        )

    # Create legendary pokemon data
    for name, legendary_data in extracted_data["legendary_pokemon"].items():
        data.legendary_pokemon[name] = MiscPokemonData(
            legendary_data["species"],
            legendary_data["level"],
            legendary_data["address"],
            legendary_data["level_address"]
        )

    # Create misc pokemon data
    for name, misc_data in extracted_data["misc_pokemon"].items():
        data.misc_pokemon[name] = MiscPokemonData(
            misc_data["species"],
            misc_data["level"],
            misc_data["address"],
            misc_data["level_address"]
        )

    # Create trainer data
    for name, trainer_data in extracted_data["trainers"].items():
        party_data = trainer_data["party"]
        data.trainers[name] = TrainerData(
            TrainerPartyData([
                    TrainerPokemonData(
                        pokemon["species"],
                        pokemon["level"],
                        (pokemon["moves"][0],
                         pokemon["moves"][1],
                         pokemon["moves"][2],
                         pokemon["moves"][3]) if "moves" in pokemon else None,
                        False
                    ) for pokemon in party_data],
                POKEMON_DATA_TYPE[trainer_data["data_type"]],
                trainer_data["party_address"]
            ),
            trainer_data["address"]
        )

    # TM/HM Moves
    data.tmhm_moves = extracted_data["tmhm_moves"]

    # Abilities
    data.abilities = {j: data.constants[i] for i, j in [
        ("ABILITY_STENCH", "Stench"),
        ("ABILITY_DRIZZLE", "Drizzle"),
        ("ABILITY_SPEED_BOOST", "Speed Boost"),
        ("ABILITY_BATTLE_ARMOR", "Battle Armor"),
        ("ABILITY_STURDY", "Sturdy"),
        ("ABILITY_DAMP", "Damp"),
        ("ABILITY_LIMBER", "Limber"),
        ("ABILITY_SAND_VEIL", "Sand Veil"),
        ("ABILITY_STATIC", "Static"),
        ("ABILITY_VOLT_ABSORB", "Volt Absorb"),
        ("ABILITY_WATER_ABSORB", "Water Absorb"),
        ("ABILITY_OBLIVIOUS", "Oblivious"),
        ("ABILITY_CLOUD_NINE", "Cloud Nine"),
        ("ABILITY_COMPOUND_EYES", "Compoundeyes"),
        ("ABILITY_INSOMNIA", "Insomnia"),
        ("ABILITY_COLOR_CHANGE", "Color Change"),
        ("ABILITY_IMMUNITY", "Immunity"),
        ("ABILITY_FLASH_FIRE", "Flash Fire"),
        ("ABILITY_SHIELD_DUST", "Shield Dust"),
        ("ABILITY_OWN_TEMPO", "Own Tempo"),
        ("ABILITY_SUCTION_CUPS", "Suction Cups"),
        ("ABILITY_INTIMIDATE", "Intimidate"),
        ("ABILITY_SHADOW_TAG", "Shadow Tag"),
        ("ABILITY_ROUGH_SKIN", "Rough Skin"),
        ("ABILITY_WONDER_GUARD", "Wonder Guard"),
        ("ABILITY_LEVITATE", "Levitate"),
        ("ABILITY_EFFECT_SPORE", "Effect Spore"),
        ("ABILITY_SYNCHRONIZE", "Synchronize"),
        ("ABILITY_CLEAR_BODY", "Clear Body"),
        ("ABILITY_NATURAL_CURE", "Natural Cure"),
        ("ABILITY_LIGHTNING_ROD", "Lightningrod"),
        ("ABILITY_SERENE_GRACE", "Serene Grace"),
        ("ABILITY_SWIFT_SWIM", "Swift Swim"),
        ("ABILITY_CHLOROPHYLL", "Chlorophyll"),
        ("ABILITY_ILLUMINATE", "Illuminate"),
        ("ABILITY_TRACE", "Trace"),
        ("ABILITY_HUGE_POWER", "Huge Power"),
        ("ABILITY_POISON_POINT", "Poison Point"),
        ("ABILITY_INNER_FOCUS", "Inner Focus"),
        ("ABILITY_MAGMA_ARMOR", "Magma Armor"),
        ("ABILITY_WATER_VEIL", "Water Veil"),
        ("ABILITY_MAGNET_PULL", "Magnet Pull"),
        ("ABILITY_SOUNDPROOF", "Soundproof"),
        ("ABILITY_RAIN_DISH", "Rain Dish"),
        ("ABILITY_SAND_STREAM", "Sand Stream"),
        ("ABILITY_PRESSURE", "Pressure"),
        ("ABILITY_THICK_FAT", "Thick Fat"),
        ("ABILITY_EARLY_BIRD", "Early Bird"),
        ("ABILITY_FLAME_BODY", "Flame Body"),
        ("ABILITY_RUN_AWAY", "Run Away"),
        ("ABILITY_KEEN_EYE", "Keen Eye"),
        ("ABILITY_HYPER_CUTTER", "Hyper Cutter"),
        ("ABILITY_PICKUP", "Pickup"),
        ("ABILITY_TRUANT", "Truant"),
        ("ABILITY_HUSTLE", "Hustle"),
        ("ABILITY_CUTE_CHARM", "Cute Charm"),
        ("ABILITY_PLUS", "Plus"),
        ("ABILITY_MINUS", "Minus"),
        ("ABILITY_FORECAST", "Forecast"),
        ("ABILITY_STICKY_HOLD", "Sticky Hold"),
        ("ABILITY_SHED_SKIN", "Shed Skin"),
        ("ABILITY_GUTS", "Guts"),
        ("ABILITY_MARVEL_SCALE", "Marvel Scale"),
        ("ABILITY_LIQUID_OOZE", "Liquid Ooze"),
        ("ABILITY_OVERGROW", "Overgrow"),
        ("ABILITY_BLAZE", "Blaze"),
        ("ABILITY_TORRENT", "Torrent"),
        ("ABILITY_SWARM", "Swarm"),
        ("ABILITY_ROCK_HEAD", "Rock Head"),
        ("ABILITY_DROUGHT", "Drought"),
        ("ABILITY_ARENA_TRAP", "Arena Trap"),
        ("ABILITY_VITAL_SPIRIT", "Vital Spirit"),
        ("ABILITY_WHITE_SMOKE", "White Smoke"),
        ("ABILITY_PURE_POWER", "Pure Power"),
        ("ABILITY_SHELL_ARMOR", "Shell Armor"),
        ("ABILITY_CACOPHONY", "Cacophony"),
        ("ABILITY_AIR_LOCK", "Air Lock")
    ]}

    # Moves
    data.moves = {j: data.constants[i] for i, j in [
        ("MOVE_POUND", "Pound"),
        ("MOVE_KARATE_CHOP", "Karate Chop"),
        ("MOVE_DOUBLE_SLAP", "Doubleslap"),
        ("MOVE_COMET_PUNCH", "Comet Punch"),
        ("MOVE_MEGA_PUNCH", "Mega Punch"),
        ("MOVE_PAY_DAY", "Pay Day"),
        ("MOVE_FIRE_PUNCH", "Fire Punch"),
        ("MOVE_ICE_PUNCH", "Ice Punch"),
        ("MOVE_THUNDER_PUNCH", "Thunderpunch"),
        ("MOVE_SCRATCH", "Scratch"),
        ("MOVE_VICE_GRIP", "Vicegrip"),
        ("MOVE_GUILLOTINE", "Guillotine"),
        ("MOVE_RAZOR_WIND", "Razor Wind"),
        ("MOVE_SWORDS_DANCE", "Swords Dance"),
        ("MOVE_CUT", "Cut"),
        ("MOVE_GUST", "Gust"),
        ("MOVE_WING_ATTACK", "Wing Attack"),
        ("MOVE_WHIRLWIND", "Whirlwind"),
        ("MOVE_FLY", "Fly"),
        ("MOVE_BIND", "Bind"),
        ("MOVE_SLAM", "Slam"),
        ("MOVE_VINE_WHIP", "Vine Whip"),
        ("MOVE_STOMP", "Stomp"),
        ("MOVE_DOUBLE_KICK", "Double Kick"),
        ("MOVE_MEGA_KICK", "Mega Kick"),
        ("MOVE_JUMP_KICK", "Jump Kick"),
        ("MOVE_ROLLING_KICK", "Rolling Kick"),
        ("MOVE_SAND_ATTACK", "Sand-Attack"),
        ("MOVE_HEADBUTT", "Headbutt"),
        ("MOVE_HORN_ATTACK", "Horn Attack"),
        ("MOVE_FURY_ATTACK", "Fury Attack"),
        ("MOVE_HORN_DRILL", "Horn Drill"),
        ("MOVE_TACKLE", "Tackle"),
        ("MOVE_BODY_SLAM", "Body Slam"),
        ("MOVE_WRAP", "Wrap"),
        ("MOVE_TAKE_DOWN", "Take Down"),
        ("MOVE_THRASH", "Thrash"),
        ("MOVE_DOUBLE_EDGE", "Double-Edge"),
        ("MOVE_TAIL_WHIP", "Tail Whip"),
        ("MOVE_POISON_STING", "Poison Sting"),
        ("MOVE_TWINEEDLE", "Twineedle"),
        ("MOVE_PIN_MISSILE", "Pin Missile"),
        ("MOVE_LEER", "Leer"),
        ("MOVE_BITE", "Bite"),
        ("MOVE_GROWL", "Growl"),
        ("MOVE_ROAR", "Roar"),
        ("MOVE_SING", "Sing"),
        ("MOVE_SUPERSONIC", "Supersonic"),
        ("MOVE_SONIC_BOOM", "Sonicboom"),
        ("MOVE_DISABLE", "Disable"),
        ("MOVE_ACID", "Acid"),
        ("MOVE_EMBER", "Ember"),
        ("MOVE_FLAMETHROWER", "Flamethrower"),
        ("MOVE_MIST", "Mist"),
        ("MOVE_WATER_GUN", "Water Gun"),
        ("MOVE_HYDRO_PUMP", "Hydro Pump"),
        ("MOVE_SURF", "Surf"),
        ("MOVE_ICE_BEAM", "Ice Beam"),
        ("MOVE_BLIZZARD", "Blizzard"),
        ("MOVE_PSYBEAM", "Psybeam"),
        ("MOVE_BUBBLE_BEAM", "Bubblebeam"),
        ("MOVE_AURORA_BEAM", "Aurora Beam"),
        ("MOVE_HYPER_BEAM", "Hyper Beam"),
        ("MOVE_PECK", "Peck"),
        ("MOVE_DRILL_PECK", "Drill Peck"),
        ("MOVE_SUBMISSION", "Submission"),
        ("MOVE_LOW_KICK", "Low Kick"),
        ("MOVE_COUNTER", "Counter"),
        ("MOVE_SEISMIC_TOSS", "Seismic Toss"),
        ("MOVE_STRENGTH", "Strength"),
        ("MOVE_ABSORB", "Absorb"),
        ("MOVE_MEGA_DRAIN", "Mega Drain"),
        ("MOVE_LEECH_SEED", "Leech Seed"),
        ("MOVE_GROWTH", "Growth"),
        ("MOVE_RAZOR_LEAF", "Razor Leaf"),
        ("MOVE_SOLAR_BEAM", "Solarbeam"),
        ("MOVE_POISON_POWDER", "Poisonpowder"),
        ("MOVE_STUN_SPORE", "Stun Spore"),
        ("MOVE_SLEEP_POWDER", "Sleep Powder"),
        ("MOVE_PETAL_DANCE", "Petal Dance"),
        ("MOVE_STRING_SHOT", "String Shot"),
        ("MOVE_DRAGON_RAGE", "Dragon Rage"),
        ("MOVE_FIRE_SPIN", "Fire Spin"),
        ("MOVE_THUNDER_SHOCK", "Thundershock"),
        ("MOVE_THUNDERBOLT", "Thunderbolt"),
        ("MOVE_THUNDER_WAVE", "Thunder Wave"),
        ("MOVE_THUNDER", "Thunder"),
        ("MOVE_ROCK_THROW", "Rock Throw"),
        ("MOVE_EARTHQUAKE", "Earthquake"),
        ("MOVE_FISSURE", "Fissure"),
        ("MOVE_DIG", "Dig"),
        ("MOVE_TOXIC", "Toxic"),
        ("MOVE_CONFUSION", "Confusion"),
        ("MOVE_PSYCHIC", "Psychic"),
        ("MOVE_HYPNOSIS", "Hypnosis"),
        ("MOVE_MEDITATE", "Meditate"),
        ("MOVE_AGILITY", "Agility"),
        ("MOVE_QUICK_ATTACK", "Quick Attack"),
        ("MOVE_RAGE", "Rage"),
        ("MOVE_TELEPORT", "Teleport"),
        ("MOVE_NIGHT_SHADE", "Night Shade"),
        ("MOVE_MIMIC", "Mimic"),
        ("MOVE_SCREECH", "Screech"),
        ("MOVE_DOUBLE_TEAM", "Double Team"),
        ("MOVE_RECOVER", "Recover"),
        ("MOVE_HARDEN", "Harden"),
        ("MOVE_MINIMIZE", "Minimize"),
        ("MOVE_SMOKESCREEN", "Smokescreen"),
        ("MOVE_CONFUSE_RAY", "Confuse Ray"),
        ("MOVE_WITHDRAW", "Withdraw"),
        ("MOVE_DEFENSE_CURL", "Defense Curl"),
        ("MOVE_BARRIER", "Barrier"),
        ("MOVE_LIGHT_SCREEN", "Light Screen"),
        ("MOVE_HAZE", "Haze"),
        ("MOVE_REFLECT", "Reflect"),
        ("MOVE_FOCUS_ENERGY", "Focus Energy"),
        ("MOVE_BIDE", "Bide"),
        ("MOVE_METRONOME", "Metronome"),
        ("MOVE_MIRROR_MOVE", "Mirror Move"),
        ("MOVE_SELF_DESTRUCT", "Selfdestruct"),
        ("MOVE_EGG_BOMB", "Egg Bomb"),
        ("MOVE_LICK", "Lick"),
        ("MOVE_SMOG", "Smog"),
        ("MOVE_SLUDGE", "Sludge"),
        ("MOVE_BONE_CLUB", "Bone Club"),
        ("MOVE_FIRE_BLAST", "Fire Blast"),
        ("MOVE_WATERFALL", "Waterfall"),
        ("MOVE_CLAMP", "Clamp"),
        ("MOVE_SWIFT", "Swift"),
        ("MOVE_SKULL_BASH", "Skull Bash"),
        ("MOVE_SPIKE_CANNON", "Spike Cannon"),
        ("MOVE_CONSTRICT", "Constrict"),
        ("MOVE_AMNESIA", "Amnesia"),
        ("MOVE_KINESIS", "Kinesis"),
        ("MOVE_SOFT_BOILED", "Softboiled"),
        ("MOVE_HI_JUMP_KICK", "Hi Jump Kick"),
        ("MOVE_GLARE", "Glare"),
        ("MOVE_DREAM_EATER", "Dream Eater"),
        ("MOVE_POISON_GAS", "Poison Gas"),
        ("MOVE_BARRAGE", "Barrage"),
        ("MOVE_LEECH_LIFE", "Leech Life"),
        ("MOVE_LOVELY_KISS", "Lovely Kiss"),
        ("MOVE_SKY_ATTACK", "Sky Attack"),
        ("MOVE_TRANSFORM", "Transform"),
        ("MOVE_BUBBLE", "Bubble"),
        ("MOVE_DIZZY_PUNCH", "Dizzy Punch"),
        ("MOVE_SPORE", "Spore"),
        ("MOVE_FLASH", "Flash"),
        ("MOVE_PSYWAVE", "Psywave"),
        ("MOVE_SPLASH", "Splash"),
        ("MOVE_ACID_ARMOR", "Acid Armor"),
        ("MOVE_CRABHAMMER", "Crabhammer"),
        ("MOVE_EXPLOSION", "Explosion"),
        ("MOVE_FURY_SWIPES", "Fury Swipes"),
        ("MOVE_BONEMERANG", "Bonemerang"),
        ("MOVE_REST", "Rest"),
        ("MOVE_ROCK_SLIDE", "Rock Slide"),
        ("MOVE_HYPER_FANG", "Hyper Fang"),
        ("MOVE_SHARPEN", "Sharpen"),
        ("MOVE_CONVERSION", "Conversion"),
        ("MOVE_TRI_ATTACK", "Tri Attack"),
        ("MOVE_SUPER_FANG", "Super Fang"),
        ("MOVE_SLASH", "Slash"),
        ("MOVE_SUBSTITUTE", "Substitute"),
        ("MOVE_SKETCH", "Sketch"),
        ("MOVE_TRIPLE_KICK", "Triple Kick"),
        ("MOVE_THIEF", "Thief"),
        ("MOVE_SPIDER_WEB", "Spider Web"),
        ("MOVE_MIND_READER", "Mind Reader"),
        ("MOVE_NIGHTMARE", "Nightmare"),
        ("MOVE_FLAME_WHEEL", "Flame Wheel"),
        ("MOVE_SNORE", "Snore"),
        ("MOVE_CURSE", "Curse"),
        ("MOVE_FLAIL", "Flail"),
        ("MOVE_CONVERSION_2", "Conversion 2"),
        ("MOVE_AEROBLAST", "Aeroblast"),
        ("MOVE_COTTON_SPORE", "Cotton Spore"),
        ("MOVE_REVERSAL", "Reversal"),
        ("MOVE_SPITE", "Spite"),
        ("MOVE_POWDER_SNOW", "Powder Snow"),
        ("MOVE_PROTECT", "Protect"),
        ("MOVE_MACH_PUNCH", "Mach Punch"),
        ("MOVE_SCARY_FACE", "Scary Face"),
        ("MOVE_FEINT_ATTACK", "Feint Attack"),
        ("MOVE_SWEET_KISS", "Sweet Kiss"),
        ("MOVE_BELLY_DRUM", "Belly Drum"),
        ("MOVE_SLUDGE_BOMB", "Sludge Bomb"),
        ("MOVE_MUD_SLAP", "Mud-Slap"),
        ("MOVE_OCTAZOOKA", "Octazooka"),
        ("MOVE_SPIKES", "Spikes"),
        ("MOVE_ZAP_CANNON", "Zap Cannon"),
        ("MOVE_FORESIGHT", "Foresight"),
        ("MOVE_DESTINY_BOND", "Destiny Bond"),
        ("MOVE_PERISH_SONG", "Perish Song"),
        ("MOVE_ICY_WIND", "Icy Wind"),
        ("MOVE_DETECT", "Detect"),
        ("MOVE_BONE_RUSH", "Bone Rush"),
        ("MOVE_LOCK_ON", "Lock-On"),
        ("MOVE_OUTRAGE", "Outrage"),
        ("MOVE_SANDSTORM", "Sandstorm"),
        ("MOVE_GIGA_DRAIN", "Giga Drain"),
        ("MOVE_ENDURE", "Endure"),
        ("MOVE_CHARM", "Charm"),
        ("MOVE_ROLLOUT", "Rollout"),
        ("MOVE_FALSE_SWIPE", "False Swipe"),
        ("MOVE_SWAGGER", "Swagger"),
        ("MOVE_MILK_DRINK", "Milk Drink"),
        ("MOVE_SPARK", "Spark"),
        ("MOVE_FURY_CUTTER", "Fury Cutter"),
        ("MOVE_STEEL_WING", "Steel Wing"),
        ("MOVE_MEAN_LOOK", "Mean Look"),
        ("MOVE_ATTRACT", "Attract"),
        ("MOVE_SLEEP_TALK", "Sleep Talk"),
        ("MOVE_HEAL_BELL", "Heal Bell"),
        ("MOVE_RETURN", "Return"),
        ("MOVE_PRESENT", "Present"),
        ("MOVE_FRUSTRATION", "Frustration"),
        ("MOVE_SAFEGUARD", "Safeguard"),
        ("MOVE_PAIN_SPLIT", "Pain Split"),
        ("MOVE_SACRED_FIRE", "Sacred Fire"),
        ("MOVE_MAGNITUDE", "Magnitude"),
        ("MOVE_DYNAMIC_PUNCH", "Dynamicpunch"),
        ("MOVE_MEGAHORN", "Megahorn"),
        ("MOVE_DRAGON_BREATH", "Dragonbreath"),
        ("MOVE_BATON_PASS", "Baton Pass"),
        ("MOVE_ENCORE", "Encore"),
        ("MOVE_PURSUIT", "Pursuit"),
        ("MOVE_RAPID_SPIN", "Rapid Spin"),
        ("MOVE_SWEET_SCENT", "Sweet Scent"),
        ("MOVE_IRON_TAIL", "Iron Tail"),
        ("MOVE_METAL_CLAW", "Metal Claw"),
        ("MOVE_VITAL_THROW", "Vital Throw"),
        ("MOVE_MORNING_SUN", "Morning Sun"),
        ("MOVE_SYNTHESIS", "Synthesis"),
        ("MOVE_MOONLIGHT", "Moonlight"),
        ("MOVE_HIDDEN_POWER", "Hidden Power"),
        ("MOVE_CROSS_CHOP", "Cross Chop"),
        ("MOVE_TWISTER", "Twister"),
        ("MOVE_RAIN_DANCE", "Rain Dance"),
        ("MOVE_SUNNY_DAY", "Sunny Day"),
        ("MOVE_CRUNCH", "Crunch"),
        ("MOVE_MIRROR_COAT", "Mirror Coat"),
        ("MOVE_PSYCH_UP", "Psych Up"),
        ("MOVE_EXTREME_SPEED", "Extremespeed"),
        ("MOVE_ANCIENT_POWER", "Ancientpower"),
        ("MOVE_SHADOW_BALL", "Shadow Ball"),
        ("MOVE_FUTURE_SIGHT", "Future Sight"),
        ("MOVE_ROCK_SMASH", "Rock Smash"),
        ("MOVE_WHIRLPOOL", "Whirlpool"),
        ("MOVE_BEAT_UP", "Beat Up"),
        ("MOVE_FAKE_OUT", "Fake Out"),
        ("MOVE_UPROAR", "Uproar"),
        ("MOVE_STOCKPILE", "Stockpile"),
        ("MOVE_SPIT_UP", "Spit Up"),
        ("MOVE_SWALLOW", "Swallow"),
        ("MOVE_HEAT_WAVE", "Heat Wave"),
        ("MOVE_HAIL", "Hail"),
        ("MOVE_TORMENT", "Torment"),
        ("MOVE_FLATTER", "Flatter"),
        ("MOVE_WILL_O_WISP", "Will-O-Wisp"),
        ("MOVE_MEMENTO", "Memento"),
        ("MOVE_FACADE", "Facade"),
        ("MOVE_FOCUS_PUNCH", "Focus Punch"),
        ("MOVE_SMELLING_SALT", "Smellingsalt"),
        ("MOVE_FOLLOW_ME", "Follow Me"),
        ("MOVE_NATURE_POWER", "Nature Power"),
        ("MOVE_CHARGE", "Charge"),
        ("MOVE_TAUNT", "Taunt"),
        ("MOVE_HELPING_HAND", "Helping Hand"),
        ("MOVE_TRICK", "Trick"),
        ("MOVE_ROLE_PLAY", "Role Play"),
        ("MOVE_WISH", "Wish"),
        ("MOVE_ASSIST", "Assist"),
        ("MOVE_INGRAIN", "Ingrain"),
        ("MOVE_SUPERPOWER", "Superpower"),
        ("MOVE_MAGIC_COAT", "Magic Coat"),
        ("MOVE_RECYCLE", "Recycle"),
        ("MOVE_REVENGE", "Revenge"),
        ("MOVE_BRICK_BREAK", "Brick Break"),
        ("MOVE_YAWN", "Yawn"),
        ("MOVE_KNOCK_OFF", "Knock Off"),
        ("MOVE_ENDEAVOR", "Endeavor"),
        ("MOVE_ERUPTION", "Eruption"),
        ("MOVE_SKILL_SWAP", "Skill Swap"),
        ("MOVE_IMPRISON", "Imprison"),
        ("MOVE_REFRESH", "Refresh"),
        ("MOVE_GRUDGE", "Grudge"),
        ("MOVE_SNATCH", "Snatch"),
        ("MOVE_SECRET_POWER", "Secret Power"),
        ("MOVE_DIVE", "Dive"),
        ("MOVE_ICEBOLT_WAVE", "Icebolt Wave"),
        ("MOVE_CAMOUFLAGE", "Camouflage"),
        ("MOVE_TAIL_GLOW", "Tail Glow"),
        ("MOVE_LUSTER_PURGE", "Luster Purge"),
        ("MOVE_MIST_BALL", "Mist Ball"),
        ("MOVE_FEATHER_DANCE", "Featherdance"),
        ("MOVE_TEETER_DANCE", "Teeter Dance"),
        ("MOVE_BLAZE_KICK", "Blaze Kick"),
        ("MOVE_MUD_SPORT", "Mud Sport"),
        ("MOVE_ICE_BALL", "Ice Ball"),
        ("MOVE_NEEDLE_ARM", "Needle Arm"),
        ("MOVE_SLACK_OFF", "Slack Off"),
        ("MOVE_HYPER_VOICE", "Hyper Voice"),
        ("MOVE_POISON_FANG", "Poison Fang"),
        ("MOVE_CRUSH_CLAW", "Crush Claw"),
        ("MOVE_BLAST_BURN", "Blast Burn"),
        ("MOVE_HYDRO_CANNON", "Hydro Cannon"),
        ("MOVE_METEOR_MASH", "Meteor Mash"),
        ("MOVE_ASTONISH", "Astonish"),
        ("MOVE_WEATHER_BALL", "Weather Ball"),
        ("MOVE_AROMATHERAPY", "Aromatherapy"),
        ("MOVE_FAKE_TEARS", "Fake Tears"),
        ("MOVE_AIR_CUTTER", "Air Cutter"),
        ("MOVE_OVERHEAT", "Overheat"),
        ("MOVE_ODOR_SLEUTH", "Odor Sleuth"),
        ("MOVE_ROCK_TOMB", "Rock Tomb"),
        ("MOVE_SILVER_WIND", "Silver Wind"),
        ("MOVE_METAL_SOUND", "Metal Sound"),
        ("MOVE_GRASS_WHISTLE", "Grasswhistle"),
        ("MOVE_TICKLE", "Tickle"),
        ("MOVE_COSMIC_POWER", "Cosmic Power"),
        ("MOVE_WATER_SPOUT", "Water Spout"),
        ("MOVE_SIGNAL_BEAM", "Signal Beam"),
        ("MOVE_SHADOW_PUNCH", "Shadow Punch"),
        ("MOVE_EXTRASENSORY", "Extrasensory"),
        ("MOVE_SKY_UPPERCUT", "Sky Uppercut"),
        ("MOVE_SAND_TOMB", "Sand Tomb"),
        ("MOVE_SHEER_COLD", "Sheer Cold"),
        ("MOVE_MUDDY_WATER", "Muddy Water"),
        ("MOVE_BULLET_SEED", "Bullet Seed"),
        ("MOVE_AERIAL_ACE", "Aerial Ace"),
        ("MOVE_ICICLE_SPEAR", "Icicle Spear"),
        ("MOVE_IRON_DEFENSE", "Iron Defense"),
        ("MOVE_BLOCK", "Block"),
        ("MOVE_HOWL", "Howl"),
        ("MOVE_DRAGON_CLAW", "Dragon Claw"),
        ("MOVE_FRENZY_PLANT", "Frenzy Plant"),
        ("MOVE_BULK_UP", "Bulk Up"),
        ("MOVE_BOUNCE", "Bounce"),
        ("MOVE_MUD_SHOT", "Mud Shot"),
        ("MOVE_POISON_TAIL", "Poison Tail"),
        ("MOVE_COVET", "Covet"),
        ("MOVE_VOLT_TACKLE", "Volt Tackle"),
        ("MOVE_MAGICAL_LEAF", "Magical Leaf"),
        ("MOVE_WATER_SPORT", "Water Sport"),
        ("MOVE_CALM_MIND", "Calm Mind"),
        ("MOVE_LEAF_BLADE", "Leaf Blade"),
        ("MOVE_DRAGON_DANCE", "Dragon Dance"),
        ("MOVE_ROCK_BLAST", "Rock Blast"),
        ("MOVE_SHOCK_WAVE", "Shock Wave"),
        ("MOVE_WATER_PULSE", "Water Pulse"),
        ("MOVE_DOOM_DESIRE", "Doom Desire"),
        ("MOVE_PSYCHO_BOOST", "Psycho Boost"),
        ("MOVE_GRAND_BOULDER", "Grand Boulder"),
        ("MOVE_SOUL_BREAK", "Soul Break"),
        ("MOVE_STARDUST", "Stardust"),
        ("MOVE_RAZE_EARTH", "Raze Earth"),
        ("MOVE_POSSESS", "Possess"),
        ("MOVE_DEVASTATE", "Devastate"),
        ("MOVE_METAL_BLAST", "Metal Blast"),
        ("MOVE_HAMMER_ARM", "Hammer Arm"),
        ("MOVE_CLOSE_COMBAT", "Close Combat"),
        ("MOVE_FLARE_BLITZ", "Flare Blitz"),
        ("MOVE_FORCE_PALM", "Force Palm"),
        ("MOVE_AURA_SPHERE", "Aura Sphere"),
        ("MOVE_ROCK_POLISH", "Rock Polish"),
        ("MOVE_POISON_JAB", "Poison Jab"),
        ("MOVE_DARK_PULSE", "Dark Pulse"),
        ("MOVE_NIGHT_SLASH", "Night Slash"),
        ("MOVE_AQUA_TAIL", "Aqua Tail"),
        ("MOVE_SEED_BOMB", "Seed Bomb"),
        ("MOVE_AIR_SLASH", "Air Slash"),
        ("MOVE_X_SCISSOR", "X-Scissor"),
        ("MOVE_BUG_BUZZ", "Bug Buzz"),
        ("MOVE_DRAGON_PULSE", "Dragon Pulse"),
        ("MOVE_DRAGON_RUSH", "Dragon Rush"),
        ("MOVE_POWER_GEM", "Power Gem"),
        ("MOVE_DRAIN_PUNCH", "Drain Punch"),
        ("MOVE_VACUUM_WAVE", "Vacuum Wave"),
        ("MOVE_FOCUS_BLAST", "Focus Blast"),
        ("MOVE_ENERGY_BALL", "Energy Ball"),
        ("MOVE_BRAVE_BIRD", "Brave Bird"),
        ("MOVE_EARTH_POWER", "Earth Power"),
        ("MOVE_SWITCHEROO", "Switcheroo"),
        ("MOVE_GIGA_IMPACT", "Giga Impact"),
        ("MOVE_NASTY_PLOT", "Nasty Plot"),
        ("MOVE_BULLET_PUNCH", "Bullet Punch"),
        ("MOVE_AVALANCHE", "Avalanche"),
        ("MOVE_ICE_SHARD", "Ice Shard"),
        ("MOVE_SHADOW_CLAW", "Shadow Claw"),
        ("MOVE_SHADOW_SNEAK", "Shadow Sneak"),
        ("MOVE_MUD_BOMB", "Mud Bomb"),
        ("MOVE_PSYCHO_CUT", "Psycho Cut"),
        ("MOVE_ZEN_HEADBUTT", "Zen Headbutt"),
        ("MOVE_MIRROR_SHOT", "Mirror Shot"),
        ("MOVE_FLASH_CANNON", "Flash Cannon"),
        ("MOVE_ROCK_CLIMB", "Rock Climb"),
        ("MOVE_DRACO_METEOR", "Draco Meteor"),
        ("MOVE_DISCHARGE", "Discharge"),
        ("MOVE_LEAF_STORM", "Leaf Storm"),
        ("MOVE_POWER_WHIP", "Power Whip"),
        ("MOVE_ROCK_WRECKER", "Rock Wrecker"),
        ("MOVE_GUNK_SHOT", "Gunk Shot"),
        ("MOVE_IRON_HEAD", "Iron Head"),
        ("MOVE_MAGNET_BOMB", "Magnet Bomb"),
        ("MOVE_STONE_EDGE", "Stone Edge"),
        ("MOVE_GRASS_KNOT", "Grass Knot"),
        ("MOVE_CHARGE_BEAM", "Charge Beam"),
        ("MOVE_WOOD_HAMMER", "Wood Hammer"),
        ("MOVE_AQUA_JET", "Aqua Jet"),
        ("MOVE_ATTACK_ORDER", "Attack Order"),
        ("MOVE_DEFEND_ORDER", "Defend Order"),
        ("MOVE_HEAL_ORDER", "Heal Order"),
        ("MOVE_DOUBLE_HIT", "Double Hit"),
        ("MOVE_ROAR_OF_TIME", "Roar Of Time"),
        ("MOVE_SPACIAL_REND", "Spacial Rend"),
        ("MOVE_MAGMA_RUSH", "Magma Rush"),
        ("MOVE_DARK_VOID", "Dark Void"),
        ("MOVE_OMINOUS_WIND", "Ominous Wind"),
        ("MOVE_CROSS_POISON", "Cross Poison"),
        ("MOVE_THUNDER_FANG", "Thunder Fang"),
        ("MOVE_ICE_FANG", "Ice Fang"),
        ("MOVE_FIRE_FANG", "Fire Fang"),
        ("MOVE_CRASH_IMPACT", "Crash Impact"),
        ("MOVE_SPIN_TAIL", "Spin Tail"),
        ("MOVE_DOUBLE_SPIN", "Double Spin"),
        ("MOVE_TONE_DEAF", "Tone-Deaf"),
        ("MOVE_DIZZY_WHIRL", "Dizzy Whirl"),
        ("MOVE_DEEP_YAWN", "Deep Yawn"),
        ("MOVE_RAGING_FLAME", "Raging Flame"),
        ("MOVE_MAGMA_RING", "Magma Ring"),
        ("MOVE_WAVE_SPLASH", "Wave Splash"),
        ("MOVE_DELUGE", "Deluge"),
        ("MOVE_AQUA_BOLT", "Aqua Bolt"),
        ("MOVE_GIGA_SPARK", "Giga Spark"),
        ("MOVE_SHINE_BOMB", "Shine Bomb"),
        ("MOVE_MEGASHOCK", "Megashock"),
        ("MOVE_MACH_BOLT", "Mach Bolt"),
        ("MOVE_ENERGIZE", "Energize"),
        ("MOVE_WILD_GROWTH", "Wild Growth"),
        ("MOVE_GUARDIAN_LEAF", "Guardian Leaf"),
        ("MOVE_POISON_LEAF", "Poison Leaf"),
        ("MOVE_RAPID_GROWTH", "Rapid Growth"),
        ("MOVE_DAZZLE_POWDER", "Dazzle Powder"),
        ("MOVE_STARFREEZE", "Starfreeze"),
        ("MOVE_ICICLE_PUNCH", "Icicle Punch"),
        ("MOVE_FROSTBITE", "Frostbite"),
        ("MOVE_ICY_KISS", "Icy Kiss"),
        ("MOVE_MAGNUM_PUNCH", "Magnum Punch"),
        ("MOVE_DOUBLE_SHOT", "Double Shot"),
        ("MOVE_TOXIN_SPRAY", "Toxin Spray"),
        ("MOVE_SMOGSCREEN", "Smogscreen"),
        ("MOVE_BURROW", "Burrow"),
        ("MOVE_SONIC_SAND", "Sonic Sand"),
        ("MOVE_SANDBLAST", "Sandblast"),
        ("MOVE_GLIDE", "Glide"),
        ("MOVE_TYPHOON", "Typhoon"),
        ("MOVE_PSYGATLING", "Psygatling"),
        ("MOVE_PSYCHO_PUNCH", "Psycho Punch"),
        ("MOVE_PSYBURN", "Psyburn"),
        ("MOVE_LATENT_POWER", "Latent Power"),
        ("MOVE_HYPNOPULSE", "Hypnopulse"),
        ("MOVE_GRAVITY_WAVE", "Gravity Wave"),
        ("MOVE_BUG_NOISE", "Bug Noise"),
        ("MOVE_ANGRY_SWARM", "Angry Swarm"),
        ("MOVE_ROCK_TUMBLE", "Rock Tumble"),
        ("MOVE_DIAMOND_BLAST", "Diamond Blast"),
        ("MOVE_PALEOBREATH", "Paleobreath"),
        ("MOVE_SHADOW_CLAMP", "Shadow Clamp"),
        ("MOVE_CURSED_WRATH", "Cursed Wrath"),
        ("MOVE_LIFE_DRAIN", "Life Drain"),
        ("MOVE_DRAGON_BEAT", "Dragon Beat"),
        ("MOVE_VENGEANCE", "Vengeance"),
        ("MOVE_DARK_RESOLVE", "Dark Resolve"),
        ("MOVE_DARK_CUTTER", "Dark Cutter"),
        ("MOVE_DARK_ROAR", "Dark Roar"),
        ("MOVE_DARK_HAND", "Dark Hand"),
        ("MOVE_CORNER", "Corner"),
        ("MOVE_METAL_PINCER", "Metal Pincer"),
        ("MOVE_GEO_IMPACT", "Geo Impact"),
        ("MOVE_MAGNET_FORCE", "Magnet Force"),
        ("MOVE_ROOST", "Roost"),
        ("MOVE_DEFOG", "Defog"),
        ("MOVE_LAVA_PLUME", "Lava Plume"),
        ("MOVE_NOVA_INFERNO", "Nova Inferno"),
        ("MOVE_RAID", "Raid"),
        ("MOVE_ACID_SPRAY", "Acid Spray"),
        ("MOVE_ELECTROWEB", "Electroweb"),
        ("MOVE_SHELL_SMASH", "Shell Smash"),
        ("MOVE_GEAR_GRIND", "Gear Grind"),
        ("MOVE_SHIFT_GEAR", "Shift Gear"),
        ("MOVE_LEAF_TORNADO", "Leaf Tornado"),
        ("MOVE_RAZOR_SHELL", "Razor Shell"),
        ("MOVE_BULLDOZE", "Bulldoze"),
        ("MOVE_DUAL_CHOP", "Dual Chop"),
        ("MOVE_QUIVER_DANCE", "Quiver Dance"),
        ("MOVE_HONE_CLAWS", "Hone Claws"),
        ("MOVE_ICICLE_CRASH", "Icicle Crash"),
        ("MOVE_COIL", "Coil"),
        ("MOVE_DRILL_RUN", "Drill Run"),
        ("MOVE_HEART_STAMP", "Heart Stamp"),
        ("MOVE_STEAMROLLER", "Steamroller"),
        ("MOVE_WORK_UP", "Work Up"),
        ("MOVE_SLUDGE_WAVE", "Sludge Wave"),
        ("MOVE_STRUGGLE_BUG", "Struggle Bug"),
        ("MOVE_INFERNO", "Inferno"),
        ("MOVE_WILD_CHARGE", "Wild Charge"),
        ("MOVE_SHARPSHOOT", "Sharpshoot"),
        ("MOVE_SCALD", "Scald")
    ]}


data = PokemonVegaData()
_init()

LEGENDARY_POKEMON = frozenset([data.constants[species] for species in [
    "SPECIES_ARTICUNO",
    "SPECIES_ZAPDOS",
    "SPECIES_MOLTRES",
    "SPECIES_RAIKOU",
    "SPECIES_ENTEI",
    "SPECIES_SUICUNE",
    "SPECIES_LYLAPSE",
    "SPECIES_GANIMEDE",
    "SPECIES_NEMEA",
    "SPECIES_DIALGA",
    "SPECIES_PALKIA",
    "SPECIES_DARKRAI",
    "SPECIES_LUGIA",
    "SPECIES_HO_OH",
    "SPECIES_MEWTWO",
    "SPECIES_MEW",
    "SPECIES_ROYTSAR",
    "SPECIES_GATANOIA",
    "SPECIES_LUKEWRAN",
    "SPECIES_HEATRAN",
    "SPECIES_LATIAS",
    "SPECIES_LATIOS",
    "SPECIES_PHIONE",
    "SPECIES_MANAPHY",
    "SPECIES_ALDINA",
    "SPECIES_ALMARIA",
    "SPECIES_ASPHERE"
]])

NATIONAL_ID_TO_SPECIES_ID = {species.national_dex_number: i for i, species in data.species.items()}
