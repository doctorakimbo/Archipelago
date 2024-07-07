"""
Option definitions for Pokemon FireRed/LeafGreen
"""
from dataclasses import dataclass
from Options import Choice, DeathLink, Range, Toggle, PerGameCommonOptions


class GameVersion(Choice):
    """
    Select FireRed or LeafGreen version.
    """
    display_name = "Game Version"
    option_firered = 0
    option_leafgreen = 1
    default = "random"


class GameRevision(Choice):
    """
    Select FireRed or LeafGreen revision.
    """
    display_name = "Game Revision"
    default = 0
    option_rev0 = 0
    option_rev1 = 1


class ShuffleBadges(Toggle):
    """
    Shuffle Gym Badges into the general item pool. If turned off, Badges will be shuffled among themselves.
    """
    display_name = "Shuffle Badges"
    default = 1


class ShuffleHiddenItems(Choice):
    """
    Shuffle Hidden Items into the general item pool.

    - Off: Hidden Items are not shuffled.
    - Nonrecurring: Nonrecurring Hidden Items are shuffled.
    - All: All Hidden Items are shuffled. Recurring Hidden Items will always appear and will not regenerate.
    """
    display_name = "Shuffle Hidden Items"
    default = 0
    option_off = 0
    option_nonrecurring = 1
    option_all = 2


class ItemfinderRequired(Choice):
    """
    Sets whether the Itemfinder if required for Hidden Items. Some items cannot be picked up without using the
    Itemfinder regardless of this setting (e.g. the Leftovers under Snorlax on Route 12 & 16).

    - Off: The Itemfinder is not required to pickup Hidden Items.
    - Logic: The Itemfinder is logically required to pickup Hidden Items.
    - Required: The Itemfinder is required to pickup Hidden Items.
    """
    display_name = "Itemfinder Required"
    default = 1
    option_off = 0
    option_logic = 1
    option_required = 2


class FlashRequired(Toggle):
    """
    Sets whether HM05 Flash is logically required to navigate Rock Tunnel.
    """
    display_name = "Flash Required"
    default = 1


class OaksAideRoute2(Range):
    """
    Sets the number of Pokemon that need to be registered in the Pokedex to receive the item from Professor Oak's Aide
    on Route 2. Vanilla is 10.
    """
    display_name = "Oak's Aide Route 2"
    default = 5
    range_start = 0
    range_end = 50


class OaksAideRoute10(Range):
    """
    Sets the number of Pokemon that need to be registered in the Pokedex to receive the item from Professor Oak's Aide
    on Route 10. Vanilla is 20.
    """
    display_name = "Oak's Aide Route 10"
    default = 10
    range_start = 0
    range_end = 50


class OaksAideRoute11(Range):
    """
    Sets the number of Pokemon that need to be registered in the Pokedex to receive the item from Professor Oak's Aide
    on Route 11. Vanilla is 30.
    """
    display_name = "Oak's Aide Route 11"
    default = 15
    range_start = 0
    range_end = 50


class OaksAideRoute16(Range):
    """
    Sets the number of Pokemon that need to be registered in the Pokedex to receive the item from Professor Oak's Aide
    on Route 16. Vanilla is 40.
    """
    display_name = "Oak's Aide Route 16"
    default = 20
    range_start = 0
    range_end = 50


class OaksAideRoute15(Range):
    """
    Sets the number of Pokemon that need to be registered in the Pokedex to receive the item from Professor Oak's Aide
    on Route 15. Vanilla is 50.
    """
    display_name = "Oak's Aide Route 15"
    default = 25
    range_start = 0
    range_end = 50


class ViridianCityRoadblock(Choice):
    """
    Sets the requirement for passing the Viridian City Roadblock.
    
    - Vanilla: The Old Man moves out of the way after delivering Oak's Parcel.
    - Early Parcel: Same as Vanilla but Oak's Parcel will be available at the beginning of your game.
    - Open: The Old Man is moved out of the way at the start of the game.
    """
    display_name = "Viridian City Roadblock"
    default = 1
    option_vanilla = 0
    option_early_parcel = 1
    option_open = 2


class PewterCityRoadblock(Choice):
    """
    Sets the requirement for passing the Pewter City Roadblock.

    - Open: The boy will not stop you from entering Route 3.
    - Brock: The boy will stop you from entering Route 3 until you defeat Brock.
    - Any Gym Leader: The boy will stop you from entering Route 3 until you defeat any Gym Leader.
    - Boulder Badge: The boy will stop you from entering Route 3 until you have the Boulder Badge.
    - Any Badge: The boy will stop you from entering Route 3 until you have a Badge.
    """
    display_name = "Pewter City Roadblock"
    default = 1
    option_open = 0
    option_brock = 1
    option_any_gym = 2
    option_boulder_badge = 3
    option_any_badge = 4


class CeruleanCityRoadblocks(Toggle):
    """
    Sets whether the Policeman and Slowpoke are blocking the exits of the city until you save Bill.
    """
    display_name = "Cerulean City Roadblocks"
    default = 1


class ViridianGymRequirement(Choice):
    """
    Sets the requirement for opening the Viridian Gym.

    - Badges: Obtain some number of Badges.
    - Gyms: Beat some number of Gyms.
    """
    display_name = "Viridian Gym Requirement"
    default = 0
    option_badges = 0
    option_gyms = 1


class ViridianGymCount(Range):
    """
    Sets the number of Badges/Gyms required to open the Viridian Gym.
    """
    display_name = "Viridian Gym Count"
    default = 7
    range_start = 0
    range_end = 7


class Route22GateRequirement(Choice):
    """
    Sets the requirement for passing through the Route 22 Gate.

    - Badges: Obtain some number of Badges.
    - Gyms: Beat some number of Gyms.
    """
    display_name = "Route 22 Gate Requirement"
    default = 0
    option_badges = 0
    option_gyms = 1


class Route22GateCount(Range):
    """
    Sets the number of Badges/Gyms required to pass through the Route 22 Gate.
    """
    display_name = "Route 22 Gate Count"
    default = 7
    range_start = 0
    range_end = 8


class Route23GuardRequirement(Choice):
    """
    Sets the requirement for passing the Route 23 Guard.

    - Badges: Obtain some number of Badges.
    - Gyms: Beat some number of Gyms.
    """
    display_name = "Route 23 Guard Requirement"
    default = 0
    option_badges = 0
    option_gyms = 1


class Route23GuardCount(Range):
    """
    Sets the number of Badges/Gyms required to pass the Route 23 Guard.
    """
    display_name = "Route 23 Guard Count"
    default = 7
    range_start = 0
    range_end = 8


class EliteFourRequirement(Choice):
    """
    Sets the requirement for challenging the Elite Four.

    - Badges: Obtain some number of Badges.
    - Gyms: Beat some number of Gyms.
    """
    display_name = "Elite Four Requirement"
    default = 0
    option_badges = 0
    option_gyms = 1


class EliteFourCount(Range):
    """
    Sets the number of Badges/Gyms required to challenge the Elite Four.
    """
    display_name = "Elite Four Count"
    default = 8
    range_start = 0
    range_end = 8


class CeruleanCaveRequirement(Choice):
    """
    Sets the requirement for being able to enter Cerulean Cave.

    - Vanilla: Become the Champion and restore the Network Machine on the Sevii Islands.
    - Champion: Become the Champion.
    - Network Machine: Restore the Network Machine on the Sevii Islands.
    - Badges: Obtain some number of Badges.
    - Gyms: Beat some number of Gyms.
    """
    display_name = "Cerulean Cave Requirement"
    default = 0
    option_vanilla = 0
    option_champion = 1
    option_restore_network = 2
    option_badges = 3
    option_gyms = 4


class CeruleanCaveCount(Range):
    """
    Sets the number of Badges/Gyms required to enter Cerulean Cave. This setting only matters if the Cerulean Cave
    Requirement is set to either Badges or Gyms.
    """
    display_name = "Cerulean Cave Count"
    default = 8
    range_start = 0
    range_end = 8


class ReusableTmsTutors(Toggle):
    """
    Sets TMs to not break after use (they remain sellable). Allows Move Tutors to be used infinitely.
    """
    display_name = "Reusable TMs/Move Tutors"


class MinCatchRate(Range):
    """
    Sets the minimum catch rate a Pokemon can have. It will raise any Pokemon's catch rate to this value if its normal
    catch rate is lower than the chosen value.
    """
    display_name = "Minimum Catch Rate"
    range_start = 3
    range_end = 255
    default = 3


class GuaranteedCatch(Toggle):
    """
    Pokeballs are guaranteed to catch wild Pokemon regardless of catch rate.
    """
    display_name = "Guarenteed Catch"


class ExpModifier(Range):
    """
    Multiplies gained EXP by a percentage.

    100 is default
    50 is half
    200 is double
    etc.
    """
    display_name = "Exp Modifier"
    range_start = 1
    range_end = 1000
    default = 100


class BlindTrainers(Toggle):
    """
    Trainers will not start a battle with you unless you talk to them.
    """
    display_name = "Blind Trainers"


class BetterShops(Toggle):
    """
    Most Pokemarts will sell all normal Pokemart items. The exceptions are the following:

    - Celadon Department Store 2F TM Pokemart
    - Celadon Department Store 4F Evo Stone Pokemart
    - Celadon Department Store 5F Vitamin Pokemart
    - Two Island Market Stall
    """
    display_name = "Better Shops"


class FreeFlyLocation(Toggle):
    """
    Enables flying to one random location (excluding cities reachable with no items).
    """
    display_name = "Free Fly Location"


class TurboA(Toggle):
    """
    Holding A will advance most text automatically.
    """
    display_name = "Turbo A"


class ReceiveItemMessages(Choice):
    """
    Sets whether you receive an in-game notification when receiving an item. Items can still onlybe received in the
    overworld.

    - All: Every item shows a message.
    - Progression: Only progression items show a message
    - None: All items are added to your bag silently (badges will still show).
    """
    display_name = "Receive Item Messages"
    default = 1
    option_all = 0
    option_progression = 1
    option_none = 2


@dataclass
class PokemonFRLGOptions(PerGameCommonOptions):
    game_version: GameVersion
    game_revision: GameRevision

    shuffle_badges: ShuffleBadges
    shuffle_hidden: ShuffleHiddenItems

    itemfinder_required: ItemfinderRequired
    flash_required: FlashRequired
    oaks_aide_route_2: OaksAideRoute2
    oaks_aide_route_10: OaksAideRoute10
    oaks_aide_route_11: OaksAideRoute11
    oaks_aide_route_16: OaksAideRoute16
    oaks_aide_route_15: OaksAideRoute15

    viridian_city_roadblock: ViridianCityRoadblock
    pewter_city_roadblock: PewterCityRoadblock
    cerulean_city_roadblocks: CeruleanCityRoadblocks
    viridian_gym_requirement: ViridianGymRequirement
    viridian_gym_count: ViridianGymCount
    route22_gate_requirement: Route22GateRequirement
    route22_gate_count: Route22GateCount
    route23_guard_requirement: Route23GuardRequirement
    route23_guard_count: Route23GuardCount
    elite_four_requirement: EliteFourRequirement
    elite_four_count: EliteFourCount
    cerulean_cave_requirement: CeruleanCaveRequirement
    cerulean_cave_count: CeruleanCaveCount

    reusable_tm_tutors: ReusableTmsTutors
    min_catch_rate: MinCatchRate
    guaranteed_catch: GuaranteedCatch
    exp_modifier: ExpModifier
    blind_trainers: BlindTrainers
    better_shops: BetterShops
    free_fly_location: FreeFlyLocation

    turbo_a: TurboA
    receive_item_messages: ReceiveItemMessages
