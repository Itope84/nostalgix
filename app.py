import json
import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


def get_spotify_token() -> str | None:
    """
    Obtain a token from the Spotify API using the Client Credentials Flow.

    Parameters:
    - client_id (str): Your Spotify Application's Client ID
    - client_secret (str): Your Spotify Application's Client Secret

    Returns:
    - str: An access token, or None if the request fails.
    """
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
        "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET"),
    }

    response = requests.post(url, headers=headers, data=urlencode(data))

    if response.status_code == 200:
        # If the request was successful, extract the token
        return response.json().get("access_token")
    else:
        # If the request failed, print the error and return None
        print(f"Failed to obtain token: {response.status_code} - {response.text}")
        return None


def get_user_token() -> str | None:
    # read user token from auth_response.json
    with open("auth_response.json", "r") as f:
        auth_response = json.load(f)
        return auth_response.get("access_token")


def get_user_id(token: str) -> str | None:
    """
    Obtain the user's Spotify ID using the provided access token.

    Parameters:
    - token (str): An access token from the Spotify API

    Returns:
    - str: The user's Spotify ID, or None if the request fails.
    """
    url = "https://api.spotify.com/v1/me"

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # If the request was successful, extract the user ID
        return response.json().get("id")
    else:
        # If the request failed, print the error and return None
        print(f"Failed to obtain user ID: {response.status_code} - {response.text}")
        return None


def create_playlist(
    token: str, user_id: str, name: str, description: str
) -> str | None:
    """
    Create a new playlist in the user's Spotify account.

    Parameters:
    - token (str): An access token from the Spotify API
    - user_id (str): The user's Spotify ID
    - name (str): The name of the new playlist
    - description (str): A description of the new playlist

    Returns:
    - str: The ID of the new playlist, or None if the request fails.
    """
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {
        "name": name,
        "description": description,
        "public": False,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        # If the request was successful, extract the playlist ID
        return response.json().get("id")
    else:
        # If the request failed, print the error and return None
        print(f"Failed to create playlist: {response.status_code} - {response.text}")
        return None


def add_tracks_to_playlist(
    tracks: list[str], token: str, user_id: str, playlist_id: str
):
    """
    Add tracks to an existing playlist in the user's Spotify account.

    Parameters:
    - tracks (list[str]): A list of Spotify track URIs to add to the playlist
    - token (str): An access token from the Spotify API
    - user_id (str): The user's Spotify ID
    - playlist_id (str): The ID of the playlist to add tracks to

    Returns:
    - None
    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    # because of spotify limits, we have to batch this in 100s
    batched_tracks = [tracks[i : i + 100] for i in range(0, len(tracks), 100)]
    for index, batch in enumerate(batched_tracks):
        data = {"uris": batch}
        response = requests.post(url, headers=headers, json=data)

        if not response.status_code in [200, 201]:
            print(
                f"Failed to add tracks batch {index} to playlist: {response.status_code} - {response.text}"
            )
        else:
            print(f"Tracks batch {index} added to playlist")


def create_playlists() -> dict | None:
    streaming_history_file = os.getenv("SPOTIFY_STREAMING_HISTORY_COMBINED_FILE")
    if not streaming_history_file:
        return None

    listening_data = pd.read_json(streaming_history_file)
    listening_data["ts"] = pd.to_datetime(listening_data["ts"])
    listening_data["year"] = listening_data["ts"].dt.year

    # unique_songs = get_unique_songs(listening_data)

    # export to json
    # with open("unique_songs.json", "w") as f:
    #     json.dump(unique_songs, f)

    token = get_user_token()
    # print(token)
    user_id = get_user_id(token)
    # create_top_50_all_time_songs_playlist(
    #     token, user_id, sort_by_ms_played(listening_data)
    # )
    # get_second_top_50_all_time_songs(token, user_id, sort_by_ms_played(listening_data))
    # create_top_monthly_songs_playlist(token, user_id, listening_data)
    # create_top_songs_by_year_playlists(token, user_id, listening_data)
    # create_top_songs_by_top_artists_playlists(token, user_id, listening_data)
    # create_seasonal_playlists(token, user_id, listening_data)
    # create_top_songs_by_artist_playlists(token, user_id, listening_data, "Passenger")
    create_all_songs_by_artist_playlists(token, user_id, listening_data, "Passenger")
    # export_sorted_artists_songs_to_csv(listening_data, "Passenger")


def get_top_songs_by_top_artists(df: pd.DataFrame) -> pd.DataFrame:
    # Step 1: Calculate total listening time per artist
    artist_listening_time = (
        df.groupby("master_metadata_album_artist_name")["ms_played"].sum().reset_index()
    )

    # Step 2: Identify the top 10 artists by listening time
    top_10_artists = artist_listening_time.nlargest(10, "ms_played")

    # Initialize an empty DataFrame to hold the top 5 songs for each of the top 10 artists
    top_songs_by_top_artists = pd.DataFrame()

    # Step 3: For each of the top 10 artists, find their top 5 most played songs
    for artist in top_10_artists["master_metadata_album_artist_name"]:
        # Filter the original DataFrame for the current artist
        artist_songs = df[df["master_metadata_album_artist_name"] == artist]

        # Group by song (track URI) and sum the ms_played, then get the top 5 songs
        top_songs = (
            artist_songs.groupby(["spotify_track_uri", "master_metadata_track_name"])[
                "ms_played"
            ]
            .sum()
            .nlargest(5)
            .reset_index()
        )

        # Add an artist name column to the top_songs DataFrame for clarity
        top_songs["artist_name"] = artist

        # Append the results to the top_songs_by_top_artists DataFrame
        top_songs_by_top_artists = pd.concat(
            [top_songs_by_top_artists, top_songs], ignore_index=True
        )

    return top_songs_by_top_artists


def create_top_songs_by_top_artists_playlists(
    token: str, user_id: str, df: pd.DataFrame
):
    top_songs_by_top_artists = get_top_songs_by_top_artists(df)

    playlist_id = create_playlist(
        token,
        user_id,
        "My Top Songs by Top Artists",
        "The top 5 songs for each of my top artists on Spotify.",
    )

    add_tracks_to_playlist(
        top_songs_by_top_artists["spotify_track_uri"].tolist(),
        token,
        user_id,
        playlist_id,
    )


def sort_by_ms_played(listening_data: pd.DataFrame) -> pd.DataFrame:
    # simplest approach uses ms_played as the metric because a song listened to in its entirety regardless of how long is more likely to be a favorite than a song started and skipped several times
    return (
        listening_data.groupby("spotify_track_uri")["ms_played"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


def create_top_50_all_time_songs_playlist(
    token: str, user_id: str, sorted_df: pd.DataFrame
):
    all_time_top_50 = sorted_df.head(50)

    # create playlist
    playlist_id = create_playlist(
        token,
        user_id,
        "My Top 50 All Time Songs",
        "The top 50 songs I've listened to the most on Spotify.",
    )

    # add tracks to playlist
    add_tracks_to_playlist(
        all_time_top_50["spotify_track_uri"].tolist(), token, user_id, playlist_id
    )


def get_second_top_50_all_time_songs(token: str, user_id: str, sorted_df: pd.DataFrame):
    second_all_time_top_50 = sorted_df.iloc[50:100]

    playlist_id = create_playlist(
        token,
        user_id,
        "My Second Top 50 All Time Songs",
        "The second top 50 songs I've listened to the most on Spotify.",
    )

    # add tracks to playlist
    add_tracks_to_playlist(
        second_all_time_top_50["spotify_track_uri"].tolist(),
        token,
        user_id,
        playlist_id,
    )


def get_top_songs_by_year(df: pd.DataFrame) -> pd.DataFrame:
    # Group by year and spotify_track_uri, then sum the ms_played for each group
    yearly_song_playtime = (
        df.groupby(
            [
                "year",
                "spotify_track_uri",
                "master_metadata_track_name",
                "master_metadata_album_artist_name",
            ]
        )["ms_played"]
        .sum()
        .reset_index()
    )

    # Sort within each year group by ms_played descending, then take the top 20 for each year
    top_20_songs_each_year = (
        yearly_song_playtime.groupby("year")
        .apply(lambda x: x.sort_values("ms_played", ascending=False).head(20))
        .reset_index(drop=True)
    )

    return top_20_songs_each_year


def get_unique_songs(df: pd.DataFrame) -> dict:
    """get unique songs by spotify_track_uri in a dict. Each song should have the form {spotify_track_uri: [track_name, artist_name, track_length, first_played]}. Each song is obtained by finding the first instance of the song where reason_end = trackdone for all the songs"""
    unique_songs = {}
    for song in df["spotify_track_uri"].unique():
        song_df = df[df["spotify_track_uri"] == song]
        song_df = song_df[song_df["reason_end"] == "trackdone"]
        if song_df.empty:
            continue

        length = song_df["ms_played"].iloc[0]
        fp = song_df["ts"].iloc[0]
        unique_songs[song] = [
            song_df["master_metadata_track_name"].iloc[0],
            song_df["master_metadata_album_artist_name"].iloc[0],
            "{length}",
            "{fp}",
        ]
    return unique_songs


def get_song_first_completed_instance(df: pd.DataFrame, song: str) -> pd.DataFrame:
    """get the first instance of the song where reason_end = trackdone"""
    song_df = df[df["spotify_track_uri"] == song]
    song_df = song_df[song_df["reason_end"] == "trackdone"]
    if song_df.empty:
        return None
    return song_df.iloc[0]

    # def get_top_songs_by_year_v2(df: pd.DataFrame, unique_songs: dict) -> pd.DataFrame:
    """get top songs by year, but first find the length of the song by finding the first instand of the song where reason_end = trackdone for all the songs. This means we filter only entries with ms_played >= get_song_first_completed_instance.ms_played, then group and then sum the ms_played for each group"""


def create_top_songs_by_year_playlists(token: str, user_id: str, df: pd.DataFrame):
    top_20_songs_each_year = get_top_songs_by_year(df)

    # Create a playlist for each year
    for year in top_20_songs_each_year["year"].unique():
        # Filter the DataFrame for the current year
        year_songs = top_20_songs_each_year[top_20_songs_each_year["year"] == year]

        # Create a playlist for the current year
        playlist_id = create_playlist(
            token,
            user_id,
            f"My Top {year} Songs",
            f"The top 20 songs I've listened to the most in {year} on Spotify.",
        )

        # Add the top songs for the current year to the playlist
        add_tracks_to_playlist(
            year_songs["spotify_track_uri"].tolist(), token, user_id, playlist_id
        )


def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month in [9, 10, 11]:
        return "Fall"


def get_seasonal_playlists(df: pd.DataFrame) -> pd.DataFrame:

    # Apply the function to create a new 'season' column
    df["season"] = df["ts"].dt.month.apply(get_season)

    # Group by season, spotify_track_uri, track name, and artist name, then sum the ms_played for each group
    seasonal_song_playtime = (
        df.groupby(
            [
                "season",
                "spotify_track_uri",
                "master_metadata_track_name",
                "master_metadata_album_artist_name",
            ]
        )["ms_played"]
        .sum()
        .reset_index()
    )

    # For each season, sort by ms_played descending, then take the top 20 for each season
    top_songs_each_season = (
        seasonal_song_playtime.groupby("season")
        .apply(lambda x: x.sort_values("ms_played", ascending=False).head(20))
        .reset_index(drop=True)
    )

    return top_songs_each_season


def create_seasonal_playlists(token: str, user_id: str, df: pd.DataFrame):
    top_songs_each_season = get_seasonal_playlists(df)

    # Create a playlist for each season
    for season in top_songs_each_season["season"].unique():
        # Filter the DataFrame for the current season
        season_songs = top_songs_each_season[top_songs_each_season["season"] == season]

        # Create a playlist for the current season
        playlist_id = create_playlist(
            token,
            user_id,
            f"My Top {season} Songs",
            f"The top 20 songs I've listened to the most in {season} on Spotify.",
        )

        # Add the top songs for the current season to the playlist
        add_tracks_to_playlist(
            season_songs["spotify_track_uri"].tolist(), token, user_id, playlist_id
        )


def get_top_monthly_songs(df: pd.DataFrame) -> pd.DataFrame:
    """A playlist of (unique) top songs listened to each month. Obtained by taking the top 5 songs each month, adjusting for weighted position (top song each month has more weight than second best etc.) and then taking the top 50 weighted occurring songs on this list"""
    df["month_year"] = df["ts"].dt.to_period("M")
    monthly_top_5 = (
        df.groupby(["month_year", "spotify_track_uri"])["ms_played"]
        .sum()
        .groupby(level=0)
        .nlargest(5)
        .reset_index(level=0, drop=True)
        .reset_index()
    )
    # Assign ranks within each month
    monthly_top_5["rank"] = monthly_top_5.groupby("month_year")["ms_played"].rank(
        "dense", ascending=False
    )

    # Calculate weight based on rank
    monthly_top_5["weight"] = 5 - monthly_top_5["rank"] + 1

    # Group by spotify_track_uri and sum the weights to get f_weight for each song
    song_weights = (
        monthly_top_5.groupby("spotify_track_uri")["weight"].sum().reset_index()
    )
    song_weights.columns = ["spotify_track_uri", "f_weight"]

    # Merge the f_weight back to the monthly_top_5 to get the f_weight of each song
    monthly_top_5_with_f_weight = monthly_top_5.merge(
        song_weights, on="spotify_track_uri"
    ).drop_duplicates(subset=["spotify_track_uri"])

    # Sort by f_weight
    monthly_top_5_with_f_weight = monthly_top_5_with_f_weight.sort_values(
        by="f_weight", ascending=False
    )

    # Take top 50 songs by f_weight
    top_songs_by_f_weight = monthly_top_5_with_f_weight.head(50)

    return top_songs_by_f_weight


def create_top_monthly_songs_playlist(token: str, user_id: str, df: pd.DataFrame):
    top_monthly_songs = get_top_monthly_songs(df)

    # create playlist
    playlist_id = create_playlist(
        token,
        user_id,
        "My Top Monthly Songs",
        "The top 50 songs I've listened to the most each month on Spotify.",
    )

    # add tracks to playlist
    add_tracks_to_playlist(
        top_monthly_songs["spotify_track_uri"].tolist(), token, user_id, playlist_id
    )


def get_top_songs_by_artist(
    df: pd.DataFrame, artist: str, size: int = 20
) -> pd.DataFrame:
    """A playlist of top songs listened to for a specific artist."""
    artist_songs = df[df["master_metadata_album_artist_name"] == artist]

    # Group by song (track URI) and sum the ms_played, then get the top 5 songs
    top_songs = (
        artist_songs.groupby(["spotify_track_uri", "master_metadata_track_name"])[
            "ms_played"
        ]
        .sum()
        .nlargest(size)
        .reset_index()
    )

    return top_songs


def create_top_songs_by_artist_playlists(
    token: str, user_id: str, df: pd.DataFrame, artist: str
):
    top_songs_by_artist = get_top_songs_by_artist(df, artist)

    playlist_id = create_playlist(
        token,
        user_id,
        f"My Favorite {artist} Songs",
        f"The top 20 songs I've listened to the most by {artist} on Spotify.",
    )

    add_tracks_to_playlist(
        top_songs_by_artist["spotify_track_uri"].tolist(),
        token,
        user_id,
        playlist_id,
    )


def get_all_songs_by_artist(df: pd.DataFrame, artist: str) -> pd.DataFrame:
    artist_songs = df[df["master_metadata_album_artist_name"] == artist]

    # Group by song (track URI) and sum the ms_played, and sort by ms_played descending
    all_songs = (
        artist_songs.groupby(["spotify_track_uri", "master_metadata_track_name"])[
            "ms_played"
        ]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    return all_songs


def create_all_songs_by_artist_playlists(
    token: str, user_id: str, df: pd.DataFrame, artist: str
):
    all_songs_by_artist = get_all_songs_by_artist(df, artist)

    playlist_id = create_playlist(
        token,
        user_id,
        f"All Songs by {artist}",
        f"All songs by {artist} on Spotify that I've ever played.",
    )

    add_tracks_to_playlist(
        all_songs_by_artist["spotify_track_uri"].tolist(),
        token,
        user_id,
        playlist_id,
    )


def export_sorted_artists_songs_to_csv(df: pd.DataFrame, artist: str):
    top_songs_by_artist = get_top_songs_by_artist(df, artist, 300)

    # save to file
    with open(f"{artist}_top_songs.csv", "w") as f:
        f.write(top_songs_by_artist.to_csv())


create_playlists()
