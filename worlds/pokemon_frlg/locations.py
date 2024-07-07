from typing import TYPE_CHECKING, Dict, Optional, FrozenSet, Iterable, List
from BaseClasses import Location, Region, ItemClassification
from .data import data, BASE_OFFSET
from .items import offset_item_value, PokemonFRLGItem
from .options import ViridianCityRoadblock, PewterCityRoadblock
if TYPE_CHECKING:
    from . import PokemonFRLGWorld


LOCATION_GROUPS = {
    "Badges": {
        "Pewter Gym - Leader Brock Prize",
        "Cerulean Gym - Leader Misty Prize",
        "Vermilion Gym - Leader Lt. Surge Prize",
        "Celadon Gym - Leader Erika Prize",
        "Fuchsia Gym - Leader Koga Prize",
        "Saffron Gym - Leader Sabrina Prize",
        "Cinnabar Gym - Leader Blaine Prize",
        "Viridian Gym - Leader Giovanni Prize"
    },
    "Oak's Aides": {
        "Route 2 East Building - Professor Oak's Aide",
        "Route 10 Pokemon Center 1F - Professor Oak's Aide",
        "Route 11 East Entrance 2F - Professor Oak's Aide",
        "Route 16 North Entrance 2F - Professor Oak's Aide",
        "Route 15 West Entrance 2F - Professor Oak's Aide"
    }
}


FLY_EVENT_NAME_TO_ID = {
    "EVENT_FLY_PALLET_TOWN": 0,
    "EVENT_FLY_VIRIDIAN_CITY": 1,
    "EVENT_FLY_PEWTER_CITY": 2,
    "EVENT_FLY_CERULEAN_CITY": 3,
    "EVENT_FLY_VERMILION_CITY": 4,
    "EVENT_FLY_LAVENDER_TOWN": 5,
    "EVENT_FLY_CELADON_CITY": 6,
    "EVENT_FLY_FUCHSIA_CITY": 7,
    "EVENT_FLY_SAFFRON_CITY": 8,
    "EVENT_FLY_CINNABAR_ISLAND": 9,
    "EVENT_FLY_ONE_ISLAND": 10,
    "EVENT_FLY_TWO_ISLAND": 11,
    "EVENT_FLY_THREE_ISLAND": 12,
    "EVENT_FLY_FOUR_ISLAND": 13,
    "EVENT_FLY_FIVE_ISLAND": 14,
    "EVENT_FLY_SIX_ISLAND": 15,
    "EVENT_FLY_SEVEN_ISLAND": 16
}


class PokemonFRLGLocation(Location):
    game: str = "Pokemon FireRed and LeafGreen"
    item_address = Optional[Dict[str, int]]
    default_item_id: Optional[int]
    tags: FrozenSet[str]

    def __init__(
            self,
            player: int,
            name: str,
            address: Optional[int],
            parent: Optional[Region] = None,
            item_address: Optional[Dict[str, int]] = None,
            default_item_id: Optional[int] = None,
            tags: FrozenSet[str] = frozenset()) -> None:
        super().__init__(player, name, address, parent)
        self.default_item_id = None if default_item_id is None else offset_item_value(default_item_id)
        self.item_address = item_address
        self.tags = tags


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


def create_locations_from_tags(world: "PokemonFRLGWorld", regions: Dict[str, Region], tags: Iterable[str]) -> None:
    """
    Iterates through region data and adds locations to the multiworld if
    those locations include any of the provided tags.
    """
    game_version = world.options.game_version.current_key

    tags = set(tags)

    for region_data in data.regions.values():
        region = regions[region_data.name]
        included_locations = [loc for loc in region_data.locations if len(tags & data.locations[loc].tags) > 0]

        for location_flag in included_locations:
            location_data = data.locations[location_flag]

            location_id = offset_flag(location_data.flag)
            item_addresses: Dict[str, int] = {f'{game_version}': location_data.address[game_version],
                                              f'{game_version}_rev1': location_data.address[f'{game_version}_rev1']}
            location = PokemonFRLGLocation(
                world.player,
                location_data.name,
                location_id,
                region,
                item_addresses,
                location_data.default_item,
                location_data.tags
            )
            region.locations.append(location)


def set_free_fly(world: "PokemonFRLGWorld") -> None:
    # Set our free fly location
    free_fly_location_id = "EVENT_FLY_PALLET_TOWN"
    if world.options.free_fly_location:
        free_fly_list: List[str] = [
            "EVENT_FLY_LAVENDER_TOWN",
            "EVENT_FLY_CELADON_CITY",
            "EVENT_FLY_FUCHSIA_CITY",
            "EVENT_FLY_SAFFRON_CITY",
            "EVENT_FLY_CINNABAR_ISLAND",
            "EVENT_FLY_ONE_ISLAND",
            "EVENT_FLY_TWO_ISLAND",
            "EVENT_FLY_THREE_ISLAND",
            "EVENT_FLY_FOUR_ISLAND",
            "EVENT_FLY_FIVE_ISLAND",
            "EVENT_FLY_SIX_ISLAND",
            "EVENT_FLY_SEVEN_ISLAND"
        ]

        if world.options.viridian_city_roadblock == ViridianCityRoadblock.option_vanilla:
            free_fly_list.append("EVENT_FLY_PEWTER_CITY")
        if world.options.pewter_city_roadblock != PewterCityRoadblock.option_open:
            free_fly_list.append("EVENT_FLY_CERULEAN_CITY")
            free_fly_list.append("EVENT_FLY_VERMILION_CITY")

        free_fly_location_id = world.random.choice(free_fly_list)

    world.free_fly_location_id = FLY_EVENT_NAME_TO_ID[free_fly_location_id]

    free_fly_location = world.multiworld.get_location("Free Fly Location", world.player)
    free_fly_location.item = None
    free_fly_location.place_locked_item(PokemonFRLGItem(
        data.events[free_fly_location_id].item,
        ItemClassification.progression,
        None,
        world.player
    ))
