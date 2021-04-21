## Pipeline

In this folder the actual scripts the do the job of:

- extracting the data from the API
- lightly preprocessing the data 
- dispatching the data to the postgres table it is supposed to go to.


### querying the api

The api has a bunch of edge cases which were incorporated in the extraction
script. These are the following:

1- The api might return empty jsons with error statuses. This has been
handled by catching the status code, and populating an error json. 

2- The api might return jsons with "error" keys, but a non error status code. 

3- When paginating (aka, you are querying the api for a list of something which is 
split into multiple requests each with a different start_index in the request url) it might
keep returning valid statuses with empty lists, instead of giving you an error. So imagine 
you are paginating the filings of a certain company, and the company has 300 filings, after
the 29th page, the api will keep returning a jsons with an empty list where previously there
were the file contents. 

Companieshouse has a team of people who keep maintaining the api, so there might be changes 
in the future. If you end up having new edge cases, just add conditions to the `res_is_not_illegal`
function. 

### cleaning the json

Before unpacking and dispatching the json to the postgres tables, some fields are cleaned. 

1- names of countries are normalised
2- nationalities strings are split, normalised, stacked and inserted in a separate table  
3- company names are normalised using the fingerprint algorithm.  
4- places and postal codes are cleaned using some regex.  
5- subelements of the jsons (which are read as dict in python) are serialised to json in order
to be inserted as JSONB in postgres.  

If you want to preprocess the data more, the `clean_json` function is where you would need to add
the extra steps. The utility function `clean_field` allows you to apply a list of regex to a value.

**Note** that it is in the `clean_data.py` script that the keys for the wanted transformations are 
defined. Imagine you want to add keys to be transformed to JSONB, you would need to add them to the 
`jsonb` variable. This has the effect of serialising to json the value of the K:V pair in any json
it is passed. This means that you cannot serialise the value of a certain companies house resource with
that key (imagine officerlist) but not for another resource (like psclist).

### unpacking and dispatching the json to postgres tables

Each json is read using its corresponding `json_param` (see configs folder), which is a dictionary
containing all the parameters that allow the `process_json` function to work. The logic is the following:

Each json is a tree that has a root (should be unique) and then fans out with branches.  
A branch can be:

- an atom:  `{root: XC322K, ..., atom1: 2, ..., atom2: "bar"}`
- a leaf:   `{root: XC323K, ..., atom1: 2, ..., leaf1: {"bar": "foo"}}`
- an array: `{root: XC324K, ..., atom1: 2, ..., leaf1: {"bar": "foo"}, array1: [1, 2, 3]}`

A branch containing an array can be:

- atoms:    `{root: XC324K, ..., array1: ["bar", "foo"], ..., array2: [1, 2, 3]}`
- leaves:   `{root: XC325K, ..., array1: [{...}, {...}]}`
- an array: `{root: XC326K, ..., array1: [[...], [...], [...]]}`

We leverage the recursive nature of trees (branches containing arrays containing branches...) and
apply a standard breadth-first algorithm to walk.

The logic of the unpack method is quite simple: the object is peeled from the outer data inwards, every step towards the inner most data unpack encounters a nested array or a nested hash and it inserts them in different tables.

Here are the steps of the algorithm:

1: flatten the data excluding the keys of leaves, arrays and keys to drop outright;  
2: insert flattened data in a table;  
3: pluck nested leaves data from the JSON, flattens and inserts them in corresponding tables;  
4: pluck nested array data from the JSON and:
   - if the array contains a list of dictionaries
     - recursively call unpack until there is no data left.  
   - if the array contains a list of atoms (string or digit)
     - it performs a bulk insert of the elements to a table.  
   - if the array contains a list of lists:  
     - it throws an error (edge case never seen in companies house jsons).  
     
### what you might want to extend

There are a few things that you might want to add. 

1: Companies House throws a certain error at you which you want to add to the list of errors you want to catch 
and insert in the `<res_name>_http_errors` table.  

Simply add the error code to the `WRONG_STATUSES` list in `extract_from_chapi`, add the error and the error response
to the `ERROR_HASH` (some error jsons are returned empty), and finally add a line in the `call_api()` function in 
`utils/extract/api_functions.py` here:

```
if not (res.status_code == 200 
        or res.status_code == 404 
        or res.status_code == 401
        or res.status_code == 400
        or res.status_code == 500):  # add errors you want to catch here
```

2: You want to clean and preprocess the json more before insertion. You can do it in the `clean_data.py` module.

3: You want to add another resource and you need to write a dedicated `json_params` dictionary. There are instructions 
in the `configs/README`. 