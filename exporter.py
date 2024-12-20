#!/usr/bin/env python3
import requests
import json
import os
import sys
import tomllib
from slugify import slugify

# Read config
with open(sys.argv[1], "rb") as ini:
	config = tomllib.load(ini)

# Global Query options for the API
query_options={'u': config['api_user'], 'p': config['api_key'], 'f': 'json'}

# Get the list of playlists
r_playlists=requests.get(f"{config['api_base']}/getPlaylists", query_options)
# unwrap it from the subsonic response object
playlists=(r_playlists.json())['subsonic-response']['playlists']['playlist']

# Find the playlist I'm interested in. Wrapped as a function for clarity(?)
def find_id_for_playlist(want_playlist, list_of_playlists):
    for p in list_of_playlists:
        if p['name'] == want_playlist:
            return p['id']
    raise ValueError(f"id for {want_playlist} not found.")

playlist_id = find_id_for_playlist(config['want_playlist'], playlists)

# Get the list of tracks on the playlist
r_tracks=requests.get(f"{config['api_base']}/getPlaylist", query_options | {'id': playlist_id})
tracks=(r_tracks.json())['subsonic-response']['playlist']['entry']

# Download all tracks and write the local TXT playlist for liquidsoap
with open(config['playlist_file'], 'w') as p:
    for track in tracks:
        track_slug=slugify(f"{track['title']} by {track['artist']}")
        track_file=f"{config['tracks_dir']}/{track['id']}_{track_slug}.{track['suffix']}"
        track_size=track['size']
        if os.path.isfile(track_file):
            print(f"Already have: {track_file}")
        else:
            r_track=requests.get(f"{config['api_base']}/download", query_options | {'id': track['id']})
            print(f"Downloading: {track_file}") 
            with open(track_file, "wb") as f:
                f.write(r_track.content)
        print(track_file, file=p)
