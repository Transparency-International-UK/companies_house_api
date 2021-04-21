#!/usr/bin/python3

from backoff import on_exception, expo
import requests
from requests import ConnectionError, Timeout, HTTPError, Response
from ratelimit import limits, sleep_and_retry
from typing import Union

from api_key_path_reader import API_KEY_ABS_PATH

KEY = open(API_KEY_ABS_PATH).read().strip()

FIVE_MINUTES = 300  # Number of seconds in five minutes.

CALLS = 500  # customise this to what CH gave as rate.
API_BASE_URL = "https://api.company-information.service.gov.uk"


# when limit imposed by @limits exceeded, @sleep_and_retry forces sleep and
# resumes as soon as possible.
@sleep_and_retry
@on_exception(expo, (ConnectionError, Timeout, HTTPError), max_tries=10)
@limits(calls=CALLS, period=FIVE_MINUTES)
def call_api(url: str, api_key: str) -> Union[dict, Response]:
	"""
	func to generate a query for an API with auth=(key, "").
	Decorators handle rate limit calls and exceptions.
	:param url: string, url of the query.
	:param api_key: string, apy_key.
	:return:
	if status_code is 200 func returns a JSON object.
	if status_code is http error func returns {"error":"error_string"}
	if status_code is not 200/404, re-run up to 10 times if exceptions in
	@on_exception tuple argument are raised.
	If 11th attempt fails, return None and print
	'API response: {}'.format(r.status_code).
	"""

	res = requests.get(url, auth=(api_key, ""))

	if not (res.status_code == 200
			or res.status_code == 404
			or res.status_code == 401
			or res.status_code == 400
	        or res.status_code == 500):  # add errors you want to catch here
		res.raise_for_status()  # all other errors will stop the program
	else:
		return res


def get_companyprofile(url_id: str, **kwargs) -> callable:
	"""
	func to extract companyprofile resource from the API with company number.
	:param url_id: uniquely identified code of the company.
	:param kwargs:
	needed to use factory Getter.extract(root_uid, start_index)
	although start_index not needed by get_companyprofile().
	:return:
	call_api(), with url formatted to search company whose code is "comp_code".
	"""
	url = API_BASE_URL + "/company/" + url_id
	print(f"Requesting companyprofile resource with url: \n{url}\n")

	return call_api(url=url, api_key=KEY)


def get_company_resource(url_id: str, res_type: str, items_per_page: int,
		start_index: int) -> callable:
	"""
	func to customise the API request for a given company, used to create other
	functions for all possible "res_type".
	:param start_index: index used by the url for the pagination.
	:param url_id: uniquely identified code of the company.
	:param res_type: resource type, can chose from:
					"officers"
					"filing-history"
					"insolvency"
					"charges"
					"persons-with-significant-control"
	:param items_per_page: max items per page to be returned
	:return: call_api(), with url formatted to search company whose code
	is root_uid and res_type is chosen from list.
	"""

	url = (API_BASE_URL + f"/company/{url_id}/"
						  f"{res_type}"
						  f"?items_per_page={items_per_page}"
						  f"&start_index={str(start_index)}")
	print(f"Requesting company resource type {res_type} with url: \n{url}\n")

	return call_api(url=url, api_key=KEY)


def get_appointmentlist(url_id: str, items_per_page: int,
		start_index: int) -> callable:
	"""
	func to query the API for appointmentList resource.
	:param items_per_page: max items per page to be returned.
	:param start_index: index used by the url for the pagination.
	:param url_id: needed to create url to get all appointments from API.
	:return: call_api(), with url formatted to search officers appointments.
	"""
	# what we are building to:
	# .../api.companieshouse.gov.uk/{root_uid}/?items_per_page=1&start_index=1
	# root_uid is: "/officers/LsKBd0tzif0mocK0gTSiK5WXmuA/appointments"

	url = (API_BASE_URL + f"/officers/{url_id}/appointments/?"
						  f"items_per_page={str(items_per_page)}"
						  f"&start_index={str(start_index)}")
	print(f"Requesting appointmentlist resource type with url: \n{url}\n")

	return call_api(url=url, api_key=KEY)


def get_officersearch(url_id: str, items_per_page: int,
		start_index: int) -> callable:
	"""
	func to get total results returned in the officerSearch resource.
	:param url_id: string for the officer search query.
	:param items_per_page: max items per page to be returned.
	:param start_index: index used by the url for the pagination.
	Be aware that if you try to extract more than the first 900 matches,
	you will get HTTP 416.
	:return: call_api with URL customised to search for a certain officer.
	"""
	url = (API_BASE_URL + f"/search/officers?"
						  f"q={url_id}"
						  f"&items_per_page={str(items_per_page)}"
						  f"&start_index={str(start_index)}")
	print(f"Requesting officersearch resource type with url: \n{url}\n")

	return call_api(url=url, api_key=KEY)
