PYTHON=python3

all:

install:
	${PYTHON} -m pip install -r requirements.txt
	${PYTHON} setup.py install_exec install --optimize=1 --record=install_log.log

test:
	${PYTHON} -m pytest

clean:
	find -depth -name __pycache__ -type d -exec rm -r -- {} \;
	find -depth -name "*.log" -type f -exec rm -rf -- {} \;
	find -depth -name "*_cache" -type d -exec rm -rf -- {} \;
	find -depth -name "__logs__" -type d -exec rm -rf -- {} \;
	find -depth -name "*_cache" -type f -exec rm -rf -- {} \;
	find -depth -name "*.pyc" -type f -exec rm -rf -- {} \;
	rm -rf dist build stitchtoon.egg-info

.PHONE: clean test
