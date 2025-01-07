#!/usr/bin/env python3
import requests
import json
import os
import sys
import tomllib
import eyed3
from slugify import slugify
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
r_tracks = requests.get(f"{config['api_base']}/getPlaylist", query_options | {'id': playlist_id})
tracks = (r_tracks.json())['subsonic-response']['playlist']['entry']

# Extremely defensive QA function
def qa_track(file):
    qa_findings = list()
    qa_ok = True
    try:
        af = eyed3.load(file)
    except:
        qa_findings.append('fileopen')
        qa_ok = False
        return ({'result': qa_ok, 'findings': qa_findings})
    try:
        af.tag.frame_set[b'TPE1'][0]
    except:
    	qa_findings.append('no artist')
    try:
        af.tag.frame_set[b'TIT2'][0]
    except:
    	qa_findings.append('no title')
    try:
        txxx = dict()
        for fid in af.tag.frame_set[b'TXXX']:
            txxx[fid.description] = fid.text
    except:
        qa_findings.append('no user text frames')
    try:
        apic = dict()
        for fid in af.tag.frame_set[b'APIC']:
            apic[fid.description] = True
    except:
        qa_findings.append('no album art frames')
    try:
        apic['Proof of license at download']
    except:
        qa_findings.append('no proof')
    try:
        txxx['Local usage note']
    except:
        qa_findings.append('no usage')
    try:
        txxx['Local license tag']
    except:
        qa_findings.append('no license')
    try:
        txxx['Local download URL']
    except:
        qa_findings.append('no url')
    if len(qa_findings) > 0:
        qa_ok = False
    return ({'result': qa_ok, 'findings': qa_findings})

# Download all tracks and write the local TXT playlist for liquidsoap
with open(config['playlist_file'], 'w') as p:
    for track in tracks:
        track_slug = slugify(f"{track['title']} by {track['artist']}")
        track_file = f"{config['tracks_dir']}/{track['id']}_{track_slug}.{track['suffix']}"
        track_size = track['size']
        if os.path.isfile(track_file):
            #print(f"Already downloaded: {track_file}")
            pass
        else:
            r_track = requests.get(f"{config['api_base']}/download", query_options | {'id': track['id']})
            print(f"Downloading now: {track_file}")
            with open(track_file, "wb") as f:
                f.write(r_track.content)
        quality = qa_track(track_file)
        if quality['result'] == True:
            print(track_file, file=p)
        else:
            print(f"Rejecting {track_file}: {', '.join(quality['findings'])}")
