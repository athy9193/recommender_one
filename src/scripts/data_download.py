# Download/Extract playlist/track data from Spotify API
# Date: 2022-02-11
# Ref: https://towardsdatascience.com/extracting-song-data-from-the-spotify-api-using-python-b1e79388d50

#%%
########## IMPORTS ##########
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pandas as pd

########## CODE ##########
#%%
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
#%%
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


def get_track_info_for_playlist(playlist_uri):
    """Get track information for a given playlist"""
    results = sp.playlist_tracks(playlist_id=playlist_uri, market="US")

    tracks = dict(
        track_name=[], track_uri=[], track_pop=[], artist_name=[], artist_uri=[]
    )

    for track in results["items"]:
        # print(i)
        # print(track["track"]["name"])
        try:
            tracks["track_name"].append(track["track"]["name"])
        except TypeError:
            continue
        tracks["track_uri"].append(track["track"]["id"])
        tracks["track_pop"].append(track["track"]["popularity"])

        tracks["artist_name"].append(track["track"]["artists"][0]["name"])
        tracks["artist_uri"].append(track["track"]["artists"][0]["id"])

    return pd.DataFrame(tracks)


# Editorial Playlist: Top Songs - Global (Weekly Music Charts) - uri = "37i9dQZEVXbNG2KDcFcKOF"
# playlist_uri = "37i9dQZF1DXcBWIGoYBM5M"
# playlist_uri = "37i9dQZF1DX4dyzvuaRJ0n"  # mint: The world's biggest dance hits
# playlist_uri = "1wjKBV0kCtFUS6mwzDBNKD"  # this and that but also this
# # playlist_uri = "37i9dQZF1DX7Jl5KP2eZaS"  # Top Track 2020 (global)
# link = "https://open.spotify.com/playlist/37i9dQZF1EVHGWrwldPRtj?si=a44d12ebf34c4ad0"
# playlist_uri = get_uri_from_link(link)
# playlist_uri= "37i9dQZF1EVGJJ3r00UGAt" # Romantic Mix
# a = get_track_info_for_playlist(playlist_uri)
# a

# results = sp.playlist_tracks(playlist_id=playlist_uri, market="US")
# results
#%%

# Step 3; Extracting Features from Tracks

# track_uri = "46IZ0fSY2mpAiktS3KOqds"  # Easy On Me - Adele
# track_sonic_feats = sp.audio_features(track_uri)[0]


def get_audio_features_for_tracks(track_df):
    audio_feats = (
        pd.DataFrame(sp.audio_features(track_df["track_uri"]))
        .drop(columns=["uri", "track_href", "analysis_url"])
        .rename(columns={"id": "track_uri"})
    )

    return track_df.merge(
        audio_feats, how="left", left_on="track_uri", right_on="track_uri"
    )


#%%
# Step 4: Generate a list of playlists

# Types of playlists on Spotify:
# Editorial playlist are picked by Spotify's team and highly competitive given the strong follower base
# Algorithmic playlist: are affected by each listener's plays, likes, shares, skips and playlist adds,
# In general, the higher the popularity of your track and the more followers you have, the more of these playlists you’ll end up on.
# Spotify claims that even conversations about your music across the internet will help influence the algorithm
# Personalized playlist: This is the list of tracks anyone would see that opens the playlist “unpersonalized” in an incognito/private browser.

# Source: https://lab.songstats.com/the-ultimate-spotify-playlist-guide-e3dab9826419


def get_playlists(user_uri="spotify"):
    """Get public playlists owned by a given user_uri"""
    playlist_results = sp.user_playlists(user_uri, limit=50)  # cannot be higher than 50
    playlists = dict(
        playlist_name=[],
        playlist_uri=[],
        playlist_owner_name=[],
        playlist_owner_type=[],
        playlist_owner_uri=[],
        playlist_description=[],
    )
    for playlist in playlist_results["items"]:
        playlists["playlist_name"].append(playlist["name"])
        playlists["playlist_uri"].append(playlist["id"])
        playlists["playlist_owner_name"].append(playlist["owner"]["display_name"])
        playlists["playlist_owner_type"].append(playlist["owner"]["type"])
        playlists["playlist_owner_uri"].append(playlist["owner"]["id"])
        playlists["playlist_description"].append(playlist["description"])
        # playlist followers?

    return pd.DataFrame(playlists)
    # return playlist_results


# b = get_playlists(user_type="algorithmic")
# b = get_playlists(
#     user_uri="t1f2hyh0i089f282hzc4ootsw"
# )  # username of atruong@nettwerk.com

# username of May # https://open.spotify.com/user/31jb3pjpewtuoi7j4qdytryjahta?si=5932be1dfdd144f8

#%%
# # link = "https://open.spotify.com/playlist/37i9dQZF1EVHGWrwldPRtj?si=a44d12ebf34c4ad0" # Chill Mix For Alex
# user_link = "https://open.spotify.com/user/playlistmecanada?si=1a52074e06774bc9"
# uri = get_uri_from_link(user_link)

a = get_track_info_for_playlist("37i9dQZF1DXcBWIGoYBM5M")


#%%
# Step 5: Put everything together


def get_track_data_from_50_playlists_by_user(user_uri="Spotify"):

    # Get a list of 50 playlists by user "Spotify"
    playlist_df = get_playlists(user_uri)

    # Get tracks in the 50 playlist
    track_df = pd.DataFrame()
    for _, row in playlist_df.iterrows():
        # print(row["playlist_name"])
        temp_track_df = get_track_info_for_playlist(
            row["playlist_uri"]
        )  # track_uri, pop, artist_uri
        # Get audio features for tracks
        temp_track_df = get_audio_features_for_tracks(temp_track_df)
        temp_track_df["playlist_name"] = row["playlist_name"]
        temp_track_df["playlist_uri"] = row["playlist_uri"]
        track_df = pd.concat([track_df, temp_track_df])

    return track_df


#%%

# TODO: to debug
a = get_track_info_for_playlist("37i9dQZF1DWT6SJaitNDax")
get_audio_features_for_tracks(a)

# TODO: get playlist over time? Trend in music over time?
# spotify:app:genre:2020 # to generate a group of playlist for 2020 (top track, top artists)


########## MAIN ##########


def main():

    track_df = get_track_data_from_50_playlists_by_user(user_uri="Spotify")

    track_df.to_parquet("../../results/track_date.parquet")

    print("Completed!")


if __name__ == "__main__":
    main()

# %%

# a = pd.read_parquet("../../results/track_date.parquet")

# %%
