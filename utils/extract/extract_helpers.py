from utils.extract.api_functions import get_companyprofile, get_company_resource
from utils.extract.api_functions import get_appointmentlist, get_officersearch
from functools import partial


def fill_error_template(error_hash, code):
    return {'errors': [{'error': error_hash.get(code, str(code))}]}


def curry_api_func(name, items_per_page):

    if name == "companyprofile":
        return get_companyprofile

    elif name == "officerlist":
        curried_f = partial(get_company_resource,
                            res_type="officers",
                            items_per_page=items_per_page)
        return curried_f

    elif name == "filinghistory":
        curried_f = partial(get_company_resource,
                            res_type="filing-history",
                            items_per_page=items_per_page)
        return curried_f

    # TODO do the params
    elif name == "companyinsolvency":
        curried_f = partial(get_company_resource,
                            res_type="insolvency",
                            items_per_page=items_per_page)
        return curried_f

    # TODO do the params
    elif name == "chargelist":
        curried_f = partial(get_company_resource,
                            res_type="charges",
                            items_per_page=items_per_page)
        return curried_f

    elif name == "psc":
        curried_f = partial(get_company_resource,
                            res_type="persons-with-significant-control",
                            items_per_page=items_per_page)
        return curried_f

    elif name == "appointmentlist":
        curried_f = partial(get_appointmentlist,
                            items_per_page=items_per_page)
        return curried_f

    # TODO consider dropping as anyways not very useful - search caped at 900
    elif name == "officersearch":
        curried_f = partial(get_officersearch,
                            items_per_page=items_per_page)
        return curried_f
