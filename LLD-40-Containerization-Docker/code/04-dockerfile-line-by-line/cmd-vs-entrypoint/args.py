"""Prints exactly what the container was asked to run -- the whole demo.

Whatever docker decided the command should be, sys.argv shows it.
"""
import sys

print("python received argv:", sys.argv)
