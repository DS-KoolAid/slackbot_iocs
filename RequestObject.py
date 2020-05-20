
from . import ErrorCodes


class RequestObject(object):
    """ """
    def __init__(self):
        """ """
        self._body = None
        self._content_type = None
        self._description = None
        self._headers = {
            # 'charset': 'UTF-8',
            # 'Connection': 'keep-alive',
            # Breaks API Connection 'Transfer-Encoding': 'chunked',
            # 'Content-Type': 'application/json',
            # 'Content-Length': 0,
        }
        self._http_method = 'GET'
        self._owner = None
        self._owner_allowed = True
        self._payload = {
            'createActivityLog': 'false'
        }
        self._path_url = None
        self._remaining_results = 1
        self._request_uri = None
        self._resource_pagination = True
        self._resource_type = None
        self._result_limit = 0
        self._result_start = 0
        self._stream = False
        self._track = False
        self._failure_callback = None
        self._success_callback = None

    # unicode
    @staticmethod
    def _uni(data):
        """ """
        if data is None or isinstance(data, (int, list, dict)):
            return data
        elif isinstance(data, str):
            return str(data.encode('utf-8').strip(), errors='ignore')  # re-encode poorly encoded unicode
        elif not isinstance(data, str):
            return str(data, 'utf-8', errors='ignore')
        else:
            return data

    def add_payload(self, key, val):
        """ add a key value pair to payload """
        self._payload[key] = str(self._uni(val))

    def empty_payload(self):
        self._payload = {}

    def add_header(self, key, val):
        """ add a key value pair to header """
        self._headers[key] = str(self._uni(val))

    def enable_activity_log(self):
        """ enable the TC activity log """
        self.add_payload('createActivityLog', 'true')

    def enable_track(self):
        """ the path url to include in the hmac headers """
        self._track = True

    def set_body(self, data):
        """ set the POST/PUT body content """
        self._body = data
        self.add_header('Content-Length', len(self._body))

    def set_content_type(self, data):
        """ allow manual setting of content type """
        self._content_type = self._uni(data)
        self.add_header('Content-Type', data)

    def set_description(self, data):
        """ a description of the request """
        self._description = self._uni(data)

    def set_http_method(self, data):
        """ set the http method """
        data = data.upper()
        if data in ['DELETE', 'GET', 'POST', 'PUT']:
            self._http_method = data

            # set content type for commit methods
            if self._content_type is None and data in ['POST', 'PUT']:
                self.add_header('Content-Type', 'application/json')
        else:
            raise AttributeError(ErrorCodes.e6000.value.format(data))

    def set_modified_since(self, data):
        """ set modified since for indicator requests """
        self.add_payload('modifiedSince', data)

    def set_owner(self, data):
        """ set the owner in the payload and also used for victims """
        self._owner = self._uni(data)
        self.add_payload('owner', data)

    def set_owner_allowed(self, data):
        """ indicate if this request supports owners """
        self._owner_allowed = self._uni(data)

    def set_path_url(self, data):
        """ the path url to include in the hmac headers """
        self._path_url = self._uni(data)

    def set_remaining_results(self, data):
        """ count of remaining results for pagination """
        self._remaining_results = self._uni(data)

    def set_request_uri(self, uri_template, values=None):
        """ set the uri for the request """
        if values is None:
            self._request_uri = uri_template
        else:
            self._request_uri = uri_template.format(*values)

    def set_resource_pagination(self, data):
        """ indicate if this reqeust support pagination """
        self._resource_pagination = self._uni(data)

    def set_resource_type(self, data_enum):
        """ set the resource type for this request """
        self._resource_type = data_enum

    def set_result_limit(self, data):
        """ per query result limit (500 max) """
        self.add_payload('resultLimit', data)
        self._result_limit = self._uni(data)

    def set_result_start(self, data):
        """ position to start retrieving results """
        self.add_payload('resultStart', data)
        self._result_start = self._uni(data)

    def set_failure_callback(self, callback):
        self._failure_callback = callback

    def set_stream(self, stream):
        if isinstance(stream, bool):
            self._stream = stream

    def set_success_callback(self, callback):
        """ position to start retrieving results """
        self._success_callback = callback

    @property
    def body(self):
        """ """
        return self._body

    @property
    def content_type(self):
        """ """
        return self._content_type

    @property
    def description(self):
        """ """
        return self._description

    @property
    def headers(self):
        """ """
        return self._headers

    @property
    def http_method(self):
        """ """
        return self._http_method

    @property
    def owner(self):
        """ required for victims since they don't store owner """
        return self._owner

    @property
    def owner_allowed(self):
        """ """
        return self._owner_allowed

    @property
    def path_url(self):
        """ """
        return self._path_url

    @property
    def payload(self):
        """ """
        return self._payload

    @property
    def remaining_results(self):
        """ """
        return self._remaining_results

    @property
    def request_uri(self):
        """ """
        return self._request_uri

    @property
    def resource_pagination(self):
        """ """
        return self._resource_pagination

    @property
    def resource_type(self):
        """ """
        return self._resource_type

    @property
    def result_limit(self):
        """ """
        return self._result_limit

    @property
    def result_start(self):
        """ """
        return self._result_start

    @property
    def track(self):
        """ """
        return self._track

    @property
    def failure_callback(self):
        """ """
        return self._failure_callback

    @property
    def stream(self):
        """ """
        return self._stream

    @property
    def success_callback(self):
        """ """
        return self._success_callback

    def __str__(self):
        """ """
        printable_string = '\n{0!s:_^80}\n'.format('Request Object')
        printable_string += '{0!s:40}\n'.format('Metadata')
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Description', self.description)

        #
        # request settings
        #
        printable_string += '\n{0!s:40}\n'.format('Request Settings')
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Owner', self.owner)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Owner Allowed', self.owner_allowed)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Resource Pagination', self.resource_pagination)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Resource Type', self.resource_type)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Remaining Results', self.remaining_results)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Result Limit', self.result_limit)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Result Start', self.result_start)

        #
        # http settings
        #
        printable_string += '\n{0!s:40}\n'.format('HTTP Settings')
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('HTTP Method', self.http_method)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Request URI', self.request_uri)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Content Type', self.content_type)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Body', self.body)

        #
        # headers
        #
        if len(self.headers) > 0:
            printable_string += '\n{0!s:40}\n'.format('Headers')
            for k, v in list(self.headers.items()):
                printable_string += '  {0!s:<29}{1!s:<50}\n'.format(k, v)

        #
        # payload
        #
        if len(self.payload) > 0:
            printable_string += '\n{0!s:40}\n'.format('Payload')
            for k, v in list(self.payload.items()):
                printable_string += '  {0!s:<29}{1!s:<50}\n'.format(k, v)

        return printable_string