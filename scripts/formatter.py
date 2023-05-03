import os


os.system("python -m black src --skip-string-normalization")
os.system("python -m isort src")
os.system("python -m flake8")
