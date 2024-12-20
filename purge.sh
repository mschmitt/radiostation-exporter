#!/usr/bin/env bash
set -o errexit

holdingdir="$(toml2json config.toml | jq -r .tracks_dir)"
playlist="$(toml2json config.toml | jq -r .playlist_file)"

for file in "${holdingdir}"/*mp3
do
	grep -q "$(basename "${file}")" "${playlist}" || rm -v "${file}"
done
