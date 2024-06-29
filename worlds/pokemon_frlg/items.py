from typing import Dict, FrozenSet, Optional
from BaseClasses import Item, ItemClassification
from .data import data


class PokemonFRLGItem(Item):
    game: str = "Pokemon FireRed and LeafGreen",
    tags: FrozenSet[str]

    def __init__(self, name: str, classification: ItemClassification, code: Optional[int], player: int) -> None:
        super().__init__(name, classification, code, player)

        if code is None:
            self.tags = frozenset(["Event"])
        else:
            self.tags = data.items[code].tags


def create_item_name_to_id_map() -> Dict[str, int]:
    """
    Creates a map from item names to their AP item ID (code)
    """
    name_to_id_map: Dict[str, int] = {}
    for item_id, attributes in data.items.items():
        name_to_id_map[attributes.name] = item_id

    return name_to_id_map


def get_item_classification(item_id: int) -> ItemClassification:
    """
    Returns the item classification for a given AP item id (code)
    """
    return data.items[item_id].classification
