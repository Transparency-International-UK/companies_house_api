import stringql
from toolz import thread_last, curry
from more_itertools import flatten

from utils.dispatch.dispatch_helpers import prepare_tuple_with_jsonb
from utils.dispatch.dispatch_helpers import create_uid_pair
from utils.dispatch.dispatch_helpers import get_root_key
from utils.dispatch.dispatch_helpers import get_branches_params
from utils.dispatch.dispatch_helpers import make_data_from_dict
from utils.dispatch.dispatch_helpers import prepare_tuple_from_atom
from utils.dispatch.dispatch_helpers import make_array_branch_fields
from utils.dispatch.dispatch_helpers import make_returned_uid_pair
from utils.dispatch.dispatch_helpers import reduce_dict_seq_on_key

from utils.dispatch.sql_queries import delete_from_table
from utils.dispatch.sql_queries import insert_from_dict
from utils.dispatch.sql_queries import batch_insert
from utils.dispatch.sql_queries import upsert_tuple_containing_jsonb


# new types to make dispatch simpler
Number = (int, float)
Atom = (str, Number)
Collection = (list, tuple)

is_json_empty = lambda x: ((x.get("total_results", None) is not None
                           and x["total_results"] == 0)
                           or (x.get("total_count", None) is not None
                           and x["total_count"] == 0)
                           or (x.get("items", None) is not None
                           and x["items"] == 0))

is_json_error = lambda x: (x.get("errors", None) is not None)

MAX_DATA_PER_BATCH_INSERT = 1000


@curry
def process_json(json_output, engine, conn, params, uid_value, root_key=None):

    # create the k:v pair which will be the primary key of the table.
    uid_key = params.get("uid_key", None)

    uid_pair = create_uid_pair(json=json_output,
                               uid_key=uid_key,
                               uid_value=uid_value)

    # root of json will be needed to create composite keys for child tables.
    root_key = get_root_key(params=params,
                            root_key=root_key,
                            uid_key=uid_key)

    error_bool = is_json_error(json_output)
    empty_bool = is_json_empty(json_output)

    # errors and empty jsons are dispatched to their tables.

    if error_bool or empty_bool:

        # upsertion key is the same for error and empty -> "id_item_queried"
        upsert_key = params.get("error_table_cols")[0]

        illegal_data = prepare_tuple_with_jsonb(
            dict_=json_output, add=list(uid_pair.values()))  # add pkey

        upsert_tuple_containing_jsonb(
            engine=engine,
            conn=conn,
            tuple_=illegal_data,
            upsert_key=upsert_key,
            fields=(empty_bool and params["empty_table_cols"]
                    or error_bool and params["error_table_cols"]),
            table=(empty_bool and params["empty_table"]
                   or error_bool and params["error_table"])
        )

        return

    # each tree has branches. Branches can be made of:

    # - Atom. Ex. {... , "branch_1": 1} / numbers or strings.
    # - Leaf. Ex. {... , "branch_1": {"leaf_1: ...} / dictionaries.
    # - Array. Ex: {..., "branch_1": [...]} / lists or tuples.

    #   A branch containing an array can be made of:

    # - Atoms: {..., "branch_1": [1, 2, 3]} / numbers or strings
    # - Leaves:  {..., "branch_1": [{..}, {..}, {..}]} / dictionaries
    # - Arrays: {..., "branch_1": [[], []} / lists or tuples¹

    #     ¹ ! NOT SUPPORTED, there is no JSON in CH-API with this structure.

    (arrays_params, arrays_keys,
     leaves_params, leaves_keys) = get_branches_params(params)

    # prepare root level variables for the query
    keys_to_drop = list(flatten([arrays_keys,
                                 leaves_keys,
                                 params.get("drop", [])]))

    # if user tries to insert same record, simply delete it first.
    # constraint ON DELETE CASCADE is in all branches tables, hence deletion
    # will cascade ensuring duplicate record is deleted from all child tables.

    if params.get("is_root", False):
        delete_from_table(
            engine=engine,
            conn=conn,
            table_name=params.get("table_name"),
            del_keys=root_key,
            data=[uid_pair.get(k) for k in root_key])

    # insert and return the primary key to catch SERIAL types.
    # the returned uid value will be needed in recursive calls.
    returned_uid_value = (insert_from_dict(
                            engine=engine,
                            conn=conn,
                            data=make_data_from_dict(dict_=json_output,
                                                     add=uid_pair,
                                                     drop=keys_to_drop),
                            table=params.get("table_name"),
                            returning=True,
                            returning_key=uid_key)
                         .fetchone())

    returned_uid_pair = make_returned_uid_pair(
        uid_key=uid_key, branch_uid_value=returned_uid_value)

    # BCNF decompositions
    # the uid_key of a leaf is the same as the root level uid_key.
    # Example (below): the address branch has still a 1:1 relationship with
    # the root_level uid_key.

    # {"uid_key": a1,
    #  "name"   : "karl",
    #  ...,
    #  "address": {"line_1": "good road", "number": 2, "postal_code": "1234"}

    # parent (root) table whose primary key is "uid_key"
    # uid_key | name  |...
    # --------------------
    # a1      | karl  |...
    # a2      | maria |...

    # address table (foreign keyed to root table "uid_key" via "root_uid")
    # root_uid | line_1    | number |...
    # ----------------------------------
    #     a1   | good road |  2     |...
    #     a2   | bad       |  2     |...

    # just like the root level data, each leaf has keys to be inserted and
    # possibly some keys to be dropped.

    keys_to_drop_in_leaves = (
        [dict_.get("drop", []) for dict_ in leaves_params] if leaves_params
        else [])

    leaves_tables = ([dict_.get("table_name", []) for dict_ in leaves_params]
        if leaves_params else [])

    all_leaves_keys = zip(leaves_keys, keys_to_drop_in_leaves, leaves_tables)

    if leaves_keys:

        for leaf_key, keys_to_drop_in_leaf, table in all_leaves_keys:

            leaf_data = json_output.get(leaf_key, None)

            if leaf_data is not None:

                # leaves of leaves are outright flattened here.
                data = make_data_from_dict(dict_=leaf_data,
                                           add=returned_uid_pair,
                                           drop=keys_to_drop_in_leaf)

                insert_from_dict(engine=engine,
                                 conn=conn,
                                 table=table,
                                 data=data)

    # 4NF decompositions.
    # the uid_key of an array table is the same as the root level uid_key +
    # a serial identifying each record in the array.
    # Example (below): the children branch has a 1:many relationship with
    # the root_level uid_key.

    # {"uid_key": a1,
    #  "name"   : "karl",
    #  ...,
    #  "children": ["bob", "martha"]}

    # parent (root) table whose primary key is "uid_key"
    # uid_key | name       |...
    # --------------------------
    # a1      | karl smith |...
    # a2      | john nuts  |...

    # children table (foreign keyed to root table "uid_key" via "root_uid")
    #                (with composite primary key [root_uid, child_serial_id])
    # root_uid | child_serial_id | name
    # -----------------------------------------
    #     a1   |       1         | bobby smith
    #     a1   |       2         | martha smith

    if arrays_keys:

        for array_params in arrays_params:

            array_key = array_params["name"]
            array_data = json_output.get(array_key, [])

            if array_data:

                if isinstance(array_data[0], dict):

                    for element in array_data:

                        # recursively unpack until array_params is None.
                        if array_params is not None:

                            process_json(
                                engine=engine, conn=conn,
                                json_output=element, params=array_params,
                                uid_value=returned_uid_value,
                                root_key=root_key)  # remember what root was

                if isinstance(array_data[0], Atom):

                    table = array_params.get("table_name")

                    # prepare variables for batch dispatch.

                    # we need to add to each record the uid_value to be able
                    # to foreign key with the parent table.
                    # we need as many as the atoms in the array (for the map).

                    foreign_key = [
                        list(returned_uid_value) for _ in array_data]

                    data_tuples = list(
                        map(prepare_tuple_from_atom, array_data, foreign_key))

                    fields = make_array_branch_fields(array_key=array_key,
                                                      array_params=array_params)

                    batch_insert(engine=engine,
                                 conn=conn,
                                 table=table,
                                 data=data_tuples,
                                 fields=fields,
                                 max_per_batch=MAX_DATA_PER_BATCH_INSERT)

                if isinstance(array_data[0], Collection):
                    raise ValueError("this is not supported.")


if __name__ == "__main__":

    from pprint import pprint
    from extract_from_chapi import query_api
    from utils.dispatch.sql_tables import companyprofile_tables, psc_tables
    from utils.dispatch.sql_tables import officerlist_tables, chargelist_tables
    from utils.dispatch.sql_tables import filinghistory_tables
    from utils.dispatch.sql_tables import appointmentlist_tables
    from configs.chapi_json_params import companyprofile_params, psc_params
    from configs.chapi_json_params import officerlist_params
    from configs.chapi_json_params import filinghistorylist_params
    from configs.chapi_json_params import appointmentlist_params
    from configs.chapi_json_params import chargelist_params

    from clean_data import clean_json

    OFFICER_ID = "FVzeHfaxEHWP31pW1BIDeqWX8bs"
    WRONG_OFFICER_ID = "XXXXddddeeeerrr33"
    COMPANY_NUMBER = "SC021189"
    WRONG_COMPANY_NUMBER = "111SSS00"

    all_tables = [companyprofile_tables, psc_tables,
                  officerlist_tables, appointmentlist_tables,
                  filinghistory_tables, chargelist_tables]

    # to test insert here the database variables to form the connection url
    libpq = "dbname= user= password="
    engine = stringql.start_engine(libpq_string=libpq)
    conn = engine.connect(schema="companies_house_api_test")

    # create target tables

    for create_stmts in all_tables:
        engine.do_query(conn=conn, mode="w", query=create_stmts)

    cp = list(query_api(companyprofile_params, COMPANY_NUMBER))
    ol = list(query_api(officerlist_params, COMPANY_NUMBER))
    psc = list(query_api(psc_params, COMPANY_NUMBER))
    fh = list(query_api(filinghistorylist_params, COMPANY_NUMBER))
    ch = list(query_api(chargelist_params, COMPANY_NUMBER))
    al = list(query_api(appointmentlist_params, OFFICER_ID))

    company_info = [cp, ol, psc, fh, ch]
    company_info_params = [companyprofile_params, officerlist_params,
                           psc_params, filinghistorylist_params,
                           chargelist_params]

    cp_wrong = list(query_api(companyprofile_params, WRONG_COMPANY_NUMBER))
    ol_wrong = list(query_api(officerlist_params, WRONG_COMPANY_NUMBER))
    psc_wrong = list(query_api(psc_params, WRONG_COMPANY_NUMBER))
    fh_wrong = list(query_api(filinghistorylist_params, WRONG_COMPANY_NUMBER))
    ch_wrong = list(query_api(chargelist_params, WRONG_COMPANY_NUMBER))
    al_wrong = list(query_api(appointmentlist_params, WRONG_OFFICER_ID))

    company_infow = [cp_wrong, ol_wrong, psc_wrong, fh_wrong, ch_wrong]

    # test with correct company number and officer id
    for json_ls, params in zip(company_info, company_info_params):

        thread_last(json_ls,
                    (map, clean_json),
                    (reduce_dict_seq_on_key, "items"),
                    (process_json(engine=engine,
                                  conn=conn,
                                  params=params,
                                  uid_value=COMPANY_NUMBER)))
    thread_last(al,
                (map, clean_json),
                (reduce_dict_seq_on_key, "items"),
                (process_json(engine=engine,
                              conn=conn,
                              params=appointmentlist_params,
                              uid_value=OFFICER_ID)))

    # test with wrong company number and officer id
    for json_ls, params in zip(company_infow, company_info_params):

        thread_last(json_ls,
                    (map, clean_json),
                    (reduce_dict_seq_on_key, "items"),
                    (process_json(engine=engine,
                                  conn=conn,
                                  params=params,
                                  uid_value=WRONG_COMPANY_NUMBER)))

    thread_last(al_wrong,
                (map, clean_json),
                (reduce_dict_seq_on_key, "items"),
                (process_json(engine=engine,
                              conn=conn,
                              params=appointmentlist_params,
                              uid_value=WRONG_OFFICER_ID)))
