# extract_helpers.py module


def iteritems_nested(dict_):
	"""
	factory func to contain function "fetch" returning list of tuples
	[(list of suffixes, value), ..., n] where n is
	len(dict_.keys()).

	usage:
	>>> from utils.base_helpers import iteritems_nested
	... d = {"a":1,
	...      "b": 2,
	...      "c": {"aa" : 3},
	...      "d" : ["cant be unpacked"]}
	... generator = iteritems_nested(dict_=d)
	... l = list(generator)
	... print(l)
	[(['d'], ['cant be unpacked']), (['a'], 1), (['c', 'aa'], 3), (['b'], 2)]
	"""

	def fetch(suffixes, v0):
		"""
		generator func unpacking the iterable dict_ recursively until all
		dict_ dictionaries are un-nested or dict_element is not a dictionary.
		"""
		if isinstance(v0, dict):
			for k, v in v0.items():
				for i in fetch(suffixes + [k], v):
					# yield tuple (list of suffixes, variable which could
					# be further unpacked)
					yield i
		else:
			# yield tuple (list of suffixes, variable which cannot
			# be further unpacked)
			yield suffixes, v0

	return fetch([], dict_)


def flatten_nested_dicts_only(dict_, drop=None):
	"""
	func creating new flattened dictionary from the generator iteritems_nested(dict_).
	usage:
	>>> from pprint import pprint
	... from utils.base_helpers import flatten_nested_dicts_only as flatten
	... d = {"a": 1, "b": 2, "c": {"aa": 3}, "d": ["cant be unpacked"]}
	... pprint(flatten(dict_=d, drop=["d"]))
	{'a': 1, 'b': 2, 'c_aa': 3}
	"""
	if drop is None:
		drop = []

	# k[0] is the root level key of the json. User can decide to recompose
	# a flattened JSON skipping certain keys.
	return dict(('_'.join(ks), v) for ks, v in iteritems_nested(dict_)
				if ks[0] not in drop)


def pipeline_each(data, fns):
	"""func that reduces a list of functions (fns) for each one of the element
	in a list (data)."""
	from functools import reduce
	return reduce(lambda a, x: list(map(x, a)), fns, data)


def is_empty_string(val):
	"""func that checks whether a string is empty."""
	if isinstance(val, str):
		if "".__eq__(val.strip()):
			return True
		else:
			return False


def nullify_empty_str_in_dict_vals(dict_):
	"""func that replaces the values in a dictionary which are empty
	strings with None"""
	return {k: v if not is_empty_string(v) else None for k, v in dict_.items()}


def read_file_with_url_ids(path):

	url_ids = []

	with open(path) as f:
		for line in f:
			line_string = line.strip().replace('"', '').replace("'", '')
			if line_string:  # empty lines will be skipped
				if "," in line_string:
					for id_ in line.split(","):
						(id_.strip().replace('"', '').replace("'", '')
						 and url_ids.append(id_.strip().replace('"', '')
											.replace("'", '')))
				else:
					url_ids.append(line_string.strip())
	return url_ids


def recursive_find(keys, dictionary):
	for k, v in dictionary.items():
		if k in keys:
			yield v
		elif isinstance(v, dict):
			for result in recursive_find(keys, v):
				yield result
		elif isinstance(v, list):
			for d in v:
				if isinstance(d, dict):
					for result in recursive_find(keys, d):
						yield result
