#!/usr/bin/env python3
import requests
import json
import os
import sys
import tomllib
from icecream import ic

# Read config
with open(sys.argv[1], "rb") as ini:
    config = tomllib.load(ini)

# Global Query options for the API
query_options = {'u': config['api_user'], 'p': config['api_key'], 'f': 'json'}

# Get the list of playlists
r_playlists = requests.get(f"{config['api_base']}/getPlaylists", query_options)
# unwrap it from the subsonic response object
playlists = (r_playlists.json())['subsonic-response']['playlists']['playlist']

# Find the playlist I'm interested in. Wrapped as a function for clarity(?)
def find_id_for_playlist(want_playlist, list_of_playlists):
    for p in list_of_playlists:
        if p['name'] == want_playlist:
            return p['id']
    raise ValueError(f"id for {want_playlist} not found.")

playlist_id = find_id_for_playlist(config['want_playlist'], playlists)

# Get the list of tracks on the playlist
featured_tracks = set()
featured_albums = set()
featured_artists = set()
r_tracks = requests.get(f"{config['api_base']}/getPlaylist", query_options | {'id': playlist_id})
tracks = (r_tracks.json())['subsonic-response']['playlist']['entry']
for track in tracks:
    featured_albums.add(track['albumId'])
    featured_artists.add(track['artistId'])
    featured_tracks.add(track['id'])

print(json.dumps({'tracks': len(featured_tracks), 'artists': len(featured_artists), 'albums': len(featured_albums)}))
with open(config['stats_file'], "w") as stats:
    json.dump({'tracks': len(featured_tracks), 'artists': len(featured_artists), 'albums': len(featured_albums)}, stats)
