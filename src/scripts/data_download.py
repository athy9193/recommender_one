# Download/Extract playlist/track data from Spotify API
# Date: 2022-02-11
# Ref: https://towardsdatascience.com/extracting-song-data-from-the-spotify-api-using-python-b1e79388d50


########## IMPORTS ##########
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pandas as pd

########## CODE ##########

# Step 1: Make Spotipy object (incld. authenticating with Spotify)

with open("../../credentials/cred_spotify.json", "r") as f:
    pw = json.load(f)

client_id = pw["client_id"]
client_secret = pw["client_secret"]


client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret
)

sp = spotipy.Spotify(
    client_credentials_manager=client_credentials_manager,
    requests_timeout=20,
    retries=20,
)

# Step 2: Extracting Tracks from a Playlist


def get_uri_from_link(spotify_link):
    return spotify_link.split("/")[-1].split("?")[0]


def get_artist_info(artist_uri):
    """Generate information about an artist

    Parameters
    ----------
    artist_uri : string
        a URI of an artist

    Returns
    -------
    dictionary
        a dictionary contains an artist's name, URI, current followers, genres, popularity score
    """
    artist_info = sp.artist(artist_uri)

    artist_dict = dict(
        artist_name=artist_info["name"],
        artist_uri=artist_uri,
        artist_followers=artist_info["followers"]["total"],
        artist_genres=artist_info["genres"],
        artist_pop=artist_info["popularity"],
    )
    return artist_dict


def get_track_info_for_playlist(playlist_link):
    """Get track information for a given playlist"""
    playlist_uri = get_uri_from_link(playlist_link)
    results = sp.playlist_tracks(playlist_id=playlist_uri, market="US")

    tracks = dict(
        track_name=[], track_uri=[], track_pop=[], artist_name=[], artist_uri=[]
    )

    for track in results["items"]:
        tracks["track_name"].append(track["track"]["name"])
        tracks["track_uri"].append(track["track"]["id"])
        tracks["track_pop"].append(track["track"]["popularity"])

        tracks["artist_name"].append(track["track"]["artists"][0]["name"])
        tracks["artist_uri"].append(track["track"]["artists"][0]["id"])

    return pd.DataFrame(tracks)


# Editorial Playlist: Top Songs - Global (Weekly Music Charts)
playlist_link = (
    "https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=1333723a6eff4b7f"
)

a = get_track_info_for_playlist(playlist_link)

#%%

# Step 3; Extracting Features from Tracks
