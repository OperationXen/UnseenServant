from django.db.models import QuerySet, Sum


def get_game_stats(game_data: QuerySet) -> dict:
    """build a game statistics object"""
    unique_dms = game_data.values_list("dm__discord_id").distinct().count()

    stats = {"games_in_specified_period": game_data.count(), "unique_dms": unique_dms}
    return stats


def get_player_stats(player_data: QuerySet) -> dict:
    """build a player statistic object"""
    user_count = player_data.values_list("discord_id").distinct().count()
    all_players = player_data.filter(standby=False)
    all_players_count = len(all_players)
    unique_players = all_players.values_list("discord_id").distinct()
    unique_players_count = len(unique_players)

    average_games_per_player = 0
    if unique_players_count:
        average_games_per_player = all_players_count / unique_players_count

    all_waitlisters = player_data.filter(standby=True)
    all_waitlisters_count = len(all_waitlisters)

    not_selected = player_data.exclude(discord_id__in=unique_players)
    not_selected_ids = not_selected.values_list("discord_id").distinct()
    not_selected_count = not_selected_ids.count()

    playerstats = {
        "active_users": user_count,
        "total_seats": all_players_count,
        "unique_players": unique_players_count,
        "games_per_player": average_games_per_player,
        "total_unselected_players": not_selected_count,
    }
    return playerstats


def get_waitlist_stats(player_data: QuerySet) -> dict:
    """Calculate some useful statistics about waitlists"""
    all_players = player_data.filter(standby=False).count() or 1
    num_direct_entry = player_data.filter(standby=False, waitlist=None).count()
    num_players_waitlist = player_data.filter(standby=False).exclude(waitlist=None).count()

    # Find the player who came from furthest down the waitlist
    try:
        deepest_waitlist_position = player_data.exclude(waitlist=None).order_by("-waitlist").first().waitlist
    except AttributeError:
        deepest_waitlist_position = 0

    # find the average waitlist position amongst all players
    aggregate_waitlist_positions = player_data.aggregate(Sum("waitlist"))
    sum_waitlist_positions = aggregate_waitlist_positions["waitlist__sum"] or 0

    waitlist_stats = {
        "players_direct_entry": num_direct_entry,
        "players_from_waitlist": num_players_waitlist,
        "percent_waitlist_players": int((num_players_waitlist / all_players) * 100),
        "deepest_waitlist_position": deepest_waitlist_position,
        "average_waitlist_position": sum_waitlist_positions / all_players,
    }
    return waitlist_stats


def get_unsuccessful_player_details(player_data: QuerySet) -> dict:
    """Get details about players and how many games they've queued for"""

    players = player_data.filter(standby=False)
    unique_players = players.values_list("discord_id").distinct()
    waitlisters = player_data.filter(standby=True)
    not_selected = waitlisters.exclude(discord_id__in=unique_players)

    details = {}
    for user in not_selected:
        if user.discord_name in details:
            details[user.discord_name] += 1
        else:
            details[user.discord_name] = 1
    return details
