from utils.dispatch.sql_tables import companyprofile_tables, psc_tables
from utils.dispatch.sql_tables import officerlist_tables, filinghistory_tables
from utils.dispatch.sql_tables import appointmentlist_tables, chargelist_tables
from configs.chapi_json_params import companyprofile_params, officerlist_params
from configs.chapi_json_params import psc_params, filinghistorylist_params
from configs.chapi_json_params import appointmentlist_params, chargelist_params
from utils.base_helpers import recursive_find

TABLES = ["table_name", "error_table", "empty_table"]

ARGS_PARAMS = {'al' : {"params"      : appointmentlist_params,
                       "create_stmts": appointmentlist_tables,
                       "all_tables"  : list(
                           recursive_find(TABLES, appointmentlist_params))},
               'ol' : {"params"      : officerlist_params,
                       "create_stmts": officerlist_tables,
                       "all_tables"  : list(
                           recursive_find(TABLES, officerlist_params))},
               'psc': {"params"      : psc_params,
                       "create_stmts": psc_tables,
                       "all_tables"  : list(
                           recursive_find(TABLES, psc_params))},
               'cp' : {"params"      : companyprofile_params,
                       "create_stmts": companyprofile_tables,
                       "all_tables"  : list(
                           recursive_find(TABLES, companyprofile_params))},
               'ch' : {"params"      : chargelist_params,
                       "create_stmts": chargelist_tables,
                       "all_tables"  : list(
                           recursive_find(TABLES, chargelist_params))},
               'fh' : {"params"      : filinghistorylist_params,
                       "create_stmts": filinghistory_tables,
                       "all_tables"  : list(
                           recursive_find(TABLES, filinghistorylist_params))}}
