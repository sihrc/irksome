"""
Where the data lives loaded in memory because we don't like databases
"""
import os

from blank.data_utils import load, OUTPUT_DIR

ELEMENT_DATA = load(os.path.join(OUTPUT_DIR, "element_data.p"))
