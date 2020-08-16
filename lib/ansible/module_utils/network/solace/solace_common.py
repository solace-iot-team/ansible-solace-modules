#!/usr/bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
# Copyright (c) 2020, Solace Corporation, Swen-Helge Huber <swen-helge.huber@solace.com
# Copyright (c) 2019, Mark Street <mkst@protonmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ---------------------------------------------------------------------------------------------

"""Common functions."""

import re
import traceback
import logging
import json
import os
import sys
from distutils.util import strtobool
import copy

HAS_IMPORT_ERROR = False
try:
    from json.decoder import JSONDecodeError
    import requests
    import xmltodict
except ImportError:
    HAS_IMPORT_ERROR = True
    IMPORT_ERR_TRACEBACK = traceback.format_exc()

_SC_SYSTEM_ERR_RC = -1
# check python version
_PY3_MIN = sys.version_info[:2] >= (3, 6)
if not _PY3_MIN:
    print(
        '\n{"failed": true, "rc": %d, "msg_hint": "Set ANSIBLE_PYTHON_INTERPRETER=path-to-python-3", '
        '"msg": "ansible-solace requires a minimum of Python3 version 3.6. Current version: %s."}' % (_SC_SYSTEM_ERR_RC, ''.join(sys.version.splitlines()))
    )
    sys.exit(1)


def module_fail_on_import_error(module, is_error, import_error_traceback=None):
    if is_error:
        if import_error_traceback is not None:
            exceptiondata = import_error_traceback.splitlines()
            exceptionarray = [exceptiondata[-1]] + exceptiondata[1:-1]
            module.fail_json(msg="Missing module: %s" % exceptionarray[0], rc=_SC_SYSTEM_ERR_RC, exception=import_error_traceback)
        else:
            module.fail_json(msg="Missing module: unknown", rc=_SC_SYSTEM_ERR_RC)
    return

################################################################################################
# initialize logging


ENABLE_LOGGING = False  # False to disable
enableLoggingEnvVal = os.getenv('ANSIBLE_SOLACE_ENABLE_LOGGING')
loggingPathEnvVal = os.getenv('ANSIBLE_SOLACE_LOG_PATH')
if enableLoggingEnvVal is not None and enableLoggingEnvVal != '':
    try:
        ENABLE_LOGGING = bool(strtobool(enableLoggingEnvVal))
    except ValueError:
        raise ValueError("failed: invalid value for env var: 'ANSIBLE_SOLACE_ENABLE_LOGGING={}'. use 'true' or 'false' instead.".format(enableLoggingEnvVal))

if ENABLE_LOGGING:
    logFile = './ansible-solace.log'
    if loggingPathEnvVal is not None and loggingPathEnvVal != '':
        logFile = loggingPathEnvVal
    logging.basicConfig(filename=logFile,
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s(): %(message)s')
    logging.info('Module start #############################################################################################')

################################################################################################


def log_http_roundtrip(resp):
    if hasattr(resp.request, 'body') and resp.request.body:
        try:
            decoded_body = resp.request.body.decode()
            request_body = json.loads(decoded_body)
        except AttributeError:
            request_body = resp.request.body
    else:
        request_body = "{}"

    if resp.text:
        try:
            resp_body = json.loads(resp.text)
        except JSONDecodeError:
            # try XML parsing it
            try:
                resp_body = xmltodict.parse(resp.text)
            except Exception:
                # print as text at least
                resp_body = resp.text
    else:
        resp_body = None

    log = {
        'request': {
            'method': resp.request.method,
            'url': resp.request.url,
            'headers': dict(resp.request.headers),
            'body': request_body
        },
        'response': {
            'status_code': resp.status_code,
            'reason': resp.reason,
            'url': resp.url,
            'headers': dict(resp.headers),
            'body': resp_body
        }
    }
    logging.debug("\n%s", json.dumps(log, indent=2))
    return


if not HAS_IMPORT_ERROR:
    class BearerAuth(requests.auth.AuthBase):
        def __init__(self, token):
            self.token = token

        def __call__(self, r):
            r.headers["authorization"] = "Bearer " + self.token
            return r


# solace cloud: cast everything to string
# broker: cast strings to ints & floats, string booleans to boolean
def type_conversion(d, is_solace_cloud):
    for k, i in d.items():
        t = type(i)
        if is_solace_cloud:
            if t == int or t == float:
                d[k] = str(i)
            elif t == bool:
                d[k] = str(i).lower()
        else:
            if (t == str) and re.search(r'^[0-9]+$', i):
                d[k] = int(i)
            elif (t == str) and re.search(r'^[0-9]+\.[0-9]$', i):
                d[k] = float(i)
            elif t == dict:
                d[k] = type_conversion(i, is_solace_cloud)
    return d


def merge_dicts(*argv):
    data = dict()
    for arg in argv:
        if arg:
            data.update(arg)
    return data


def compose_path(path_array):
    if not type(path_array) is list:
        raise TypeError("argument 'path_array' is not an array but {}".format(type(path_array)))
    # ensure elements are 'url encoded'
    # except first one: SEMP_V2_CONFIG or SOLACE_CLOUD_API_SERVICES_BASE_PATH
    paths = []
    for i, path_elem in enumerate(path_array):
        if path_elem == '':
            raise ValueError("path_elem='{}' is empty in path_array='{}'.".format(path_elem, str(path_array)))
        if i > 0:
            paths.append(path_elem.replace('/', '%2F'))
        else:
            paths.append(path_elem)
    return '/'.join(paths)


def do_deep_compare(new, old, changes=dict()):
    for k in new.keys():
        if not isinstance(new[k], dict):
            if new[k] != old.get(k, None):
                changes[k] = new[k]
        else:
            # changes[k] = dict()
            if k in old:
                c = do_deep_compare(new[k], old[k], dict())
                # logging.debug("\n\nc=\n{}\n\n".format(json.dumps(c, indent=2)))
                if c:
                    # logging.debug("\n\nc not empty: c=\n{}\n\n".format(json.dumps(c, indent=2)))
                    changes[k] = c
                    # changes[k].update(c)
            else:
                changes[k] = copy.deepcopy(new[k])
    # logging.debug("\n\nreturning changes =\n{}\n\n".format(json.dumps(changes, indent=2)))
    return changes


###
# The End.
