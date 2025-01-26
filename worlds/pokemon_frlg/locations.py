import copy
from typing import TYPE_CHECKING, Dict, FrozenSet, Iterable, List, Optional, Union
from BaseClasses import CollectionState, Location, Region, ItemClassification
from .data import data, BASE_OFFSET
from .items import get_random_item, offset_item_value, reverse_offset_item_value, PokemonVegaItem
from .options import FreeFlyLocation, TownMapFlyLocation

if TYPE_CHECKING:
    from . import PokemonVegaWorld

LOCATION_GROUPS = {
    "Badges": {
        "Junopsis Gym - Prize",
        "Seafin Gym - Prize",
        "Gamboge Gym - Prize",
        "Nephrite Gym - Prize",
        "Orpimence Gym - Prize",
        "Ravenplume Gym - Prize",
        "Lapizula Gym - Prize",
        "New Island Gym - Prize"
    },
    "Gym TMs": {
        "Junopsis Gym - Annette TM",
        "Seafin Gym - Geoff TM",
        "Gamboge Gym - Brooke TM",
        "Nephrite Gym - Avery TM",
        "Orpimence Gym - Chie and Rito TM",
        "Ravenplume Gym - Fenton TM",
        "Lapizula Gym - Tara TM",
        "New Island Gym - Mewtwo TM"
    }
}

FLY_ITEM_ID_MAP = {
    "ITEM_FLY_NONE": 0,
    "ITEM_FLY_PORCELIA": 1,
    "ITEM_FLY_JUNOPSIS": 2,
    "ITEM_FLY_SEAFIN": 3,
    "ITEM_FLY_GAMBOGE": 4,
    "ITEM_FLY_SHAMOUTI": 5,
    "ITEM_FLY_NEPHRITE": 6,
    "ITEM_FLY_ORPIMENCE": 7,
    "ITEM_FLY_LAPIZULA": 8,
    "ITEM_FLY_NEW_ISLAND": 9,
    "ITEM_FLY_SHAKUDO": 10,
    "ITEM_FLY_RAVENPLUME": 11,
    "ITEM_FLY_ROUTE510": 20
}

fly_item_exclusion_map = {
    "Porcelia Town": "ITEM_FLY_PORCELIA",
    "Junopsis City": "ITEM_FLY_JUNOPSIS",
    "Seafin City": "ITEM_FLY_SEAFIN",
    "Gamboge City": "ITEM_FLY_GAMBOGE",
    "Shamouti Island": "ITEM_FLY_SHAMOUTI",
    "Nephrite City": "ITEM_FLY_NEPHRITE",
    "Orpimence City": "ITEM_FLY_ORPIMENCE",
    "Lapizula City": "ITEM_FLY_LAPIZULA",
    "New Island": "ITEM_FLY_NEW_ISLAND",
    "Shakudo Island": "ITEM_FLY_SHAKUDO",
    "Ravenplume City": "ITEM_FLY_RAVENPLUME",
    "Route 510": "ITEM_FLY_ROUTE510"
}


class PokemonVegaLocation(Location):
    game: str = "Pokemon Vega"
    item_address = Optional[Dict[str, int]]
    default_item_id: Optional[int]
    tags: FrozenSet[str]
    data_ids: Optional[List[str]]
    spoiler_name: str

    def __init__(
            self,
            player: int,
            name: str,
            address: Optional[int],
            parent: Optional[Region] = None,
            item_address: Optional[Dict[str, Union[int, List[int]]]] = None,
            default_item_id: Optional[int] = None,
            tags: FrozenSet[str] = frozenset(),
            data_ids: Optional[List[str]] = None,
            spoiler_name: Optional[str] = None) -> None:
        super().__init__(player, name, address, parent)
        self.default_item_id = None if default_item_id is None else offset_item_value(default_item_id)
        self.item_address = item_address
        self.tags = tags
        self.data_ids = data_ids
        self.spoiler_name = spoiler_name if spoiler_name is not None else name

def offset_flag(flag: int) -> int:
    if flag is None:
        return None
    return flag + BASE_OFFSET


def reverse_offset_flag(location_id: int) -> int:
    if location_id is None:
        return None
    return location_id - BASE_OFFSET


def create_location_name_to_id_map() -> Dict[str, int]:
    """
    Creates a map from location names to their AP location ID (address)
    """
    name_to_id_mapping: Dict[str, int] = {}
    for region_data in data.regions.values():
        for location_id in region_data.locations:
            location_data = data.locations[location_id]
            name_to_id_mapping[location_data.name] = offset_flag(location_data.flag)

    return name_to_id_mapping


def create_locations_from_tags(world: "PokemonVegaWorld", regions: Dict[str, Region], tags: Iterable[str]) -> None:
    """
    Iterates through region data and adds locations to the multiworld if
    those locations include any of the provided tags.
    """
    tags = set(tags)

    for region_data in data.regions.values():
        if world.options.exclude_sphere_ruins and region_data.sphere_ruins:
            continue

        region = regions[region_data.name]
        included_locations = [loc for loc in region_data.locations
                              if len(tags & data.locations[loc].tags) >= len(data.locations[loc].tags)]

        for location_flag in included_locations:
            location_data = data.locations[location_flag]

            location_id = offset_flag(location_data.flag)

            if location_data.default_item == data.constants["ITEM_NONE"]:
                default_item = reverse_offset_item_value(
                    world.item_name_to_id[get_random_item(world, ItemClassification.filler)]
                )
            else:
                default_item = location_data.default_item

            location = PokemonVegaLocation(
                world.player,
                location_data.name,
                location_id,
                region,
                location_data.address,
                default_item,
                location_data.tags
            )
            region.locations.append(location)


def set_free_fly(world: "PokemonVegaWorld") -> None:
    # Set our free fly location
    world.free_fly_location_id = FLY_ITEM_ID_MAP["ITEM_FLY_NONE"]
    world.town_map_fly_location_id = FLY_ITEM_ID_MAP["ITEM_FLY_NONE"]

    if (world.options.free_fly_location == FreeFlyLocation.option_off and
            world.options.town_map_fly_location == TownMapFlyLocation.option_off):
        return

    state = CollectionState(world.multiworld)
    regions = world.multiworld.get_regions(world.player)
    locations = world.multiworld.get_locations(world.player)
    free_fly_list: List[str] = [
        "ITEM_FLY_PORCELIA",
        "ITEM_FLY_JUNOPSIS",
        "ITEM_FLY_SEAFIN",
        "ITEM_FLY_GAMBOGE",
        "ITEM_FLY_SHAMOUTI",
        "ITEM_FLY_NEPHRITE",
        "ITEM_FLY_ORPIMENCE",
        "ITEM_FLY_LAPIZULA",
        "ITEM_FLY_NEW_ISLAND",
        "ITEM_FLY_RAVENPLUME",
        "ITEM_FLY_ROUTE510",
    ]

    found_event = True
    collected_events = set()
    while found_event:
        found_event = False
        for location in locations:
            if state.can_reach(location) and location.is_event and location not in collected_events:
                state.collect(location.item, True, location)
                collected_events.add(location)
                found_event = True

    reachable_regions = set()
    for region in regions:
        if region.can_reach(state):
            reachable_regions.add(region.name)

    town_map_fly_list = copy.deepcopy(free_fly_list)

    if world.options.free_fly_location == FreeFlyLocation.option_any:
        free_fly_list.append("ITEM_FLY_SHAKUDO")

    if world.options.town_map_fly_location == TownMapFlyLocation.option_any:
        town_map_fly_list.append("ITEM_FLY_SHAKUDO")

    for region in reachable_regions:
        if region in fly_item_exclusion_map.keys():
            fly_to_remove = fly_item_exclusion_map[region]
            if fly_to_remove in free_fly_list:
                free_fly_list.remove(fly_to_remove)
            if fly_to_remove in town_map_fly_list:
                town_map_fly_list.remove(fly_to_remove)

    if world.options.free_fly_location != FreeFlyLocation.option_off:
        free_fly_location_id = world.random.choice(free_fly_list)
        world.free_fly_location_id = FLY_ITEM_ID_MAP[free_fly_location_id]

        if free_fly_location_id in town_map_fly_list:
            town_map_fly_list.remove(free_fly_location_id)

        menu_region = world.multiworld.get_region("Menu", world.player)
        free_fly_location = PokemonVegaLocation(
            world.player,
            "Free Fly Location",
            None,
            menu_region,
            None,
            None,
            frozenset({"Event"})
        )
        item_id = data.constants[free_fly_location_id]
        free_fly_location.place_locked_item(PokemonVegaItem(data.items[item_id].name,
                                                            ItemClassification.progression,
                                                            None,
                                                            world.player))
        free_fly_location.show_in_spoiler = False
        menu_region.locations.append(free_fly_location)

    if world.options.town_map_fly_location != TownMapFlyLocation.option_off:
        town_map_fly_location_id = world.random.choice(town_map_fly_list)
        world.town_map_fly_location_id = FLY_ITEM_ID_MAP[town_map_fly_location_id]

        menu_region = world.multiworld.get_region("Menu", world.player)
        town_map_fly_location = PokemonVegaLocation(
            world.player,
            "Town Map Fly Location",
            None,
            menu_region,
            None,
            None,
            frozenset({"Event"})
        )
        item_id = data.constants[town_map_fly_location_id]
        town_map_fly_location.place_locked_item(PokemonVegaItem(data.items[item_id].name,
                                                                 ItemClassification.progression,
                                                                 None,
                                                                 world.player))
        town_map_fly_location.access_rule = lambda state: state.has("Town Map", world.player)
        town_map_fly_location.show_in_spoiler = False
        menu_region.locations.append(town_map_fly_location)
