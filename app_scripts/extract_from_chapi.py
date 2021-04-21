from utils.extract.extract_helpers import curry_api_func
from utils.extract.extract_helpers import fill_error_template

# Some of CH error jsons are empty -> cannot check for error keys.
# Use statuses to detect and create the error jsons when empty.
WRONG_STATUSES = [400, 401, 404, 416, 500]  # add error code here to catch them
ERROR_HASH = {400: "bad request",
              401: "not authorized",
              404: "not found",
              416: "range not satisfiable",
              500: "internal Server Error"}


def res_is_not_illegal(res):

    # the API returned illegal response statuses
    if res.status_code in WRONG_STATUSES:
        return False

    res_dict = res.json()

    # The API may return error jsons with non error response statuses
    if "error" in res_dict or "errors" in res_dict:
        return False

    # finally the API may just keep returning jsons with empty arrays when
    # a request is out of index (you request a page that doesn't exist).
    # careful -> bool([]) is false, so negate it to check if jsons has empty []
    dict_contains_empty_array = lambda d: not (d.get("items", []))
    if dict_contains_empty_array(res_dict):
        return False
    # otherwise return True and continue paginating
    return True


def query_api(json_params, url_id):

    json_name = json_params["name"]
    items_per_page = json_params.get("items_per_page", 0)
    api_curried_func = curry_api_func(json_params["name"],
                                      items_per_page)

    if json_name == "companyprofile":
        res = api_curried_func(start_index=None, url_id=url_id)
        yield res.json()

    else:

        start_index = 0
        res = api_curried_func(start_index=start_index, url_id=url_id)
        res_dict = res.json()

        # if request successful, this yields first page.
        # if request unsuccessful, this yields error json.

        if not res_dict:  # some error jsons are completely empty.
            yield fill_error_template(ERROR_HASH, res.status_code)
        else:
            yield res_dict

        while res_is_not_illegal(res):
            # paginate until error occurs, then yield.
            start_index += items_per_page
            res = api_curried_func(start_index=start_index, url_id=url_id)
            if not res.json():
                yield fill_error_template(ERROR_HASH, res.status_code)
            else:
                yield res.json()

    return


if __name__ == "__main__":

    from configs.chapi_json_params import companyprofile_params, psc_params
    from configs.chapi_json_params import appointmentlist_params, officerlist_params

    OFFICER_ID = "FVzeHfaxEHWP31pW1BIDeqWX8bs"
    COMPANY_NUMBER = "09825890"

    # etag of the companyProfile resource
    CP_ETAG = "9f6992bff81672ca17a232db49eff90d2044d7b3"
    AL_ETAG = "f17c7f12aac13901277305231cfcfc0960815992"
    OL_ETAG = "1fa8efffdf5f9d3cc5ac445bab874cd80e592b09"

    # links.self of psc list
    LINKS_SELF_PSC = "/company/09825890/persons-with-significant-control"
    PSC_COUNT = 3

    # test companyProfile resource
    cp_iter = query_api(companyprofile_params, COMPANY_NUMBER)
    cp = list(cp_iter)
    cp_etag = cp[0].get("etag")
    assert cp_etag == CP_ETAG, "Wrong companyProfile query result."

    # test officerList resource
    ol_iter = query_api(officerlist_params, COMPANY_NUMBER)
    ol = list(ol_iter)
    ol_etag = ol[0].get("etag")
    assert ol_etag == OL_ETAG, "Wrong officerList query result."

    # test psc list resource
    psc_iter = query_api(psc_params, COMPANY_NUMBER)
    psc = list(psc_iter)
    links_self_psc = psc[0].get("links").get("self")
    psc_count = len(psc[0].get("items"))
    assert links_self_psc == LINKS_SELF_PSC, "Wrong psc list query result."
    assert psc_count == PSC_COUNT, "Wrong number of psc list query result."

    al_iter = query_api(appointmentlist_params, OFFICER_ID)
    al = list(al_iter)
    al_etag = al[0].get("etag")
    assert al_etag == AL_ETAG, "Wrong appointmentList query result."


