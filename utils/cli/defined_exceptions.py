from utils.cli.defined_exceptions_messages import flags_clash_text
from utils.cli.defined_exceptions_messages import wrong_url_id_text


class BaseValidationError(ValueError):
    pass


class FlagsCollide(BaseValidationError):
    pass


class WrongUrlIdPassed(BaseValidationError):
    pass


def file_is_csv_or_txt(args):
    if args.file.endswith(("csv", "txt")):
        return True


def file_contains_company_codes(url_ids):
    if len(list(url_ids)[0]) == 8:
        return True
    return False


def raise_if_flags_clash(args):

    # bool(file) + bool(al) = 2
    if (args.al is True

        # more flags than there should be
        and (sum([bool(value) for value in vars(args).values()]) > 2)):

        raise FlagsCollide(flags_clash_text)


def print_file_head(url_ids):
    return ("Here's the top 5 ids were read from the file.\n\n"
            + " \n".join(url_ids[:5] if len(url_ids) > 5 else url_ids))


def run_file_check(args, url_ids):

    if (args.al is True
        and file_contains_company_codes(url_ids)
       or
       ((any([args.psc, args.cp, args.ol, args.fh, args.ch])
        and
        not file_contains_company_codes(url_ids)))):

        raise WrongUrlIdPassed(wrong_url_id_text
                               + print_file_head(url_ids=url_ids))
