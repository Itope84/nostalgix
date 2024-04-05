def get_top_20_artists_by_unique_songs(df: pd.DataFrame) -> pd.DataFrame:
    # Group by artist and count unique songs
    artist_unique_songs = (
        df.groupby("master_metadata_album_artist_name")["spotify_track_uri"]
        .nunique()
        .reset_index()
    )

    # Rename columns for clarity
    artist_unique_songs.columns = ["artist_name", "unique_songs_count"]

    # Sort the artists by the number of unique songs in descending order
    top_artists_by_unique_songs = artist_unique_songs.sort_values(
        by="unique_songs_count", ascending=False
    ).head(20)

    # Convert the top artists DataFrame to JSON format
    top_artists_by_unique_songs_json = top_artists_by_unique_songs.to_json(
        orient="records"
    )

    return top_artists_by_unique_songs_json


def get_top_20_artists_by_listening_time(df: pd.DataFrame) -> pd.DataFrame:
    # Step 1: Group by artist and aggregate to find total listening time and count unique songs
    artist_aggregates = (
        df.groupby("master_metadata_album_artist_name")
        .agg(
            total_listening_time_ms=("ms_played", "sum"),
            unique_songs=("spotify_track_uri", "nunique"),
        )
        .reset_index()
    )

    # Step 2: Sort the artists by total listening time to find the top 20
    top_20_artists = artist_aggregates.sort_values(
        by="total_listening_time_ms", ascending=False
    ).head(20)

    # Convert the top 20 artists DataFrame to JSON format
    top_20_artists_json = top_20_artists.to_json(orient="records")

    # Print the JSON string
    return top_20_artists_json
