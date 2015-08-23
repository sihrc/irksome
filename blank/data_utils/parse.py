"""
Parses data files from nist
Output python serialized objects
"""
# TODO - combine all atomic references into 1 dictionary

import os, json, pprint, cPickle

import indicoio

from blank.data_utils import DATA_DIR, ELEMENT_MAPPING


def load_file(data_name):
    """
    load_file loads contents from file 'data_name'
    @param 'data_name' - string
    @return - string
    """
    def dec(func):
        def wrapper(*args, **kwargs):
            with open(os.path.join(DATA_DIR, data_name), 'rb') as f:
                data = func(json.loads(f.read()), *args, **kwargs)
                cache(data, os.path.join(
                    DATA_DIR, data_name.split(".")[0] + ".p")
                )
                return data
        return wrapper
    return dec

def cache(data, filename):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    cPickle.dump(data, open(filename, 'wb'))

@load_file("atomic_ionization_output.json")
def parse_ionization(data):
    formatted = {}
    for i, element in enumerate(data["ionization energies data"]):
        if not element:
            continue
        element_name = element.pop(u"Element Name")
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
        element_name = SYMBOL_MAPPING[element["Atomic Symbol"]]
        formatted[element_name] = element
    return formatted


if __name__ == "__main__":
    print parse_physical_constants()
