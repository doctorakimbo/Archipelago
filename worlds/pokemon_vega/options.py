"""
Option definitions for Pokémon Vega
"""
from dataclasses import dataclass
from Options import Choice, DefaultOnToggle, NamedRange, OptionSet, PerGameCommonOptions, Range, Toggle
from .data import data


class Goal(Choice):
    """
    Sets what your goal is to consider the game beaten.

    - Elite Four: Defeat the Elite Four
    - Distant Island: Get to Distant Island and enter the Sphere Ruins' first room
    - Asphere: Catch or defeat Asphere at the core of the Sphere Ruins
    """
    display_name = "Goal"
    default = 0
    option_elite_four = 0
    option_distant_island = 1
    option_asphere = 2


class ExcludeSphereRuins(DefaultOnToggle): #todo: make sure this works
    """
    Excludes all the Sphere Ruins locations. Locations on Distant Island outside the ruins are still included.
    This is compatible with the Distant Island goal, but obviously not the Asphere goal.
    """
    display_name = "Exclude Sphere Ruins"
    
    
# todo: option for opening postgame early is important enough to be up here instead of in ModifyWorldState
# (warn to turn on level scaling in the desc)


# todo: option to remove hax items from trainers (replace with type-booster)


class ShuffleBadges(DefaultOnToggle):
    """
    Shuffle Gym Badges into the general item pool. If turned off, Badges will be shuffled among themselves.
    """
    display_name = "Shuffle Badges"


class ShuffleHiddenItems(Choice): # note: are there even recurring hidden items in vega?
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


class ExtraKeyItems(Toggle): # todo: edit rules; edit baserom; different item for Spirit Mansion; Machine Part -> Lab Pass
    """
    Adds key items that are required to access the DH Hideout, Safari Zone, Spirit Mansion, and the back room of Perimeter Labs.

    Adds four new locations:
    - Item in the house leading to DH Hideout
    - Item given by the man with the hungry Rynos
    - Second item given by your rival outside Spirit Mansion
    - Item given by the Perimeter Labs receptionist
    """
    display_name = "Extra Key Items"


class Trainersanity(Toggle):
    """
    Defeating a trainer gives you an item.

    Trainers are no longer missable. Each trainer will add a random filler item into the pool.
    """
    display_name = "Trainersanity"


class ShuffleFlyDestinationUnlocks(Toggle): # todo: don't have an item for distant island fly, as it's pointless - just unlock it immediately
    """
    Shuffles the ability to fly to Pokémon Centers into the pool. Entering the map that normally would unlock the
    fly destination gives a random item.
    """
    display_name = "Shuffle Fly Destination Unlocks"


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


class FlashRequired(Choice):
    """
    Sets whether HM05 Flash is logically required to navigate dark areas.

    - Off: Flash is not required to navigate dark areas.
    - Logic: Flash is logically required to navigate dark areas.
    - Required: Flash is required to navigate dark areas.
    """
    display_name = "Flash Required"
    default = 1
    option_off = 0
    option_logic = 1
    option_required = 2


class JunopsisCityRoadblock(Choice):
    """
    Sets the requirement for passing the Junopsis City Roadblock.

    - Open: The man will not stop you from entering Route 503.
    - Annette: The man will stop you from entering Route 503 until you defeat Annette.
    - Any Gym Leader: The man will stop you from entering Route 503 until you defeat any Gym Leader.
    - Elnath Badge: The man will stop you from entering Route 503 until you have the Elnath Badge.
    - Any Badge: The man will stop you from entering Route 503 until you have a Badge.
    """
    display_name = "Junopsis City Roadblock"
    default = 1
    option_open = 0
    option_annette = 1
    option_any_gym = 2
    option_elnath_badge = 3
    option_any_badge = 4


class ModifyWorldState(OptionSet): # not even touching this yet, but maybe option to open distant island via porcelia when reqs reached
    """
    Set various changes to the world's state that changes how you can access various regions and locations.
    The valid options and their effects are the following:

    - Modify Route 2: Replaces the northmost cuttable tree with a smashable rock.
    - Remove Cerulean Roadblocks: Removes the policeman and slowpoke that block the exits of the city.
    - Block Tunnels: Blocks the entrances to the underground tunnels with smashable rocks.
    - Modify Route 9: Replaces the cuttable tree with a smashable rock.
    - Modify Route 10: Adds a waterfall to Route 10 that connects the north and south sides.
    - Block Tower: Blocks the 1F stairs of Pokémon Tower with a ghost battle.
    - Route 12 Boulders: Adds boulders to Route 12 that block the exits to Route 11 & 13.
    - Modify Route 12: Adds impassable rocks to Route 12 that prevent surfing around Snorlax.
    - Modify Route 16: Adds a smashable rock to Route 16 that allows you to bypass the Snorlax.
    - Route 23 Trees: Adds cuttable trees to Route 23 under the sixth checkpoint.
    - Modify Route 23: Adds a waterfall to Route 23 at the end of the water section.
    - Victory Road Rocks: Adds smashable rocks to Victory Road that block the floor switches.
    - Early Gossipers: Removes the requirement to have entered the Hall of Fame from various Famesanity locations.
    - Total Darkness: Changes dark caves to be completely black and provide no vision without Flash.
    """
    display_name = "Modify World State"
    valid_keys = ["Modify Route 2", "Remove Cerulean Roadblocks", "Block Tunnels", "Modify Route 9",
                  "Modify Route 10", "Block Tower", "Route 12 Boulders", "Modify Route 12", "Modify Route 16",
                  "Route 23 Trees", "Modify Route 23", "Victory Road Rocks", "Early Gossipers", "Total Darkness"]


class AdditionalDarkCaves(OptionSet): # not even touching this yet
    """
    Set additional caves to be dark caves, potentially requiring Flash to navigate them.

    The caves that can be turned into dark caves are:
    - Mt. Moon
    - Diglett's Cave
    - Victory Road
    """
    display_name = "Additional Dark Caves"
    valid_keys = ["Mt. Moon", "Diglett's Cave", "Victory Road"]
    
    
# todo: add options for when legendaries appear: vanilla/pokemon castle/immediately; note: hide ganimede during mt. snowfall cutscene and add funny dialogue to people there


class RemoveBadgeRequirement(OptionSet):
    """
    Removes the badge requirement to use any of the HMs listed.

    HMs need to be listed by the move name. (e.g. Cut, Fly, Surf, etc.)
    """
    display_name = "Remove Badge Requirement"
    valid_keys = ["Cut", "Fly", "Surf", "Strength", "Flash", "Rock Smash", "Waterfall"]


class Route523GuardRequirement(Choice):
    """
    Sets the requirement for passing the guard in Orpimence City blocking Route 523.

    - Badges: Obtain some number of Badges.
    - Gyms: Beat some number of Gyms.
    """
    display_name = "Route 523 Guard Requirement"
    default = 0
    option_badges = 0
    option_gyms = 1


class Route523GuardCount(Range):
    """
    Sets the number of Badges/Gyms required to pass the Route 523 Guard.
    """
    display_name = "Route 523 Guard Count"
    default = 8
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


class CeruleanCaveRequirement(Choice): # distant island: rematches/badges/gyms; also add new option for determining which rematches count (similar to legendary hunt)
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


class LevelScaling(Choice):
    """
    Sets whether encounter levels are scaled by sphere access.

    - Off: Vanilla levels are used.
    - Spheres: Levels are scaled based on sphere access.
    - Spheres and Distance: Levels are scaled based on sphere access and the distance they are from your starting town.
    """
    display_name = "Level Scaling"
    default = 0
    option_off = 0
    option_spheres = 1
    option_spheres_and_distance = 2


class ModifyTrainerLevels(Range):
    """
    Modifies the level of all Trainer's Pokémon by the specified percentage.
    """
    display_name = "Modify Trainer Levels"
    default = 0
    range_start = -100
    range_end = 100


class RandomizeWildPokemon(Choice):
    """
    Randomizes wild Pokémon encounters (grass, caves, water, fishing)

    - Vanilla: Wild Pokémon are unchanged
    - Match Base Stats: Wild Pokémon are replaced with species with approximately the same BST
    - Match Type: Wild Pokémon are replaced with species that share a type with the original
    - Match Base Stats and Type: Apply both Match Base Stats and Match Type
    - Completely Random: There are no restrictions
    """
    display_name = "Randomize Wild Pokemon"
    default = 0
    option_vanilla = 0
    option_match_base_stats = 1
    option_match_type = 2
    option_match_base_stats_and_type = 3
    option_completely_random = 4


class WildPokemonGroups(Choice):
    """
    If wild Pokémon are not vanilla, they will be randomized according to the grouping specified.

    - None: Pokémon are not randomized together based on any groupings
    - Dungeons: All Pokémon of the same species in a dungeon are randomized together
    - Species: All Pokémon of the same species are randomized together
    """
    display_name = "Wild Pokemon Groups"
    default = 0
    option_none = 0
    option_dungeons = 1
    option_species = 2


class WildPokemonBlacklist(OptionSet):
    """
    Prevents listed species from appearing in the wild when wild Pokémon are randomized.

    May be overridden if enforcing other restrictions in combination with this blacklist is impossible.

    Use "Legendaries" as a shortcut for all legendary Pokémon.
    """
    display_name = "Wild Pokemon Blacklist"
    valid_keys = ["Legendaries"] + sorted([species.name for species in data.species.values()])


class RandomizeStarters(Choice):
    """
    Randomizes the starter Pokémon in Professor Oak's Lab.

    - Vanilla: Starters are unchanged
    - Match Base Stats: Starters are replaced with species with approximately the same BST
    - Match Type: Starters are replaced with species that share a type with the original
    - Match Base Stats and Type: Apply both Match Base Stats and Match Type
    - Completely Random: There are no restrictions
    """
    display_name = "Randomize Starters"
    default = 0
    option_vanilla = 0
    option_match_base_stats = 1
    option_match_type = 2
    option_match_base_stats_and_type = 3
    option_completely_random = 4


class StarterBlacklist(OptionSet):
    """
    Prevents listed species from appearing as a starter when starters are randomized.

    May be overridden if enforcing other restrictions in combination with this blacklist is impossible.

    Use "Legendaries" as a shortcut for all legendary Pokémon.
    """
    display_name = "Starter Blacklist"
    valid_keys = ["Legendaries"] + sorted([species.name for species in data.species.values()])

# if choice band, replace with type-booster if new pkmn has all special moves
# porygon-z should have upgrade only if it's porygon-z and wild/starter/movepool/tm randomization are all off (prevent thievery), otherwise type-booster
class RandomizeTrainerParties(Choice):
    """
    Randomizes the Pokémon in all trainer's parties.

    - Vanilla: Parties are unchanged
    - Match Base Stats: Trainer Pokémon are replaced with species with approximately the same BST
    - Match Type: Trainer Pokémon are replaced with species that share a type with the original
    - Match Base Stats and Type: Apply both Match Base Stats and Match Type
    - Completely Random: There are no restrictions
    """
    display_name = "Randomize Trainer Parties"
    default = 0
    option_vanilla = 0
    option_match_base_stats = 1
    option_match_type = 2
    option_match_base_stats_and_type = 3
    option_completely_random = 4


class TrainerPartyBlacklist(OptionSet):
    """
    Prevents listed species from appearing in trainer's parties when trainer's parties are randomized.

    May be overridden if enforcing other restrictions in combination with this blacklist is impossible.

    Use "Legendaries" as a shortcut for all legendary Pokémon.
    """
    display_name = "Trainer Party Blacklist"
    valid_keys = ["Legendaries"] + sorted([species.name for species in data.species.values()])


class RandomizeLegendaryPokemon(Choice):
    """
    Randomizes legendary Pokémon (Mewtwo, Zapdos, Deoxys, etc.). Does not randomize the roamer.

    - Vanilla: Legendary encounters are unchanged
    - Legendaries: Legendary encounters are replaced with another legendary Pokémon
    - Match Base Stats: Legendary encounters are replaced with species with approximately the same BST
    - Match Type: Legendary encounters are replaced with species that share a type with the original
    - Match Base Stats and Type: Apply both Match Base Stats and Match Type
    - Completely Random: There are no restrictions
    """
    display_name = "Randomize Legendary Pokemon"
    default = 0
    option_vanilla = 0
    option_legendaries = 1
    option_match_base_stats = 2
    option_match_type = 3
    option_match_base_stats_and_type = 4
    option_completely_random = 5


class RandomizeMiscPokemon(Choice):
    """
    Randomizes misc Pokémon. This includes non-legendary static encounters, gift Pokémon, and trade Pokémon

    - Vanilla: Species are unchanged
    - Match Base Stats: Species are replaced with species with approximately the same bst
    - Match Type: Species are replaced with species that share a type with the original
    - Match Base Stats and Type: Apply both Match Base Stats and Match Type
    - Completely Random: There are no restrictions
    """
    display_name = "Randomize Misc Pokemon"
    default = 0
    option_vanilla = 0
    option_match_base_stats = 1
    option_match_type = 2
    option_match_base_stats_and_type = 3
    option_completely_random = 4


class RandomizeTypes(Choice):
    """
    Randomizes the type(s) of every Pokémon. Each species will have the same number of types.

    - Vanilla: Types are unchanged
    - Shuffle: Types are shuffled globally for all species (e.g. every Water-type Pokémon becomes Fire-type)
    - Completely Random: Each species has its type(s) randomized
    - Follow Evolutions: Types are randomized per evolution line instead of per species
    """
    display_name = "Randomize Types"
    default = 0
    option_vanilla = 0
    option_shuffle = 1
    option_completely_random = 2
    option_follow_evolutions = 3


class RandomizeAbilities(Choice):
    """
    Randomizes abilities of every species. Each species will have the same number of abilities.

    - Vanilla: Abilities are unchanged
    - Completely Random: Each species has its abilities randomized
    - Follow Evolutions: Abilities are randomized, but evolutions that normally retain abilities will still do so
    """
    display_name = "Randomize Abilities"
    default = 0
    option_vanilla = 0
    option_completely_random = 1
    option_follow_evolutions = 2


class AbilityBlacklist(OptionSet):
    """
    Prevent species from being given these abilities.

    Has no effect if abilities are not randomized.
    """
    display_name = "Ability Blacklist"
    valid_keys = sorted(data.abilities.keys())


class RandomizeMoves(Choice):
    """
    Randomizes the moves a Pokémon learns through leveling.
    Your starter is guaranteed to have a usable damaging move.

    - Vanilla: Learnset is unchanged
    - Randomized: Moves are randomized
    - Start with Four Moves: Moves are randomized and all Pokémon know 4 moves at level 1
    """
    display_name = "Randomize Moves"
    default = 0
    option_vanilla = 0
    option_randomized = 1
    option_start_with_four_moves = 2


class MoveBlacklist(OptionSet):
    """
    Prevents species from learning these moves via learnsets, TMs, and move tutors.
    """
    display_name = "Move Blacklist"
    valid_keys = sorted(data.moves.keys())
    
    
# todo: option to only randomize types/abilities/moves of vanilla mons; option to randomize moves from within pool of level+egg


class HmCompatibility(NamedRange):
    """
    Sets the percent chance that a given HM is compatible with a species.
    """
    display_name = "HM Compatibility"
    default = -1
    range_start = 50
    range_end = 100
    special_range_names = {
        "vanilla": -1,
        "full": 100,
    }


class TmTutorCompatibility(NamedRange):
    """
    Sets the percent chance that a given TM or move tutor is compatible with a species.
    """
    display_name = "TM/Tutor Compatibility"
    default = -1
    range_start = 0
    range_end = 100
    special_range_names = {
        "vanilla": -1,
        "full": 100,
    }


class TmTutorMoves(Toggle):
    """
    Randomizes the moves taught by TMs and move tutors.

    Some opponents like gym leaders are allowed to use TMs. This option can affect the moves they know.
    """
    display_name = "Randomize TM/Tutor Moves"


class ReusableTmsTutors(Toggle):
    """
    Sets TMs to not break after use (they remain sellable). Allows Move Tutors to be used infinitely.
    """
    display_name = "Reusable TMs/Move Tutors"


class MinCatchRate(Range):
    """
    Sets the minimum catch rate a Pokémon can have. It will raise any Pokémon's catch rate to this value if its normal
    catch rate is lower than the chosen value.
    """
    display_name = "Minimum Catch Rate"
    range_start = 3
    range_end = 255
    default = 3


class GuaranteedCatch(Toggle):
    """
    Pokeballs are guaranteed to catch wild Pokémon regardless of catch rate.
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


class StartingMoney(Range):
    """
    Sets the amount of money that you start with.
    """
    display_name = "Starting Money"
    range_start = 0
    range_end = 999999
    default = 3000


class BlindTrainers(Toggle):
    """
    Trainers will not start a battle with you unless you talk to them.
    """
    display_name = "Blind Trainers"


# todo: actually change shops; also add options for restoring x items (w/ dialogue changes),
# revives (guy in stall just complains that he's useless now); restore full restores no matter what
# also auto add moon/sun stones to shamouti dept store
class BetterShops(Toggle):
    """
    Most Pokemarts will sell all normal Pokemart items. The exceptions are the following:

    - Shamouti Department Store 2F TM Pokemart
    - Shamouti Department Store 4F Evo Stone Pokemart
    - Shamouti Department Store 5F Vitamin Pokemart
    - Distant Island Market Stalls
    """
    display_name = "Better Shops"


class FreeFlyLocation(Choice):
    """
    Enables flying to one random location (excluding cities reachable with no items).
    """
    display_name = "Free Fly Location"
    default = 0
    option_off = 0
    option_exclude_shakudo = 1
    option_any = 2


class TownMapFlyLocation(Choice):
    """
    Enables flying to one random location once the town map has been obtained
    (excluding cities reachable with no items).
    """
    display_name = "Town Map Fly Location"
    default = 0
    option_off = 0
    option_exclude_shakudo = 1
    option_any = 2


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
class PokemonVegaOptions(PerGameCommonOptions):
    goal: Goal
    exclude_sphere_ruins: ExcludeSphereRuins

    shuffle_badges: ShuffleBadges
    shuffle_hidden: ShuffleHiddenItems
    extra_key_items: ExtraKeyItems
    trainersanity: Trainersanity
    shuffle_fly_destination_unlocks: ShuffleFlyDestinationUnlocks

    itemfinder_required: ItemfinderRequired
    flash_required: FlashRequired
    junopsis_city_roadblock: JunopsisCityRoadblock
    modify_world_state: ModifyWorldState
    additional_dark_caves: AdditionalDarkCaves
    remove_badge_requirement: RemoveBadgeRequirement

    route523_guard_requirement: Route523GuardRequirement
    route523_guard_count: Route523GuardCount
    elite_four_requirement: EliteFourRequirement
    elite_four_count: EliteFourCount
    cerulean_cave_requirement: CeruleanCaveRequirement
    cerulean_cave_count: CeruleanCaveCount

    level_scaling: LevelScaling
    modify_trainer_levels: ModifyTrainerLevels

    wild_pokemon: RandomizeWildPokemon
    wild_pokemon_groups: WildPokemonGroups
    wild_pokemon_blacklist: WildPokemonBlacklist
    starters: RandomizeStarters
    starter_blacklist: StarterBlacklist
    trainers: RandomizeTrainerParties
    trainer_blacklist: TrainerPartyBlacklist
    legendary_pokemon: RandomizeLegendaryPokemon
    misc_pokemon: RandomizeMiscPokemon
    types: RandomizeTypes
    abilities: RandomizeAbilities
    ability_blacklist: AbilityBlacklist
    moves: RandomizeMoves
    move_blacklist: MoveBlacklist
    hm_compatibility: HmCompatibility
    tm_tutor_compatibility: TmTutorCompatibility
    tm_tutor_moves: TmTutorMoves

    reusable_tm_tutors: ReusableTmsTutors
    min_catch_rate: MinCatchRate
    guaranteed_catch: GuaranteedCatch
    exp_modifier: ExpModifier
    starting_money: StartingMoney
    blind_trainers: BlindTrainers
    better_shops: BetterShops
    free_fly_location: FreeFlyLocation
    town_map_fly_location: TownMapFlyLocation

    turbo_a: TurboA
    receive_item_messages: ReceiveItemMessages
