from configparser import ConfigParser
from toolz import thread_last

from app_scripts.clean_data import clean_json
from utils.dispatch.dispatch_helpers import reduce_dict_seq_on_key
from app_scripts.dispatch_to_table import process_json
from utils.cli.defined_exceptions import file_is_csv_or_txt
from utils.base_helpers import read_file_with_url_ids
from pprint import pprint


def make_url_list(args):
    """
    given a file url runs checks for illegal cases and extracts the serializes
    content of the file to an iterable.
    """

    if not file_is_csv_or_txt(args):
        raise ValueError("The file of url_ids has to be in csv format.")

    else:
        url_ids = read_file_with_url_ids(path=args.file)

    return url_ids


def make_dsn_dict(db_config_path, section="PostgreSQL"):
    """func to extract the parameters of db connection form .ini file"""

    parser = ConfigParser()

    if not parser.read(db_config_path):
        raise Exception(
            f"Reading from File: {db_config_path} seems to return and empty "
            f"object.")
    else:
        parser.read(db_config_path)

    dict_ = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            dict_[param[0]] = param[1]
    else:
        raise Exception(
            f"Section {section} not found in the {db_config_path} file.")

    return dict_


def create_tables(engine, conn, params):

    create_stmts = [d["create_stmts"] for key, d in params.items()]

    for create_stmt in create_stmts:
        engine.do_query(conn=conn, mode="w", query=create_stmt)
    return


def run_pipeline(engine, conn, json_ls, json_id, json_params):

    # uncomment to debug
    pprint(json_ls)

    return thread_last(json_ls,
                       (map, clean_json),
                       (reduce_dict_seq_on_key, "items"),
                       (process_json(engine=engine,
                                     conn=conn,
                                     params=json_params,
                                     uid_value=json_id)))
