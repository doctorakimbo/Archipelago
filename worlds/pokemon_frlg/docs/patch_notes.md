# Updates

* Badges, Fly Unlocks, and Progressive Items will no longer display a message if the `receive_item_messages` option is set to `none`.
* Dark caves will now kick you out immediately if you cannot use flash and `flash_required` is set to `required`.
* Cycling music will now play again when on the Bicycle and you are in an outdoor location.
* Removed the Union Room check that is made when entering Pokémon Centers. This removes the longer loading times that happened when entering them and talking to the Nurse will not send the player to the Shadow Realm this time. (rejoice palex)
* Removed the Pikachu tutorial part of the intro.
* Changed the movement on Cycling Road.
  * You will now always move very fast no matter what direction you are going.
  * Holding down the B button allows you to move slowly as long as the button is held.
* Changed instant text to now be a text speed option in game (text speed will default to instant).
* The boulders in Victory Road won't reset to their initial positions once the puzzle has been solved.
* Made it so that Oak's Pokémon in the intro is randomized.
* Increased the rate at which a Pokémon's HP drains in battle to be proportional to their max HP.
* Changed the purchase 50 coins option at the Celadon Game Corner to purchase 100 coins and added a new option the purchase 1000 coins.
* Added Player's PC item location
  * The potion that starts in the Player's PC is a location that will now be randomized.
* Added Running Shoes location
  * Given by one of Prof. Oak's Aides at the exit of Pewter City towards Route 3 after beating Brock.
* `Total Darkness` no longer forces the `flash_required` settting to `logic` if set to `off`.
* Updated option `card_key`.
  * Changed the new locations for when the Card Key is split to be newly added item balls in Silph Co. instead of being given by NPCs in Silph Co.
* Updated option `island_passes`.
  * Changed the new locations for when the Passes are split to be gotten from various events that are related to the Sevii Islands instead of from random NPCs on the islands.
* New option `split_teas`.
  * Splits the Tea item into four separate items: Blue Tea, Red Tea, Purple Tea, and Green Tea.
  * Each guard to Saffron City will require a different Tea in order to get past them.
  * Three new locations are added to the Celadon Condominiums. Brock, Misty, and Erika will be there after defeating them and give you a randomized item.
* Updated `Route 12 Boulders` in the `modify_world_state` option.
  * Adds additional boudlers that block the path between Route 12 and Lavender Town.
* Added `Open Silph` to the `modify_world_state` option.
  * The Team Rocket Grunt in front of Silph Co. will be moved without needing to rescue Mr. Fuji.
* Added `Remove Saffron Rockets` to the `modify_world_state` option.
  * The Team Rocket Grunts in Saffron City will be gone without needing to liberate Silph Co.
* Added `Block Vermilion Sailing` to the `modify_world_state` option.
  * Prevents you from sailing to Vermilion City on the Seagallop until you have gotten the S.S. Ticket.
* New option `normalize_encounter_rates`.
  * Sets every encounter slot to (almost) equal probability.
* New option `provide_hints`
  * Provides AP hints for locations that specify the item they give you once you've gotten the in game hint.
* New options `elite_four_rematch_requirement` and `elite_four_rematch_count`
  * Allows you to specify the requirements for accessing the E4 rematch. These requirements will be in addition to beating the E4 the first time and restoring the Network Machine on the Sevii Islands.

# Bug Fixes

* Coins will no longer display a message when received from another player unless the `receive_item_messages` option is set to `all`.