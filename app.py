import stringql

from command_line_interface import parser
from utils.cli.defined_exceptions import raise_if_flags_clash, run_file_check
from app_scripts.extract_from_chapi import query_api
from utils.app.app_utils import make_url_list, make_dsn_dict
from utils.app.app_utils import create_tables, run_pipeline
from configs.cli_args_params import ARGS_PARAMS
from configs.pg_constants import DB_CONFIG_ABS_PATH, DB_SCHEMA


ARGS = parser.parse_args()
raise_if_flags_clash(args=ARGS)

flags_summary_dicts = {k: v for k, v in ARGS_PARAMS.items() if vars(ARGS)[k]}
url_ids = make_url_list(args=ARGS)

# ensure urls in file don't clash with flags passed
run_file_check(args=ARGS, url_ids=url_ids)


# all went well - start engine and process file.
engine = stringql.start_engine(**make_dsn_dict(DB_CONFIG_ABS_PATH))
conn = engine.connect(schema=DB_SCHEMA)

# create tables needed
create_tables(engine=engine, conn=conn, params=flags_summary_dicts)

for ix, json_id in enumerate(url_ids, 1):

    for _, summary_dict in flags_summary_dicts.items():

        json_ls = list(query_api(summary_dict["params"], json_id))

        run_pipeline(engine=engine,
                     conn=conn,
                     json_ls=json_ls,
                     json_id=json_id,
                     json_params=summary_dict["params"])
