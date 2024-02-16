from django.db.models import QuerySet


def get_gamestats(game_data: QuerySet) -> dict:
    """build a game statistics object"""
    unique_dms = game_data.values_list("dm__discord_id").distinct().count()

    stats = {"games_in_specified_period": game_data.count(), "unique_dms": unique_dms}
    return stats


def get_playerstats(player_data: QuerySet) -> dict:
    """build a player statistic object"""
    user_count = player_data.values_list("user").distinct().count()
    all_players = player_data.filter(standby=False)
    all_players_count = len(all_players)
    unique_players = all_players.values_list("user").distinct()
    unique_players_count = len(unique_players)

    average_games_per_player = 0
    if unique_players_count:
        average_games_per_player = all_players_count / unique_players_count

    not_selected = player_data.exclude(user__in=unique_players)
    not_selected_ids = not_selected.values_list("user").distinct()
    not_selected_count = not_selected_ids.count()

    playerstats = {
        "active_users": user_count,
        "total_players": all_players_count,
        "unique_players": unique_players_count,
        "games_per_player": average_games_per_player,
        "total_unselected_players": not_selected_count,
    }
    return playerstats


def get_unsuccessful_player_details(player_data: QuerySet) -> dict:
    """Get details about players and how many games they've queued for"""

    players = player_data.filter(standby=False)
    unique_players = players.values_list("user__pk").distinct()
    waitlisters = player_data.filter(standby=True)
    not_selected = waitlisters.exclude(user__in=unique_players)

    details = {}
    for player in not_selected:
        if player.user.username in details:
            details[player.user.username] += 1
        else:
            details[player.user.username] = 1
    return details
