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

import traceback
import logging
import json
import os
import sys
from distutils.util import strtobool

HAS_IMPORT_ERROR = False
try:
    from json.decoder import JSONDecodeError
    import requests
    import xmltodict
except ImportError:
    HAS_IMPORT_ERROR = True
    IMPORT_ERR_TRACEBACK = traceback.format_exc()

# check python version
_PY3_MIN = sys.version_info[:2] >= (3, 6)
if not _PY3_MIN:
    print(
        '\n{"failed": true, "rc": 1, "msg_hint": "Set ANSIBLE_PYTHON_INTERPRETER=path-to-python-3", '
        '"msg": "ansible-solace requires a minimum of Python3 version 3.6. Current version: %s."}' % (''.join(sys.version.splitlines()))
    )
    sys.exit(1)


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

###
# The End.