"""Actual Linux RSS for the unchanged server's optional resource measurement.

The base image lacks psutil. This test-only instrumentation reads resident
pages from /proc/self/statm; no model, input or detection rule is replaced.
Run inside the isolated qualification container, outside /qualified sources.
"""
import os
from pathlib import Path
import sys

sys.path.insert(0, '/qualified')
from tools import wakeword_calibration as calibration


def resident_bytes():
    return int(Path('/proc/self/statm').read_text().split()[1])*os.sysconf('SC_PAGE_SIZE')


calibration.rss_bytes = resident_bytes
raise SystemExit(calibration.main(['resources', '--iterations', '200']))
