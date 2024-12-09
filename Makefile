all:
	./exporter.py config.toml
	./reload.py config.toml
