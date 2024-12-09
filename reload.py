#!/usr/bin/env python3
import tomllib
import sys
import socket

# Read config
with open(sys.argv[1], "rb") as ini:
	config = tomllib.load(ini)

try:
	with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
		client.connect(config['liquid_socket'])
		client.send(b"playlist.reload\n")
		client.send(b"quit\n")
		client.close()
except Exception as e:
	print(f"Failed to reload: {e}")
	sys.exit(255)
