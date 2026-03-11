PYTHON=python3

all:

install:
	${PYTHON} -m pip install -r requirements.txt
	${PYTHON} setup.py install_exec install --optimize=1 --record=install_log.log

test:
	${PYTHON} -m pytest

# ---------------------------------------------------------------------------
# Benchmarks
#
#   make bench                         run all benchmarks
#   make bench BENCH_FILTER=detection  run only names containing "detection"
#   make bench-profile BENCH_FILTER=pipeline/pixel+jpeg/small
#   make bench-profile BENCH_FILTER=pipeline/pixel+jpeg/small BENCH_SAVE_PROF=out.prof
#   make bench-list                    list available benchmarks
# ---------------------------------------------------------------------------
bench:
	${PYTHON} -m benchmarks $(if $(BENCH_FILTER),--filter $(BENCH_FILTER),)

bench-profile:
	${PYTHON} -m benchmarks --profile \
		$(if $(BENCH_FILTER),--filter $(BENCH_FILTER),) \
		$(if $(BENCH_SAVE_PROF),--save-prof $(BENCH_SAVE_PROF),)

bench-list:
	${PYTHON} -m benchmarks --list

clean:
	find -depth -name __pycache__ -type d -exec rm -r -- {} \;
	find -depth -name "*.log" -type f -exec rm -rf -- {} \;
	find -depth -name "*_cache" -type d -exec rm -rf -- {} \;
	find -depth -name "__logs__" -type d -exec rm -rf -- {} \;
	find -depth -name "*_cache" -type f -exec rm -rf -- {} \;
	find -depth -name "*.pyc" -type f -exec rm -rf -- {} \;
	find -depth -name "*.dat" -type f -exec rm -rf -- {} \;
	find -depth -name "*.prof" -type f -exec rm -rf -- {} \;
	rm -rf dist build stitchtoon.egg-info

.PHONY: all install test bench bench-profile bench-list clean
