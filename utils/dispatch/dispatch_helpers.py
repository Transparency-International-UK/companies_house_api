import json
from more_itertools import flatten

from utils.base_helpers import flatten_nested_dicts_only as flatten_dicts
from utils.base_helpers import nullify_empty_str_in_dict_vals as nullify_str
from utils.base_helpers import is_empty_string

# types
Number = (int, float)
Atom = (str, Number)
Collection = (list, tuple)


# helper funcs
def create_uid_pair(json, uid_key, uid_value=None):
    uid_pair = {}

    # -1 there exists no unique key in the json. The key value is passed by
    # user.

    # non-composite key
    if uid_value is not None and isinstance(uid_value, Atom):
        uid_pair = dict(zip(uid_key, [uid_value]))

    # composite key
    elif uid_value is not None and isinstance(uid_value, Collection):
        uid_pair = dict(zip(uid_key, uid_value))

    # -2 there exists a unique uid in the json.

    # extract it.
    elif uid_value is None:
        uid_pair = {k: v for k, v in json.items() if k in uid_key}

    return uid_pair


def get_root_key(params, root_key, uid_key):

    if params.get("is_root", True):
        return uid_key
    else:
        return isinstance(root_key, str) and [root_key] or root_key


def get_branches_params(params):

    arrays_params = params.get("arrays", [])
    leaves_params = params.get("leaves", [])

    if arrays_params:
        arrays_keys = [params_d.get("name") for params_d in arrays_params]
    else:
        arrays_keys = []

    if leaves_params:
        leaves_keys = [params_d.get("name") for params_d in leaves_params]
    else:
        leaves_keys = []

    return (arrays_params, arrays_keys,
            leaves_params, leaves_keys,)


def make_data_from_dict(dict_, add=None, drop=None):

    if add is None:
        add = {}

    # flatten_dicts returns a generator, realize into a dict before chaining.
    return nullify_str(dict(flatten_dicts(dict_, drop),
                            **add))


def prepare_tuple_from_atom(atom, add=None, prepend=True):

    if is_empty_string(val=atom):
        data = [None]
    else:
        data = [atom]

    if add and prepend:
        data = add + data

    elif add and not prepend:
        data.extend(add)

    return tuple(data)


def prepare_tuple_with_jsonb(dict_, add=None, prepend=True):

    data = [json.dumps(dict_)]

    if add and prepend:
        data = add + data

    elif add and not prepend:
        data.extend(add)

    return tuple(data)


def make_array_branch_fields(array_key, array_params):

    if array_key in array_params.get("uid_key"):
        fields = array_params.get("uid_key")
    else:
        fields = array_params.get("uid_key") + [array_key]

    return fields


def make_returned_uid_pair(uid_key, branch_uid_value):
    # connection.fetchall() returns tuples:
    # 1 -> non-composite key:  (["bar"],)
    # 2 -> composite key:      ([("bar", "foo")],)
    branch_uid_pair = (
        isinstance(branch_uid_value[0], Atom)           # 1 "bar"
        and dict(zip(uid_key, branch_uid_value))
        or isinstance(branch_uid_value[0], Collection)  # 2 ("bar", "foo")
        and dict(zip(uid_key, branch_uid_value[0])))

    return branch_uid_pair


def reduce_dict_seq_on_key(key, json_output_ls):

    ls = list(json_output_ls)
    head = ls.pop(0)
    rest = filter(lambda d: "errors" not in d, ls)
    if ls:
        all_other_items = flatten([d.get(key, [])
                                   for d in rest])
        head[key].extend(all_other_items)
    return head
