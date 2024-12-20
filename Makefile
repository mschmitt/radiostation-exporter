all:
	./exporter.py config.toml
	./purge.sh
	toml2json config.toml | jq -r .tracks_dir  | xargs collectiongain
	./reload.py config.toml
