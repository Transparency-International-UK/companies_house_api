import json
from countrynames import to_code
from fingerprints import generate

from utils.clean.json_cleaner_helpers import clean_field
from utils.clean.json_cleaner_helpers import split_nationality_string
from utils.clean.json_cleaner_helpers import nullify_nits

# replace separators with space
sub_sep_with_space = ('[_\\&;.,/-]', ' ')
# replace non alpha num to space, keep existing spaces
rm_non_alnum_preserve_space = ('[^A-Za-z0-9 ]', ' ')
# remove non alpha num
rm_non_alnum = ('[^A-Za-z0-9]', '')
# collapse multiple spaces
collapse_multispaces = ('\\s+', ' ')

places = ["locality", "legal_authority", "place_registered"]
jsonb = ["description_values", "data"]


def clean_json(data: dict) -> (list, dict):
    if isinstance(data, dict):
        copy = {}
        for k, v in data.items():

            if "country" in k:
                copy[k + "_iso"] = to_code(v)

            if "company_name" in k:
                copy[k + "_fp"] = generate(v)

            if k == "nationality":
                nat_ls = split_nationality_string(v)
                copy[k + "_list_iso"] = list(set(to_code(x, fuzzy=True)
                                                 for x in nat_ls))

            if k == "postal_code":
                copy[k + "_clean"] = (
                    nullify_nits(clean_field(v, [rm_non_alnum, ])))

            if k in places:
                copy[k + "_clean"] = (
                    nullify_nits(clean_field(v, [sub_sep_with_space,
                                                 rm_non_alnum_preserve_space,
                                                 collapse_multispaces, ])))
            if k in jsonb:

                # replace with json object
                copy[k + "_json"] = json.dumps(v)

            copy[k] = clean_json(v)

        return copy

    elif isinstance(data, list):

        copy = [clean_json(v) for v in data]
        return copy

    else:
        return data


if __name__ == "__main__":

    JSON = {
        "company_code": "123456",
        "name": "Astrocom AG",
        "officers": [{
            "name": "Abigail Kaloomp",
            "country_of_residence": "bvi",
            "nationality": "italy, DE and South Africa, Germany, IT"
        },
            {
            "name": "EXPONET limited",
            "address": {
                "address_line_1": "somewhere",
                "address_line_2": "somewhere_else",
                "postal_code": " Ag,12345 ",
                "locality": "Some shit 23!",
                "country": "united kingdom"
            }
        }],
        "address": {
            "address_line_1": "somewhere",
            "address_line_2": "somewhere_else",
            "country": "italia",
            "postal_code": "na"
        },
        "description_values": {"<key>": "<value>"}
    }

    new_json = clean_json(JSON)

    print(json.dumps(new_json, indent=4))
