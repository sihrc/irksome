"""
Parses data files from nist
Output python serialized objects
"""
import os, json

import indicoio

from blank.data_utils import DATA_DIR, OUTPUT_DIR, ELEMENT_MAPPING, SYMBOL_MAPPING
from blank.data_utils import cache

def load_file(data_name, should_cache=True):
    """
    load_file loads contents from file 'data_name'
    @param 'data_name' - string
    @return - string
    """
    def dec(func):
        def wrapper(*args, **kwargs):
            with open(os.path.join(DATA_DIR, data_name), 'rb') as f:
                data = func(json.loads(f.read()), *args, **kwargs)
                if should_cache:
                    cache(data, os.path.join(
                        OUTPUT_DIR, data_name.split(".")[0] + ".p")
                    )
                return data
        return wrapper
    return dec


@load_file("atomic_ionization_output.json")
def parse_ionization(data):
    formatted = {}
    for i, element in enumerate(data["ionization energies data"]):
        if not element:
            continue
        element_name = element.pop(u"Element Name").lower()
        # Extract and cross reference references and corresponding urls
        references = element.pop("References")
        urls = element.pop("ReferencesURL")
        element["Links"] = zip(references, urls)

        element["Atomic Symbol"] = ELEMENT_MAPPING[element_name]
        formatted[element_name] = element
    return formatted

@load_file("physical_constants.json")
def parse_physical_constants(data):
    quantities = []
    elements = []
    for element in data["constant"]:
        if not element:
            continue
        quantities.append(element.pop("Quantity "))
        elements.append(element)

    list_keywords = indicoio.keywords(quantities, top_n=10)
    for i, element in enumerate(elements):
        element['Keywords'] = list_keywords[i].keys()

    return elements


@load_file("atomic_weight_compositions.json")
def parse_isotopes(data):
    formatted = {}
    for element in data["data"]:
        element_name = SYMBOL_MAPPING[element["Atomic Symbol"].lower()]
        formatted[element_name] = element
    return formatted

@load_file(os.path.join("srd_13","srd13_janaf.species.json"))
def parse_thermochemical(data):
    formatted = {}
    for spec in data["species"]:
        elem = spec.pop("molecular formula")
        filename = spec.pop("file")
        @load_file(os.path.join("srd_13", filename), should_cache=False)
        def parse_molecule(data):
            return dict((each["T"], each["values"]) for each in data["data"] if "T" in each)
        spec["thermochemical"] = parse_molecule()
        formatted[elem] = spec
    return formatted

if __name__ == "__main__":
    parse_ionization()
    parse_isotopes()
    parse_physical_constants()
    parse_thermochemical()
