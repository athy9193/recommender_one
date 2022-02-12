# Download/Extract playlist/track data from Spotify API
# Date: 2022-02-11
# Ref: https://towardsdatascience.com/extracting-song-data-from-the-spotify-api-using-python-b1e79388d50

########## IMPORTS ##########
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


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


playlist_link = (
    "https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=1333723a6eff4b7f"
)
#%%
playlist_uri = playlist_link.split("/")[-1].split("?")[0]


sp.playlist_tracks(playlist_id=playlist_uri)

#%%

# Step 3; Extracting Features from Tracks
