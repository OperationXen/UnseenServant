
def get_player_game_count(discord_user):
    """ get the total number of games a player is in """
    pass

def get_user_rank(discord_user):
    """ go through user roles and identify their best rank """
    if 'Sage' in discord_user.roles:
        pass
    elif 'Knight' in discord_user.roles:
        pass
    elif set(['Resident DM', 'Moderator', 'Treasurer', 'Admin']) & set(discord_user.roles):
        pass
    elif 'Jester' in discord_user.roles:
        pass
    elif 'Traveller' in discord_user.roles:
        pass
    else:
        pass

def get_player_max_games(discord_user):
    """ get the total number of games a user can sign up for """
    print(discord_user)