import requests
from requests.exceptions import HTTPError
from .auth import OAuth2Bearer

RETRY_ERROR_CODES = (
    requests.codes['conflict'],  # 409
    requests.codes['internal_server_error'],  # 500
    requests.codes['bad_gateway'],  # 502
    requests.codes['service_unavailable'],  # 503
    requests.codes['gateway_timeout']  # 504
)


def merge_or_create_key_value_for_dictionary(target, key, value=None):
    """
    This helper method will attempt to update a given key on a target dictionary with a value.
    If the value is empty, nothing is done.  If the key does not currently exist on the target,
    the key-value pair is created; otherwise, the given value is merged into the current key's
    value in the target (it's assumed an existing key is a dictionary).

    :param dictionary target: The dictionary to merge into
    :param str key: The key to merge or create on the target
    :param value: The value to merge into the dictionary key
    :type value: Dictionary or None
    """
    if value:
        if key in target:
            target.get(key).update(value)
        else:
            target.update({key: value})


def get(request_context, url, payload=None, **optional_request_params):
    """
    Shortcut for making a GET call to the API.  Data is passed as url params.
    """
    merge_or_create_key_value_for_dictionary(optional_request_params, 'params', payload)
    return call("GET", url, request_context, **optional_request_params)


def put(request_context, url, payload=None, **optional_request_params):
    """
    Shortcut for making a PUT call to the API
    """
    merge_or_create_key_value_for_dictionary(optional_request_params, 'data', payload)
    return call("PUT", url, request_context, **optional_request_params)


def post(request_context, url, payload=None, **optional_request_params):
    """
    Shortcut for making a POST call to the API
    """
    merge_or_create_key_value_for_dictionary(optional_request_params, 'data', payload)
    return call("POST", url, request_context, **optional_request_params)


def delete(request_context, url, payload=None, **optional_request_params):
    """
    Shortcut for making a DELETE call to the API
    """
    merge_or_create_key_value_for_dictionary(optional_request_params, 'data', payload)
    return call("DELETE", url, request_context, **optional_request_params)


def call(action, url, request_context, params=None, data=None, max_retries=None,
         auth_token=None, files=None, headers=None, cookies=None, timeout=None, proxies=None,
         verify=None, cert=None, allow_redirects=True):
    """This method servers as a pass-through to the requests library request functionality, but provides some configurable default
    values.  Constructs and sends a :class:`requests.Request <Request>`.
    Returns :class:`requests.Response <Response>` object.

    :param action: method for the new :class:`Request` object.
    :param url: Absolute url path to API method
    :param request_context: Instance of :class:`RequestContext` that holds a request session and other default values
    :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
    :param int max_retries: (optional) Number of times a request that generates a certain class of HTTP exception will be retried
        before being raised back to the caller.  See :py:mod:`client.base` for a list of those error types.
    :param files: (optional) Dictionary of 'name': file-like-objects (or {'name': ('filename', fileobj)}) for multipart encoding upload.
    :param dictionary headers: (optional) dictionary of headers to send for each request.  Will be merged with a default set of headers.
    :param cookies: (optional) Cookies to attach to each requests.
    :type cookies: dictionary or CookieJar
    :param str auth_token: (optional) OAuth2 token retrieved from a Canvas site
    :param float timeout: (optional) The timeout of the request in seconds.
    :param dictionary proxies: (optional) Mapping protocol to the URL of the proxy.
    :param verify: (optional) if ``True``, the SSL cert will be verified.  A CA_BUNDLE path can also be provided.
    :type verify: boolean or str
    :param cert: (optional) if String, path to ssl client cert file (.pem).  If Tuple, ('cert', 'key') pair.
    :type cert: str or Tuple
    :param bool allow_redirects: (optional) Set to True if POST/PUT/DELETE redirect following is allowed.  Defaults to True.
    """
    # This will be a requests.Session object with defaults set for context
    canvas_session = request_context.session
    retries = max_retries or request_context.max_retries  # Default back to value in request_context
    if retries is None:
        retries = 0  # Fall back in case max_retries in context was explicitly set to None
    # Set up an authentication callable using OAuth2Bearer if a token was passed in
    auth = None
    if auth_token:
        auth = OAuth2Bearer(auth_token)
    # try the request until max_retries is reached.  we need to account for the
    # fact that the first iteration through isn't a retry, so add 1 to max_retries
    for retry in range(retries + 1):
        try:
            # build and send the request
            response = canvas_session.request(
                action, url, params=params, data=data, headers=headers, cookies=cookies,
                files=files, auth=auth, timeout=timeout, proxies=proxies, verify=verify,
                cert=cert, allow_redirects=allow_redirects)

            # raise an http exception if one occured
            response.raise_for_status()

            # Otherwise, return raw response
            return response

        except HTTPError as http_error:
            # Need to check its an error code that can be retried
            status_code = http_error.response.status_code
            if status_code in RETRY_ERROR_CODES and retry < retries:
                # continue in a retry loop until max_retries
                continue
            # Otherwise, re-raise the exception
            raise