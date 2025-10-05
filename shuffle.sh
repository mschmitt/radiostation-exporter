#!/usr/bin/env bash
set -o errexit

playlist="$(toml2json config.toml | jq -r .playlist_file)"

shuf "${playlist}" | sponge "${playlist}"
