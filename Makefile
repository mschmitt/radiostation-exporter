all:
	./exporter.py config.toml
	toml2json config.toml | jq -r .tracks_dir  | xargs collectiongain
	./reload.py config.toml
