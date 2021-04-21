company_flags = "--cp --ol --psc --fh --ch"

url_ids_examples = (
    "Example of url id for appointmentlist resource: \n"
    "FVzeHfaxEHWP31pW1BIDeqWX8bs\n"
    "Example of root_uid for " + company_flags + " :"
    "OC399321\n\n")


flags_clash_text = ("The --al flag and all other flags are mutually "
                   "exclusive. You can either pass the --al flag, or all "
                   f"others: {company_flags}\n"
                   "This is because the url for the appointmentslist "
                   "resource is different from the url required by "
                   "any other company resouce.\n\n"
                   + url_ids_examples)

wrong_url_id_text = ("It looks like you have provided a file with url ids not "
                     "suitable for the json you want to extract.\n"
                     f"Company codes must be used with {company_flags} flags"
                     "Officer ids with the --al flag.\n\n"
                     + url_ids_examples)
