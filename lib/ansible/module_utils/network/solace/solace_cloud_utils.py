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

"""Collection of utility classes and functions to aid the solace_cloud_* modules."""

import re
import traceback
import logging
import json

HAS_IMPORT_ERROR = False
try:
    import ansible.module_utils.network.solace.solace_common as sc
    import requests
except ImportError:
    HAS_IMPORT_ERROR = True
    IMPORT_ERR_TRACEBACK = traceback.format_exc()


""" Solace Cloud resources """
SOLACE_CLOUD_API_SERVICES_BASE_PATH = 'https://api.solace.cloud/api/v0/services'


class SolaceCloudConfig(object):
    def __init__(self,
                 api_token,
                 timeout):
        self.url = SOLACE_CLOUD_API_SERVICES_BASE_PATH
        self.auth = sc.BearerAuth(api_token)
        self.timeout = float(timeout)
        return


class SolaceCloudTask:

    def __init__(self, module):
        if HAS_IMPORT_ERROR:
            exceptiondata = traceback.format_exc().splitlines()
            exceptionarray = [exceptiondata[-1]] + exceptiondata[1:-1]
            module.fail_json(msg="Missing module: %s" % exceptionarray[0], rc=1, exception=IMPORT_ERR_TRACEBACK)

        self.module = module
        self.sc_config = SolaceCloudConfig(
            api_token=self.module.params['api_token'],
            timeout=self.module.params['timeout']
        )
        return

    def do_task(self):

        result = dict(
            changed=False,
            rc=0,
            response=dict()
        )
        crud_args = self.crud_args()
        settings = self.module.params['settings']
        if settings:
            settings = _type_conversion(settings)

        ok, resp = self.get_func(self.sc_config, *(self.get_args() + [self.lookup_item()]))
        if not ok:
            result['rc'] = 1
            self.module.fail_json(msg=resp, **result)

        # any whitelist required?

        existing_service = resp
        if existing_service is not None:
            if self.module.params['state'] == 'absent':
                # if not self.module.check_mode:
                #     ok, resp = self.delete_func(self.sc_config, *(self.get_args() + [self.lookup_item()]))
                #     if not ok:
                #         result['rc'] = 1
                #         self.module.fail_json(msg=resp, **result)
                result['rc'] = 1
                result['msg_todo'] = "implement DELETE"
                self.module.fail_json(msg=resp, **result)
                result['changed'] = True
            else:
                # state=present
                # if not self.module.check_mode:
                # get changes
                # changed keys are those that exist in settings and don't match current settings
                # check if any settings have changed
                # if so, calculate delta
                # call update_func if not in check_mode
                # TODO: if no update exists:
                #       raise error, user must delete & create themselves
                # if not self.module.check_mode:
                # delta_settings = {key: settings[key] for key in changed_keys}
                # crud_args.append(delta_settings)
                # ok, resp = self.update_func(self.solace_config, *crud_args)
                # result['response'] = resp
                # if not ok:
                #     self.module.fail_json(msg=resp, **result)
                result['rc'] = 1
                result['msg_todo'] = "implement UPDATE"
                self.module.fail_json(msg=resp, **result)

                result['changed'] = True
        else:
            if self.module.params['state'] == 'present':
                if not self.module.check_mode:

                    # result['rc'] = 1
                    # result['msg_todo'] = "implement CREATE"
                    # self.module.fail_json(msg=resp, **result)

                    if settings:
                        crud_args.append(settings)
                    ok, resp = self.create_func(self.sc_config, *crud_args)
                    if ok:
                        result['response'] = resp
                    else:
                        result['rc'] = 1
                        self.module.fail_json(msg=resp, **result)
                result['changed'] = True

        return result

    def get_func(self, solace_config, *args):
        return False, dict()

    def create_func(self, solace_config, *args):
        return False, dict()

    def update_func(self, solace_config, *args):
        return False, dict()

    def delete_func(self, solace_config, *args):
        return False, dict()

    def lookup_item(self):
        return None

    def get_args(self):
        return []

    def crud_args(self):
        return self.get_args() + [self.lookup_item()]


###
# End Class SolaceCloudTask

# composable argument specs
def arg_spec_solace_cloud():
    return dict(
        api_token=dict(type='str', required=True, no_log=True),
        service_id=dict(type='str', required=False, default=None),
        timeout=dict(type='int', default='60', required=False)
    )


def arg_spec_settings():
    return dict(
        settings=dict(type='dict', required=False)
    )


def arg_spec_state():
    return dict(
        state=dict(type='str', default='present', choices=['absent', 'present'])
    )


def merge_dicts(*argv):
    data = dict()
    for arg in argv:
        if arg:
            data.update(arg)
    return data


def _type_conversion(d):
    for k, i in d.items():
        t = type(i)
        if (t == str) and re.search(r'^[0-9]+$', i):
            d[k] = int(i)
        elif (t == str) and re.search(r'^[0-9]+\.[0-9]$', i):
            d[k] = float(i)
        elif t == dict:
            d[k] = _type_conversion(i)
    return d


def _build_config_dict(resp, key):
    if not type(resp) is dict:
        raise TypeError("argument 'resp' is not a 'dict' but {}.".format(type(resp)))
    # wrong LOOKUP_ITEM_KEY in module
    if key not in resp:
        raise ValueError("wrong 'LOOKUP_ITEM_KEY' in module. semp GET response does not contain key='{}'".format(key))
    # resp is a single dict, not an array
    # return an array with 1 element
    d = dict()
    d[resp[key]] = resp
    return d

# request/response handling


def _parse_response(solace_config, resp):
    if sc.ENABLE_LOGGING:
        sc.log_http_roundtrip(resp)
    # ?check what GET returns?
    # POST: create service returns 201
    # ?Solace Cloud API returns 202: accepted if long running request
    if resp.status_code != 200:
        return False, _parse_bad_response(resp)
    return True, _parse_good_response(resp)


def _parse_good_response(resp):
    j = resp.json()
    # return the array for GET calls if exists
    if 'data' in j.keys():
        return j['data']
    return dict()


def _parse_bad_response(resp):
    if not resp.text:
        return resp
    # j = resp.json()
    # if 'meta' in j.keys() and \
    #         'error' in j['meta'].keys() and \
    #         'description' in j['meta']['error'].keys():
    #     # return j['meta']['error']['description']
    #     # we want to see the full message, including the code & request
    #     return _create_hint_bad_response(j['meta'])
    return dict(status_code=resp.status_code,
                body=json.loads(resp.text)
                )


def compose_path(path_array):
    if not type(path_array) is list:
        raise TypeError("argument 'path_array' is not an array but {}".format(type(path_array)))
    # ensure elements are 'url encoded'
    # except first one: SEMP_V2_CONFIG or SOLACE_CLOUD_API_SERVICES_BASE_PATH
    paths = []
    for i, path_elem in enumerate(path_array):
        if i > 0:
            paths.append(path_elem.replace('/', '%2F'))
        else:
            paths.append(path_elem)
    return '/'.join(paths)


def _make_request(func, solace_config, path_array, json=None):
    try:
        return _parse_response(
            solace_config,
            func(
                url=compose_path(path_array),
                json=json,
                auth=solace_config.auth,
                timeout=solace_config.timeout,
                params=None
            )
        )
    except requests.exceptions.ConnectionError as e:
        logging.debug("ConnectionError: %s", str(e))
        return False, str(e)


def make_get_request(solace_config, path_array):
    return _make_request(requests.get, solace_config, path_array)


def make_post_request(solace_config, path_array, json=None):
    return _make_request(requests.post, solace_config, path_array, json)


def make_delete_request(solace_config, path_array, json=None):
    return _make_request(requests.delete, solace_config, path_array, json)


def make_patch_request(solace_config, path_array, json=None):
    return _make_request(requests.patch, solace_config, path_array, json)

###
# The End.
