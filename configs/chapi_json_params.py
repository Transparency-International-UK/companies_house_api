companyprofile_params = {
    "is_root": True,
    "name": "companyprofile",
    "table_name": "companyprofile",
    "error_table": "companyprofile_http_errors",
    "error_table_cols": ["id_item_queried", "error_json"],
    "arrays": [
        {"name": "previous_company_names",
         "table_name": "cp_previous_company_names",
         "uid_key": ["company_number", "serial_id"]},
        {"name": "sic_codes",
         "table_name": "cp_sic_codes",
         "uid_key": ["company_number"]}
    ],
    "leaves": [
        {"name": "links",
         "table_name": "cp_links"},
        {"name": "registered_office_address",
         "table_name": "cp_registered_office_address"},
        {"name": "accounts",
         "table_name": "cp_accounts"},
        {"name": "annual_return",
         "table_name": "cp_annual_return"},
        {"name": "foreign_company_details",
         "table_name": "cp_foreign_company_details"},
        {"name": "branch_company_details",
         "table_name": "cp_branch_company_details"},
        {"name": "confirmation_statement",
         "table_name": "cp_confirmation_statement"}],
    "uid_key": ["company_number"],
    "drop": ["previous_company_names_fp"]
}

psc_params = {
    "is_root": True,
    "name": "psc",
    "table_name": "psc",
    "error_table": "psc_http_errors",
    "empty_table": "psc_empty",
    "error_table_cols": ["id_item_queried", "error_json"],
    "empty_table_cols": ["id_item_queried", "empty_json"],
    "items_per_page": 100,
    "arrays": [{
        "name": "items",
        "table_name": "psc_items",
        "arrays": [
            {"name": "natures_of_control",
             "table_name": "psc_items_natures_of_control",

             # when inserting from list of atoms (str and digits) adding
             # the serial_id into the uid_key list throws an error:
             # psycopg2.errors.SyntaxError: INSERT has more target columns
             # than expressions

             "uid_key": ["company_number", "psc_serial_id"]},
            {"name": "nationality_list_iso",
             "table_name": "psc_items_nationalities",

             # when inserting from list of atoms (str and digits) adding
             # the serial_id into the uid_key list throws an error:
             # psycopg2.errors.SyntaxError: INSERT has more target columns
             # than expressions

             "uid_key": ["company_number", "psc_serial_id"]}],
        "uid_key": ["company_number", "psc_serial_id"],
        "leaves": [
            {"name": "address",
             "table_name": "psc_items_address"},
            {"name": "identification",
             "table_name": "psc_items_identification"},
            {"name": "name_elements",
             "table_name": "psc_items_name_elements"}],
        "drop": ["nationality"]
    }],
    "uid_key": ["company_number"],
}

officerlist_params = {
    "is_root": True,
    "name": "officerlist",
    "table_name": "officerlist",
    "error_table": "officerlist_http_errors",
    "empty_table": "officerlist_empty",
    "error_table_cols": ["id_item_queried", "error_json"],
    "empty_table_cols": ["id_item_queried", "empty_json"],
    "items_per_page": 100,
    "arrays": [{
        "name": "items",
        "table_name": "ol_items",
        "uid_key": ["company_number", "officer_serial_id"],
        "arrays": [{
            "name": "former_names",
            "table_name": "ol_items_former_names",
            "uid_key": ["company_number", "officer_serial_id", "serial_id"]},
                   {
            "name": "nationality_list_iso",
            "table_name": "ol_items_nationalities",

            # when inserting from list of atoms (str and digits) adding
            # the serial_id into the uid_key list throws an error:
            # psycopg2.errors.SyntaxError: INSERT has more target columns
            # than expressions

            "uid_key": ["company_number", "officer_serial_id"]}
        ],
        "leaves": [
            {"name": "address",
             "table_name": "ol_items_address"},
            {"name": "identification",
             "table_name": "ol_items_identification"}],
        "drop": ["nationality"]}],
    "uid_key": ["company_number"],
}

appointmentlist_params = {
    "is_root": True,
    "name": "appointmentlist",
    "table_name": "appointmentlist",
    "error_table": "appointmentlist_http_errors",
    "error_table_cols": ["id_item_queried", "error_json"],
    "items_per_page": 50,
    "arrays": [{
        "name": "items",
        "table_name": "al_items",
        "uid_key": ["appointmentlist_url_id", "appointment_serial_id"],
        "arrays": [{
            "name": "former_names",
            "table_name": "al_items_former_names",
            "uid_key": ["appointmentlist_url_id", "appointment_serial_id",
                        "serial_id"]},
            {"name": "nationality_list_iso",
             "table_name": "al_items_nationalities",

            # pg adds extra SERIAL id here but we cannot add it to the list
            # it would throw an error (this is a string we are splitting, not
            # a pre-existing array in the json.

             "uid_key": ["appointmentlist_url_id", "appointment_serial_id"]}
        ],
        "leaves": [
            {"name": "address",
             "table_name": "al_items_address"},
            {"name": "identification",
             "table_name": "al_items_identification"},
            {"name": "name_elements",
             "table_name": "al_items_name_elements"}],
        "drop": ["nationality"]}],
    "uid_key": ["appointmentlist_url_id"],
    }

filinghistorylist_params = {
    "is_root": True,
    "name": "filinghistory",
    "table_name": "filinghistory",
    "error_table": "filinghistory_http_errors",
    "error_table_cols": ["id_item_queried", "error_json"],
    "empty_table": "filinghistory_empty",
    "empty_table_cols": ["id_item_queried", "empty_json"],
    "items_per_page": 100,
    "arrays": [{
        "name": "items",
        "table_name": "fh_items",
        "uid_key": ["company_number", "filing_serial_id"],
        "arrays": [{

            "name": "annotations",
            "table_name": "fh_items_annotations",
            "uid_key": ["company_number", "filing_serial_id",
                        "serial_id"],
            "drop": ["description_values", "data"]},

           {"name": "associated_filings",
            "table_name": "fh_items_associated_filings",
            "uid_key": ["company_number", "filing_serial_id",
                        "serial_id"],
            "drop": ["description_values", "data"]},

           {"name": "resolutions",
            "table_name": "fh_items_resolutions",
            "uid_key": ["company_number", "filing_serial_id",
                        "serial_id"],
            "drop": ["description_values", "data"]}],

        "drop": ["description_values"]}],
    "uid_key": ["company_number"],
    "drop": ["description_values", "data"]
}

chargelist_params = {
    "is_root": True,
    "name": "chargelist",
    "table_name": "chargelist",
    "error_table": "chargelist_http_errors",
    "empty_table": "chargelist_empty",
    "error_table_cols": ["id_item_queried", "error_json"],
    "empty_table_cols": ["id_item_queried", "empty_json"],
    "items_per_page": 100,
    "arrays": [{
        "name": "items",
        "table_name": "ch_items",
        "uid_key": ["company_number", "charge_serial_id"],
        "drop" : ["links"],
        "arrays": [
            {"name": "insolvency_cases",
             "table_name": "ch_items_insolvency_cases",
             "uid_key": ["company_number", "charge_serial_id", "serial_id"]},
            {"name": "persons_entitled",
             "table_name": "ch_items_persons_entitled",
             "uid_key": ["company_number", "charge_serial_id", "serial_id"]},
            {"name": "transactions",
             "table_name": "ch_items_transactions",
             "uid_key": ["company_number", "charge_serial_id", "serial_id"]}],
        "leaves": [{"name": "particulars",
                    "table_name": "ch_items_particulars"},
                   {"name": "scottish_alterations",
                    "table_name": "ch_items_scottish_alterations"}
                   ]
    }],
    "uid_key": ["company_number"]
}
