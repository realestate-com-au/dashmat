from python_dashing.core_modules.base import Module
from python_dashing.errors import ProgrammerError

from six.moves import http_client as httplib
from input_algorithms.dictobj import dictobj
from six.moves.urllib.parse import urlparse
from contextlib import contextmanager
import logging
import time
import site
import sys
import ssl
import os

# Put splunklib in our path
site.addsitedir(os.path.join(os.path.dirname(__file__), "splunk-sdk-1.3.0"))

log = logging.getLogger("custom.splunk.main")

class Splunk(Module):
    pass

class SplunkSource(dictobj):
    fields = ["source_host", "search", "user", "password", "earliest_time", "latest_time"]

    @property
    def host(self):
        return urlparse(self.source_host).netloc.split(":", 1)[0]

    @property
    def port(self):
        netloc = urlparse(self.source_host).netloc
        if ":" in netloc:
            return int(netloc.split(":", 1)[1])
        else:
            scheme = urlparse(self.source_host).scheme or 'http'
            return {'http': 80, 'https': 443}[scheme]

    @property
    def service(self):
        if not getattr(self, "_service"):
            raise ProgrammerError("Please login to the splunk before asking the splunk questions")
        return self._service

    @property
    def resolved_password(self):
        if not getattr(self, "_resolved_password", None):
            password = self.password
            if callable(password):
                password = password()
            self._resolved_password = password
        return self._resolved_password

    @contextmanager
    def login(self):
        import splunklib.client as client
        self._service = client.connect(handler=handler(), host=self.host, port=self.port, username=self.user, password=self.resolved_password, autologin=True)
        try:
            yield self
        finally:
            self._service.logout()
            self._service = None
            del self._resolved_password

    def entries(self):
        import splunklib.results as results

        log.info("Performing search\tsearch=%s\tearliest_time=%s\tlatest_time=%s", self.search, self.earliest_time, self.latest_time)
        job = self.service.jobs.create("search {0}".format(self.search)
            , exec_mode = "normal"
            , latest_time = self.latest_time
            , earliest_time = self.earliest_time
            )

        while True:
            while not job.is_ready():
                pass

            stats = {
                  "isDone": job["isDone"]
                , "scanCount": int(job["scanCount"])
                , "eventCount": int(job["eventCount"])
                , "resultCount": int(job["resultCount"])
                , "doneProgress": float(job["doneProgress"])*100
                }

            status = "\r%(doneProgress)03.1f%%   %(scanCount)d scanned   %(eventCount)d matched   %(resultCount)d results" % stats
            sys.stdout.write(status)
            sys.stdout.flush()
            if stats["isDone"] == "1":
                sys.stdout.write("\n\nDone!\n\n")
                break
            time.sleep(2)

        log.info("Processing %s results", job["resultCount"])
        count = 0
        for result in results.ResultsReader(job.results(count=0)):
            count += 1
            if count % 100 == 0 and "rt" not in self.latest_time and "rt" not in self.earliest_time:
                sys.stdout.write(".")
                sys.stdout.flush()
            yield result

    def __iter__(self):
        with self.login() as src:
            for entry in src.entries():
                yield entry

def handler(key_file=None, cert_file=None, timeout=None):
    """This class returns an instance of the default HTTP request handler using
    the values you provide.
    :param `key_file`: A path to a PEM (Privacy Enhanced Mail) formatted file containing your private key (optional).
    :type key_file: ``string``
    :param `cert_file`: A path to a PEM (Privacy Enhanced Mail) formatted file containing a certificate chain file (optional).
    :type cert_file: ``string``
    :param `timeout`: The request time-out period, in seconds (optional).
    :type timeout: ``integer`` or "None"

    Taken from the splunklib library with one modification to not close the Connection prematurely
    """

    def connect(scheme, host, port):
        kwargs = {}
        if timeout is not None: kwargs['timeout'] = timeout
        if scheme == "http":
            return httplib.HTTPConnection(host, port, **kwargs)
        if scheme == "https":
            if key_file is not None: kwargs['key_file'] = key_file
            if cert_file is not None: kwargs['cert_file'] = cert_file
            if hasattr(ssl, "_create_unverified_context"):
                ssl._create_default_https_context = ssl._create_unverified_context

            # If running Python 2.7.9+, disable SSL certificate validation
            # if sys.version_info >= (2,7,9) and key_file is None and cert_file is None:
            #     kwargs['context'] = ssl._create_unverified_context()
            return httplib.HTTPSConnection(host, port, **kwargs)
        raise ValueError("unsupported scheme: %s" % scheme)

    def request(url, message, **kwargs):
        from splunklib.binding import _spliturl, ResponseReader

        scheme, host, port, path = _spliturl(url)
        body = message.get("body", "")
        head = {
            "Content-Length": str(len(body)),
            "Host": host,
            "User-Agent": "splunk-sdk-python/0.1",
            "Accept": "*/*",
        } # defaults
        for key, value in message["headers"]:
            head[key] = value
        method = message.get("method", "GET")

        response = None
        connection = connect(scheme, host, port)
        try:
            connection.request(method, path, body, head)
            if timeout is not None:
                connection.sock.settimeout(timeout)
            response = connection.getresponse()
        finally:
            if response:
                conn_header = response.getheader('Connection', None)
                if conn_header == "Close":
                    connection.close()

        return {
            "status": response.status,
            "reason": response.reason,
            "headers": response.getheaders(),
            "body": ResponseReader(response),
        }

    return request
