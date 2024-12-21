all:
	./exporter.py config.toml
	./purge.sh
	# Remove all replaygain frames
	#toml2json config.toml | jq -r .tracks_dir  | xargs --no-run-if-empty --replace=_xargs_ sh -c 'eyeD3 --user-text-frame=replaygain_track_peak: --user-text-frame=replaygain_reference_loudness: --user-text-frame=replaygain_track_gain: --user-text-frame=replaygain_album_peak --user-text-frame=replaygain_album_gain --user-text-frame=QuodLibet\\:\\:replaygain_reference_loudness: _xargs_/*.mp3'
	toml2json config.toml | jq -r .tracks_dir  | xargs --no-run-if-empty --replace=_xargs_ sh -c 'replaygain _xargs_/*.mp3'
	./reload.py config.toml
