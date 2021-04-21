companyprofile_tables = """
CREATE TABLE IF NOT EXISTS companyprofile_http_errors (
id_item_queried VARCHAR (8) PRIMARY KEY,
error_json JSONB NOT NULL);

CREATE TABLE IF NOT EXISTS companyprofile (
company_name VARCHAR,
company_name_fp VARCHAR,
company_number VARCHAR (8) PRIMARY KEY,
can_file BOOLEAN,
company_status VARCHAR,
status VARCHAR, -- not mentioned in the CH docs.
company_status_detail VARCHAR,
date_of_cessation DATE,
date_of_dissolution DATE,
date_of_creation DATE,
etag VARCHAR,
external_registration_number VARCHAR,
has_been_liquidated BOOLEAN,
has_charges BOOLEAN,
has_super_secure_pscs BOOLEAN,
has_insolvency_history BOOLEAN,
is_community_interest_company VARCHAR,
jurisdiction VARCHAR, 
last_full_members_list_date VARCHAR,
partial_data_available VARCHAR,
registered_office_is_in_dispute BOOLEAN,
subtype VARCHAR,
type VARCHAR,
undeliverable_registered_office_address BOOLEAN);

-- companyprofile BCNF decompositions "links", 
--                                    "registered_office_address", 
--                                    "accounts", "annual_return",
--                                    "foreign_company_details", 
--                                    "branch_company_details", 
--                                    "confirmation_statement".

CREATE TABLE IF NOT EXISTS cp_links (
company_number VARCHAR (8) PRIMARY KEY REFERENCES companyprofile(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
charges VARCHAR,
overseas VARCHAR, -- not mentioned in the CH docs.
exemptions VARCHAR,  -- not mentioned in the CH docs.
filing_history VARCHAR,
insolvency VARCHAR,
officers VARCHAR,
persons_with_significant_control VARCHAR,
persons_with_significant_control_statements VARCHAR,
registers VARCHAR,
self VARCHAR,
uk_establishments VARCHAR); -- not mentioned in the CH docs.

CREATE TABLE IF NOT EXISTS cp_registered_office_address (
company_number VARCHAR (8) PRIMARY KEY REFERENCES companyprofile(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
address_line_1 VARCHAR,
address_line_2 VARCHAR,
care_of VARCHAR,
country VARCHAR,
country_iso VARCHAR,
locality VARCHAR,
locality_clean VARCHAR,
po_box VARCHAR,
postal_code VARCHAR,
postal_code_clean VARCHAR,
address_premises VARCHAR,
region VARCHAR);

CREATE TABLE IF NOT EXISTS cp_accounts (
company_number VARCHAR (8) PRIMARY KEY 
REFERENCES companyprofile(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
accounting_reference_date_day INTEGER,
accounting_reference_date_month INTEGER, 
last_accounts_made_up_to DATE,
last_accounts_period_end_on DATE,
last_accounts_period_start_on DATE,
last_accounts_type VARCHAR, 
next_accounts_due_on DATE,
next_accounts_overdue BOOLEAN,
next_accounts_period_start_on DATE,
next_due DATE,
next_made_up_to DATE, 
next_accounts_period_end_on DATE,
overdue BOOLEAN);

CREATE TABLE IF NOT EXISTS cp_annual_return (
company_number VARCHAR (8) PRIMARY KEY 
REFERENCES companyprofile(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
last_made_up_to DATE,
next_due DATE,
next_made_up_to DATE,
overdue BOOLEAN);

CREATE TABLE IF NOT EXISTS cp_foreign_company_details (
company_number VARCHAR (8) PRIMARY KEY 
REFERENCES companyprofile(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
accounting_requirement_foreign_account_type VARCHAR,
accounting_requirement_terms_of_account_publication VARCHAR,
accounts_account_period_from_day INTEGER,
accounts_account_period_from_month INTEGER,
accounts_account_period_to_day INTEGER,
accounts_account_period_to_month INTEGER,
accounts_must_file_within_months INTEGER,
business_activity VARCHAR,
company_type VARCHAR,
governed_by VARCHAR,
is_a_credit_finance_institution BOOLEAN,
is_a_credit_financial_institution BOOLEAN, -- not  mentioned in the CH docs.
legal_form VARCHAR, -- not mentioned in the CH docs.
originating_registry_country VARCHAR,
originating_registry_country_iso VARCHAR,
originating_registry_name VARCHAR,
registration_number VARCHAR);

CREATE TABLE IF NOT EXISTS cp_branch_company_details(
company_number VARCHAR (8) PRIMARY KEY 
REFERENCES companyprofile(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
business_activity VARCHAR,
parent_company_name VARCHAR, 
parent_company_name_fp VARCHAR,
parent_company_number VARCHAR); 

CREATE TABLE IF NOT EXISTS cp_confirmation_statement(
company_number VARCHAR (8) PRIMARY KEY 
REFERENCES companyprofile(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
last_made_up_to DATE,
next_due DATE,
next_made_up_to DATE,
overdue BOOLEAN);

-- companyprofile 4NF decompositions "previous_company_names", 
--                                   "sic_codes".

CREATE TABLE IF NOT EXISTS cp_previous_company_names(
serial_id SERIAL,
PRIMARY KEY (company_number, serial_id),
company_number VARCHAR (8) REFERENCES companyprofile(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
ceased_on DATE,
effective_from DATE,
name VARCHAR);

CREATE TABLE IF NOT EXISTS cp_sic_codes(
serial_id SERIAL,
PRIMARY KEY (company_number, serial_id),
company_number VARCHAR (8) REFERENCES companyprofile(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
sic_codes VARCHAR);"""

psc_tables = """
CREATE TABLE IF NOT EXISTS psc_http_errors (
id_item_queried VARCHAR (8) PRIMARY KEY,
error_json JSONB NOT NULL);

CREATE TABLE IF NOT EXISTS psc_empty(
id_item_queried VARCHAR (8) PRIMARY KEY,
empty_json JSONB NOT NULL);

CREATE TABLE IF NOT EXISTS psc(
company_number VARCHAR (8) PRIMARY KEY,
active_count INTEGER,
ceased_count INTEGER,
etag VARCHAR,
items_per_page INTEGER,
kind VARCHAR,
links_persons_with_significant_control_statements_list VARCHAR,
links_persons_with_significant_control_statements VARCHAR, -- not mentioned in the CH docs.
links_self VARCHAR,
links_exemptions VARCHAR, -- not mentioned in the CH docs.
start_index INTEGER,
total_results INTEGER);

-- psc 4NF decomposition ("items").

CREATE TABLE IF NOT EXISTS psc_items(
company_number VARCHAR (8) REFERENCES psc(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE, 
psc_serial_id SERIAL,
PRIMARY KEY (company_number, psc_serial_id),
ceased_on DATE,
country_of_residence VARCHAR,
country_of_residence_iso VARCHAR,
date_of_birth_day INTEGER,
date_of_birth_month INTEGER,
date_of_birth_year INTEGER,
etag VARCHAR,
kind VARCHAR, -- not mentioned in the CH docs.
links_self VARCHAR,
description VARCHAR,
links_statement VARCHAR,
name VARCHAR,
-- nationality VARCHAR, -- dropped
notified_on DATE);

-- psc[items] BCNF decompositions "address",  
--                                "identification", 
--                                "name_elements".

CREATE TABLE IF NOT EXISTS psc_items_address(
company_number VARCHAR (8), 
psc_serial_id INT, 
PRIMARY KEY (psc_serial_id, company_number),
FOREIGN KEY (psc_serial_id, company_number) 
REFERENCES psc_items(psc_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
address_line_1 VARCHAR,
address_line_2 VARCHAR,
care_of VARCHAR,
country VARCHAR,
country_iso VARCHAR,
locality VARCHAR,
locality_clean VARCHAR,
po_box VARCHAR,
postal_code VARCHAR,
postal_code_clean VARCHAR,
premises VARCHAR,
region VARCHAR);

CREATE TABLE IF NOT EXISTS psc_items_identification(
company_number VARCHAR (8), 
psc_serial_id INT, 
PRIMARY KEY (psc_serial_id, company_number),
FOREIGN KEY (psc_serial_id, company_number) 
REFERENCES psc_items(psc_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
legal_authority VARCHAR, -- not mentioned in the CH docs.
legal_authority_clean VARCHAR,
registration_number VARCHAR, -- not mentioned in the CH docs.
legal_form VARCHAR, -- not mentioned in the CH docs.
place_registered VARCHAR, -- not mentioned in the CH docs.
place_registered_clean VARCHAR,
country_registered VARCHAR, -- not mentioned in the CH docs.
country_registered_iso VARCHAR);

CREATE TABLE IF NOT EXISTS psc_items_name_elements(
company_number VARCHAR (8), 
psc_serial_id INT, 
PRIMARY KEY (psc_serial_id, company_number),
FOREIGN KEY (psc_serial_id, company_number) 
REFERENCES psc_items(psc_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
forename VARCHAR,
middle_name VARCHAR,
other_forenames VARCHAR,
surname VARCHAR,
title VARCHAR);

-- psc[items] 4NF decompositions "natures_of_control", 
--                               "nationality_list_iso".

CREATE TABLE IF NOT EXISTS psc_items_natures_of_control(
serial_id SERIAL,
company_number VARCHAR (8), 
psc_serial_id INT, 
PRIMARY KEY (serial_id, psc_serial_id, company_number),
FOREIGN KEY (psc_serial_id, company_number) 
REFERENCES psc_items(psc_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
natures_of_control VARCHAR);

CREATE TABLE IF NOT EXISTS psc_items_nationalities(
serial_id SERIAL,
company_number VARCHAR (8),
psc_serial_id INTEGER,
nationality_list_iso VARCHAR,
PRIMARY KEY (serial_id, psc_serial_id, company_number),
FOREIGN KEY (psc_serial_id, company_number) 
REFERENCES psc_items(psc_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE
);
"""

officerlist_tables = """
CREATE TABLE IF NOT EXISTS officerlist_http_errors (
id_item_queried VARCHAR (8) PRIMARY KEY,
error_json JSONB NOT NULL);

CREATE TABLE IF NOT EXISTS officerlist_empty (
id_item_queried VARCHAR (8) PRIMARY KEY,
empty_json JSONB NOT NULL);

CREATE TABLE IF NOT EXISTS officerlist (
company_number VARCHAR (8) PRIMARY KEY, 
etag VARCHAR,
links_self VARCHAR,
active_count INTEGER ,
inactive_count INTEGER, 
items_per_page INTEGER,
kind VARCHAR NOT NULL,
resigned_count INTEGER,
start_index VARCHAR,
total_results INTEGER);

-- officerlist 4NF decompositions "items".

CREATE TABLE IF NOT EXISTS ol_items (
company_number VARCHAR (8) REFERENCES officerlist(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE, 
officer_serial_id SERIAL, 
PRIMARY KEY (officer_serial_id, company_number), 
appointed_on DATE,
country_of_residence VARCHAR,
country_of_residence_iso VARCHAR,
date_of_birth_day INTEGER,
date_of_birth_month INTEGER,
date_of_birth_year INTEGER,
links_officer_appointments VARCHAR,
links_self VARCHAR,
name VARCHAR,
-- nationality VARCHAR,  -- dropped
occupation VARCHAR,
officer_role VARCHAR,
resigned_on DATE);

-- officerlist["items"] BCNF decompositions "address", 
--                                          "identification".

CREATE TABLE IF NOT EXISTS ol_items_address (
company_number VARCHAR (8), 
officer_serial_id INTEGER,
PRIMARY KEY (officer_serial_id, company_number), 
FOREIGN KEY (officer_serial_id, company_number)
REFERENCES ol_items (officer_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
address_line_1 VARCHAR, 
address_line_2 VARCHAR,
care_of VARCHAR,
country VARCHAR, 
country_iso VARCHAR,
locality VARCHAR,
locality_clean VARCHAR,
po_box VARCHAR,
postal_code VARCHAR,
postal_code_clean VARCHAR,
premises VARCHAR,
region VARCHAR);

CREATE TABLE IF NOT EXISTS ol_items_identification (
company_number VARCHAR (8),
officer_serial_id INTEGER,
PRIMARY KEY (officer_serial_id, company_number), 
FOREIGN KEY (officer_serial_id, company_number)
REFERENCES ol_items (officer_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
identification_type VARCHAR,
legal_authority VARCHAR,
legal_authority_clean VARCHAR,
legal_form VARCHAR,
place_registered VARCHAR,
place_registered_clean VARCHAR,
registration_number VARCHAR);

-- officerlist["items"] 4NF decompositions "former_names", 
--                                         "nationality_list_iso".

CREATE TABLE IF NOT EXISTS ol_items_former_names(
serial_id SERIAL,
PRIMARY KEY (serial_id, officer_serial_id, company_number),
company_number VARCHAR (8),
officer_serial_id INTEGER,
FOREIGN KEY (officer_serial_id, company_number)
REFERENCES ol_items(officer_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
forenames VARCHAR, 
surname VARCHAR);

CREATE TABLE IF NOT EXISTS ol_items_nationalities(
serial_id SERIAL,
company_number VARCHAR (8),
officer_serial_id INTEGER,
nationality_list_iso VARCHAR,
PRIMARY KEY (serial_id, officer_serial_id, company_number),
FOREIGN KEY (officer_serial_id, company_number) 
REFERENCES ol_items(officer_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE
);
"""

appointmentlist_tables = """
CREATE TABLE IF NOT EXISTS appointmentlist_http_errors (
id_item_queried VARCHAR PRIMARY KEY,
error_json JSONB NOT NULL);

CREATE TABLE IF NOT EXISTS appointmentlist(
appointmentlist_url_id VARCHAR PRIMARY KEY,  -- same as links_self, renamed for clarity. 
links_self VARCHAR,  
date_of_birth_month INTEGER,
date_of_birth_year INTEGER,
etag VARCHAR,
is_corporate_officer BOOLEAN,
items_per_page INTEGER,
kind VARCHAR,
name VARCHAR,
start_index INTEGER,
total_results INTEGER);

-- appointmentlist 4NF decompositions "items".

CREATE TABLE IF NOT EXISTS al_items(
appointmentlist_url_id VARCHAR,
appointment_serial_id SERIAL,
FOREIGN KEY (appointmentlist_url_id) 
REFERENCES appointmentlist(appointmentlist_url_id) 
ON DELETE CASCADE ON UPDATE CASCADE,
PRIMARY KEY (appointment_serial_id, appointmentlist_url_id), 
appointed_before DATE,
appointed_on DATE,
appointed_to_company_name VARCHAR,
appointed_to_company_name_fp VARCHAR,
appointed_to_company_number VARCHAR,
appointed_to_company_status VARCHAR,
country_of_residence VARCHAR,
country_of_residence_iso VARCHAR,
is_pre_1992_appointment BOOLEAN,
links_company VARCHAR,
name VARCHAR,
-- nationality VARCHAR,  -- dropped
occupation VARCHAR,
officer_role VARCHAR,
resigned_on DATE);

-- appointmentlist["items"] BCNF decompositions "address", 
--                                              "identification", 
--                                              "name_elements".

CREATE TABLE IF NOT EXISTS al_items_address(
appointmentlist_url_id VARCHAR,
appointment_serial_id INTEGER,
FOREIGN KEY (appointment_serial_id, appointmentlist_url_id) 
REFERENCES al_items(appointment_serial_id, appointmentlist_url_id) 
ON DELETE CASCADE ON UPDATE CASCADE,
PRIMARY KEY (appointment_serial_id, appointmentlist_url_id),
address_line_1 VARCHAR,
address_line_2 VARCHAR,
care_of VARCHAR,
country VARCHAR,
country_iso VARCHAR,
locality VARCHAR,
locality_clean VARCHAR,
po_box VARCHAR,
postal_code VARCHAR,
postal_code_clean VARCHAR,
premises VARCHAR,
region VARCHAR);

CREATE TABLE IF NOT EXISTS al_items_identification(
appointmentlist_url_id VARCHAR,
appointment_serial_id INTEGER,
FOREIGN KEY (appointment_serial_id, appointmentlist_url_id) 
REFERENCES al_items(appointment_serial_id, appointmentlist_url_id) 
ON DELETE CASCADE ON UPDATE CASCADE,
PRIMARY KEY (appointment_serial_id, appointmentlist_url_id),
identification_type VARCHAR,
legal_authority VARCHAR,
legal_authority_clean VARCHAR,
legal_form VARCHAR,
place_registered VARCHAR,
place_registered_clean VARCHAR,
registration_number VARCHAR);

CREATE TABLE IF NOT EXISTS al_items_name_elements(
appointmentlist_url_id VARCHAR,
appointment_serial_id INTEGER,
FOREIGN KEY (appointment_serial_id, appointmentlist_url_id) 
REFERENCES al_items(appointment_serial_id, appointmentlist_url_id) 
ON DELETE CASCADE ON UPDATE CASCADE,
PRIMARY KEY (appointment_serial_id, appointmentlist_url_id),
forename VARCHAR,
honours VARCHAR,
other_forenames VARCHAR,
surname VARCHAR,
title VARCHAR);

-- appointmentlist["items"] 4NF decompositions "former_names", 
--                                             "nationalities"

CREATE TABLE IF NOT EXISTS al_items_former_names(
serial_id SERIAL,
PRIMARY KEY (appointment_serial_id, appointmentlist_url_id),
appointmentlist_url_id VARCHAR,
appointment_serial_id INTEGER,
FOREIGN KEY (appointment_serial_id, appointmentlist_url_id) 
REFERENCES al_items(appointment_serial_id, appointmentlist_url_id) 
ON DELETE CASCADE ON UPDATE CASCADE,
forenames VARCHAR,
surname VARCHAR);

CREATE TABLE IF NOT EXISTS al_items_nationalities(
serial_id SERIAL,
appointmentlist_url_id VARCHAR,
appointment_serial_id INTEGER,
nationality_list_iso VARCHAR,
PRIMARY KEY (serial_id, appointment_serial_id, appointmentlist_url_id),
FOREIGN KEY (appointment_serial_id, appointmentlist_url_id) 
REFERENCES al_items(appointment_serial_id, appointmentlist_url_id) 
ON DELETE CASCADE ON UPDATE CASCADE
);
"""

filinghistory_tables = """
CREATE TABLE IF NOT EXISTS filinghistory_http_errors (
id_item_queried VARCHAR PRIMARY KEY,
error_json JSONB NOT NULL);

CREATE TABLE IF NOT EXISTS filinghistory_empty(
id_item_queried VARCHAR PRIMARY KEY,
empty_json JSONB NOT NULL);


CREATE TABLE IF NOT EXISTS filinghistory(
company_number VARCHAR (8) PRIMARY KEY,
filing_history_status VARCHAR,
etag VARCHAR,
items_per_page INTEGER,
kind VARCHAR,
start_index INTEGER,
total_count INTEGER
);

-- psc 4NF decomposition ("items").

CREATE TABLE IF NOT EXISTS fh_items(
company_number VARCHAR (8) REFERENCES filinghistory(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE, 
filing_serial_id SERIAL,
PRIMARY KEY (filing_serial_id, company_number),
barcode VARCHAR,
category VARCHAR,
date DATE,
action_date DATE,  -- not mentioned in the docs.
description VARCHAR,
description_values_json JSONB,
data_json JSONB,
links_document_metadata VARCHAR,
links_self VARCHAR, 
pages INTEGER, 
paper_filed BOOLEAN, 
subcategory VARCHAR, 
transaction_id VARCHAR,
type VARCHAR
);

-- filinghistory["items"] 4NF decompositions "annotations", 
--                                           "associated_filings", 
--                                           "resolutions".

CREATE TABLE IF NOT EXISTS fh_items_annotations(
company_number VARCHAR (8),
filing_serial_id INTEGER,
serial_id SERIAL,
PRIMARY KEY (serial_id, filing_serial_id, company_number),
FOREIGN KEY (filing_serial_id, company_number) 
REFERENCES fh_items(filing_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE, 
annotation VARCHAR,
description_values_json JSONB,
data_json JSONB,
category VARCHAR,
date DATE,
type VARCHAR,
action_date DATE,  -- not mentioned in the docs.
description VARCHAR);

CREATE TABLE IF NOT EXISTS fh_items_associated_filings(
company_number VARCHAR (8),
filing_serial_id INTEGER,
serial_id SERIAL,
PRIMARY KEY (serial_id, filing_serial_id, company_number),
FOREIGN KEY (filing_serial_id, company_number) 
REFERENCES fh_items(filing_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE, 
category VARCHAR,
subcategory VARCHAR,
"matched-default" VARCHAR,  -- smart cookie in CH decided to use double quotes.
description_values_json JSONB,
data_json JSONB,
date VARCHAR,
type VARCHAR,
action_date BIGINT,  -- not mentioned in the docs, and is 13-digit unix epoch
description VARCHAR);

CREATE TABLE IF NOT EXISTS fh_items_resolutions(
company_number VARCHAR (8),
filing_serial_id INTEGER,
serial_id SERIAL,
PRIMARY KEY (serial_id, filing_serial_id, company_number),
FOREIGN KEY (filing_serial_id, company_number) 
REFERENCES fh_items(filing_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE, 
category VARCHAR,
date VARCHAR, 
barcode VARCHAR,
parent_form_type VARCHAR,
description_values_json JSONB,
data_json JSONB,
original_description VARCHAR,
description VARCHAR,
document_id VARCHAR, 
receive_date DATE, 
subcategory VARCHAR, 
type VARCHAR);
"""

chargelist_tables = """
CREATE TABLE IF NOT EXISTS chargelist_http_errors (
id_item_queried VARCHAR (8) PRIMARY KEY,
error_json JSONB NOT NULL);

CREATE TABLE IF NOT EXISTS chargelist_empty (
id_item_queried VARCHAR (8) PRIMARY KEY,
empty_json JSONB NOT NULL);

CREATE TABLE IF NOT EXISTS chargelist (
company_number VARCHAR (8) PRIMARY KEY, 
etag VARCHAR,
total_count INTEGER,
unfiltered_count INTEGER, 
part_satisfied_count INTEGER,
satisfied_count INTEGER);

-- chargelist 4NF decompositions "items".

CREATE TABLE IF NOT EXISTS ch_items (
company_number VARCHAR REFERENCES  chargelist(company_number) 
ON DELETE CASCADE ON UPDATE CASCADE, 
charge_serial_id SERIAL, 
PRIMARY KEY (charge_serial_id, company_number), 
acquired_on DATE,
assets_ceased_released VARCHAR,
charge_code VARCHAR,
charge_number INTEGER,
covering_instrument_date DATE,
created_on DATE,
delivered_on DATE,
etag VARCHAR,
id VARCHAR,
links_self VARCHAR,  
more_than_four_persons_entitled BOOLEAN,
resolved_on DATE,
satisfied_on DATE,
status VARCHAR,
classification_description VARCHAR,
classification_type VARCHAR,
secured_details_description VARCHAR,
secured_details_type VARCHAR
);

-- chargelist["items"] BCNF decompositions "particulars".

CREATE TABLE IF NOT EXISTS ch_items_particulars(
charge_serial_id INTEGER,
company_number VARCHAR (8) NOT NULL,
PRIMARY KEY (charge_serial_id, company_number),
FOREIGN KEY (charge_serial_id, company_number) 
REFERENCES ch_items(charge_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
chargor_acting_as_bare_trustee BOOLEAN,
contains_fixed_charge BOOLEAN,
contains_floating_charge BOOLEAN,
contains_negative_pledge BOOLEAN,
floating_charge_covers_all BOOLEAN,
type VARCHAR,
description VARCHAR);

CREATE TABLE IF NOT EXISTS ch_items_scottish_alterations(
charge_serial_id INTEGER,
company_number VARCHAR (8) NOT NULL,
PRIMARY KEY (charge_serial_id, company_number),
FOREIGN KEY (charge_serial_id, company_number) 
REFERENCES ch_items(charge_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
description VARCHAR,
has_alterations_to_order BOOLEAN,
has_alterations_to_prohibitions BOOLEAN,
has_alterations_to_provisions BOOLEAN,
has_restricting_provisions BOOLEAN,
type VARCHAR);

-- chargelist["items"] 4NF decompositions "insolvency_cases", 
--                                        "persons_entitled", 
--                                        "transactions".

CREATE TABLE IF NOT EXISTS ch_items_insolvency_cases(
serial_id SERIAL, 
charge_serial_id INTEGER,
company_number VARCHAR (8) NOT NULL,
PRIMARY KEY (serial_id, charge_serial_id, company_number),
FOREIGN KEY (charge_serial_id, company_number) 
REFERENCES ch_items(charge_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
case_number INTEGER,
transaction_id INTEGER
);

CREATE TABLE IF NOT EXISTS ch_items_persons_entitled(
serial_id SERIAL, 
charge_serial_id INTEGER,
company_number VARCHAR (8) NOT NULL,
PRIMARY KEY (serial_id, charge_serial_id, company_number),
FOREIGN KEY (charge_serial_id, company_number) 
REFERENCES ch_items(charge_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
name VARCHAR);

CREATE TABLE IF NOT EXISTS ch_items_transactions(
serial_id SERIAL, 
charge_serial_id INTEGER,
company_number VARCHAR (8) NOT NULL,
PRIMARY KEY (serial_id, charge_serial_id, company_number),
FOREIGN KEY (charge_serial_id, company_number) 
REFERENCES ch_items(charge_serial_id, company_number) 
ON DELETE CASCADE ON UPDATE CASCADE,
links_filing VARCHAR,
delivered_on DATE,
filing_type VARCHAR,
insolvency_case_number INTEGER,
transaction_id INTEGER);
"""