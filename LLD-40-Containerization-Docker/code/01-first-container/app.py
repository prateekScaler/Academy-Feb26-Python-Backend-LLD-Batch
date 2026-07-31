"""LLD-40, Tier 1: the same tiny script, run on your host AND inside a container.

Watch three things change between the two runs:
  1. hostname  -> on the host it is your machine; in a container it is a random id
  2. python    -> on the host it is whatever you installed; in the container it is
                  whatever the IMAGE ships (we pin python:3.12-slim in the Dockerfile)
  3. GREETING  -> same image, different env var = different behavior (12-factor config)
"""
import os
import platform
import socket

print("=" * 46)
print("  Hello from LLD-40!")
print("=" * 46)
print(f"hostname : {socket.gethostname()}")
print(f"python   : {platform.python_version()}")
print(f"GREETING : {os.environ.get('GREETING', 'hello from the host')}")
