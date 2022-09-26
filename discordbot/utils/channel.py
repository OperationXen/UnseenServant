def notify_game_channel(game, message):
    """ Send a notification to a game channel"""
    pass
 
def game_channel_tag_promoted_player(game, player):
    """ Send a message to the game channel notifying the player that they've been promoted """
    message = f"<@{player.discord_id}> promoted from waitlist"
    notify_game_channel(game, message)

def game_channel_tag_removed_player(game, player):
    """ Send a message to the game channel notifying the DM that a player has dropped """
    pass

def game_channel_add_player(game, player):
    pass

def game_channel_remove_player(game, player):
    pass
