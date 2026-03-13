#!/bin/sh
import subprocess
import os

print("Formatting with black...")
subprocess.run(["black", os.path.abspath("./src")])
print("Finished...")
print("-" * 20)
print("Sorting imports...")
subprocess.run(["isort", "--sl", "-m", "3", os.path.abspath("./src")])
print("Finished...")
print("-" * 20)
print("Removing unused imports...")
subprocess.run(
    ["autoflake", "--remove-all-unused-imports", "-i", "-r", os.path.abspath("./src")]
)
print("Finished...")
