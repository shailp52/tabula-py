import os
import shutil
# Python 3
# from urllib.parse import urlparse as parse_url
# from urllib.parse import uses_netloc, uses_params, uses_relative
# from urllib.request import Request, urlopen

# Python 2
from urlparse import urlparse as parse_url
from urlparse import uses_netloc, uses_params, uses_relative
from urllib2 import Request, urlopen

_VALID_URLS = set(uses_relative + uses_netloc + uses_params)
_VALID_URLS.discard("")


def localize_file(path_or_buffer, user_agent=None):
    """Ensure localize target file.

    If the target file is remote, this function fetches into local storage.

    Args:
        path (str):
            File path or file like object or URL of target file.

    Returns:
        filename (str): file name in local storage
        temporary_file_flag (bool): temporary file flag
    """

    path_or_buffer = _stringify_path(path_or_buffer)

    if _is_url(path_or_buffer):
        if user_agent:
            req = urlopen(_create_request(path_or_buffer, user_agent))
        else:
            req = urlopen(path_or_buffer)
        filename = os.path.basename(req.geturl())
        if os.path.splitext(filename)[-1] != ".pdf":
            pid = os.getpid()
            filename = "{0}.pdf".format(pid)

        with open(filename, "wb") as f:
            shutil.copyfileobj(req, f)

        return filename, True

    elif is_file_like(path_or_buffer):
        pid = os.getpid()
        filename = "{0}.pdf".format(pid)

        with open(filename, "wb") as f:
            shutil.copyfileobj(path_or_buffer, f)

        return filename, True

    # File path case
    else:
        return os.path.expanduser(path_or_buffer), False


def _is_url(url):
    try:
        return parse_url(url).scheme in _VALID_URLS

    except Exception:
        return False


def _create_request(path_or_buffer, user_agent):
    req_headers = {"User-Agent": user_agent}
    return Request(path_or_buffer, headers=req_headers)


def is_file_like(obj):
    """Check file like object

    Args:
        obj:
            file like object.

    Returns:
        bool: file like object or not
    """

    if not (hasattr(obj, "read") or hasattr(obj, "write")):
        return False

    if not hasattr(obj, "__iter__"):
        return False

    return True


def _stringify_path(path_or_buffer):
    """Convert path like object to string

    Args:
        path_or_buffer: object to be converted

    Returns:
        string_path_or_buffer: maybe string version of path_or_buffer
    """

    try:
        import pathlib

        _PATHLIB_INSTALLED = True
    except ImportError:
        _PATHLIB_INSTALLED = False

    if hasattr(path_or_buffer, "__fspath__"):
        return path_or_buffer.__fspath__()

    if _PATHLIB_INSTALLED and isinstance(path_or_buffer, pathlib.Path):
        return str(path_or_buffer)

    return path_or_buffer
