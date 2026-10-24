from __future__ import annotations

from phase0a.simulator import Player, Team, default_teams


CAREER_VERSION = "career-lifecycle-v1"
RETIREMENT_AGE = 35
RATING_NAMES = ("shooting", "passing", "defense", "rebounding", "stamina")
DEBUT_AGES = {
    "Jalen Cross": 25,
    "Micah Vale": 22,
    "Dorian Pike": 28,
    "Kellan Shore": 31,
    "Andre North": 29,
    "Malik Frost": 20,
    "Nico Reyes": 23,
    "Tariq Stone": 27,
    "Eli Mercer": 21,
    "Roman Voss": 33,
    "Cal Brooks": 30,
    "Mateo Cruz": 24,
    "Soren Lake": 21,
}
DEBUT_SEASONS = {"Soren Lake": 4}
REPLACEMENTS = {"Roman Voss": Player("Soren Lake", 74, 72, 73, 78, 84)}


def debut_season(player_name: str) -> int:
    if player_name not in DEBUT_AGES:
        raise ValueError(f"missing career age for {player_name!r}")
    return DEBUT_SEASONS.get(player_name, 1)


def age_for_season(player_name: str, season_number: int) -> int:
    first_season = debut_season(player_name)
    if season_number < first_season:
        raise ValueError(f"{player_name} does not enter until season {first_season}")
    return DEBUT_AGES[player_name] + season_number - first_season


def career_stage(age: int) -> str:
    if age <= 23:
        return "DEVELOPMENT"
    if age <= 29:
        return "PRIME"
    if age < RETIREMENT_AGE:
        return "VETERAN"
    return "FINAL SEASON" if age == RETIREMENT_AGE else "RETIRED"


def retirement_season(player_name: str) -> int:
    return debut_season(player_name) + RETIREMENT_AGE - DEBUT_AGES[player_name]


def career_status(player_name: str, completed_seasons: int) -> str:
    if completed_seasons < 0:
        raise ValueError("completed seasons cannot be negative")
    return "RETIRED" if completed_seasons >= retirement_season(player_name) else "ACTIVE"


def signature_ratings(player: Player) -> tuple[str, str]:
    ranked = sorted(
        RATING_NAMES,
        key=lambda name: (-getattr(player, name), RATING_NAMES.index(name)),
    )
    return ranked[0], ranked[1]


def player_for_season(player: Player, season_number: int) -> Player:
    age_for_season(player.name, season_number)
    final_season = retirement_season(player.name)
    if season_number > final_season:
        raise ValueError(f"{player.name} retired after season {final_season}")
    ratings = {name: getattr(player, name) for name in RATING_NAMES}
    signatures = signature_ratings(player)
    weakest_non_signature = min(
        (name for name in RATING_NAMES if name not in signatures),
        key=lambda name: (ratings[name], RATING_NAMES.index(name)),
    )
    for year in range(debut_season(player.name) + 1, season_number + 1):
        age = age_for_season(player.name, year)
        if age <= 24:
            for name in signatures:
                ratings[name] = min(getattr(player, name) + 3, ratings[name] + 1)
        elif age >= 31:
            ratings["stamina"] = max(40, ratings["stamina"] - 1)
            if age >= 33:
                ratings[weakest_non_signature] = max(40, ratings[weakest_non_signature] - 1)
    return Player(player.name, *(ratings[name] for name in RATING_NAMES))


def teams_for_season(season_number: int) -> tuple[Team, Team]:
    if season_number < 1:
        raise ValueError("season number must be positive")
    return tuple(
        Team(
            team.name,
            tuple(
                player_for_season(
                    player
                    if season_number <= retirement_season(player.name)
                    else REPLACEMENTS.get(player.name, player),
                    season_number,
                )
                for player in team.players
            ),
        )
        for team in default_teams()
    )
