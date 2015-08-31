"""
Processes parsed data to be in the form:
keywords -> data desired
"""
import os

from blank.data_utils import OUTPUT_DIR, ELEMENT_MAPPING, SYMBOL_MAPPING
from blank.data_utils import cache, load

def lower_keys(_dict):
    return dict((key.lower(), value) for key, value in _dict.iteritems())

def update_dict(_dict, key, values):
    orig = _dict.get(key, {})
    orig.update(values)
    _dict[key] = orig

def set_value(_dict, keys, value):
    for key in keys:
        _dict[key] = value

def merge_dicts(ionization, isotopes):
    element_data = {}

    # Processes Ionization Levels
    for elem, ion in ionization.iteritems():
        symbol = SYMBOL_MAPPING.get(elem.lower(), elem.lower())
        ion = lower_keys(ion)
        ion['protons'] = ion['atomic number']
        element_data[symbol] = ion


    # Process Isotopes
    for elem, isotope in isotopes.iteritems():
        symbol = SYMBOL_MAPPING.get(elem.lower(), elem.lower())
        isotope = lower_keys(isotope)
        if "standard atomic weight" in isotope:
            set_value(
                element_data[symbol],
                [ "atomic weight", "atomic mass", "mass", "amu", "weight"],
                isotope["standard atomic weight"]
            )
        # isotope_dict = {}
        for each in isotope["isotopes"]:
            each = lower_keys(each)
            set_value(
                each,
                [ "atomic weight", "atomic mass", "mass", "amu", "weight"],
                each["relative atomic mass"]
            )
            mass_number = each["mass number"]
            if symbol in element_data:
                element_data[symbol][mass_number] = each

    return element_data

def get_the_big_dict(data, values = ""):
    result = {}
    for key, value in data.iteritems():
        if key == "links":
            value = dict(value)
            key = "ref"
        str_key = values + " "  + key
        result[str_key] = value
        if not isinstance(value, dict):
            try:
                assert int(str(value)) == float(str(value))
                result[str_key + " " + str(value)] = data
            except:
                pass
        else:
            result.update(get_the_big_dict(value, values=str_key))

    result = dict((key.strip().lower().replace("  ", " ").replace("symbol", "").replace("(", "").replace(")", ""), value) for key, value in result.iteritems())
    return dict((" ".join(sorted(set(key.split(" ")))), value) for key, value in result.iteritems())

def parse_out_isotopes(data):
    for key,value in data.iteritems():
        if key in ELEMENT_MAPPING:
            isotopes = []
            for k in value.keys():
                try:
                    val = int(str(k))
                    assert val == float(str(k))
                    isotopes.append((k, value.pop(k)))
                except:
                    pass
            if isotopes:
                data[key]["isotopes"] = dict(isotopes)
    return data



if __name__ == "__main__":
    result = merge_dicts(
        load(os.path.join(OUTPUT_DIR, "atomic_ionization_output.p")),
        load(os.path.join(OUTPUT_DIR,"atomic_weight_compositions.p"))
    )

    look_up = get_the_big_dict(parse_out_isotopes(result))
    print "\n".join(look_up.keys())
    print look_up["hydrogen"]
    cache(look_up, os.path.join(OUTPUT_DIR, "element_data.p"))
