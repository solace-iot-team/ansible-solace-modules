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

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

import ansible.module_utils.network.solace.solace_utils as su
from ansible.module_utils.basic import AnsibleModule
import traceback

HAS_IMPORT_ERROR = False
try:
    import requests
except ImportError:
    HAS_IMPORT_ERROR = True
    IMPORT_ERR_TRACEBACK = traceback.format_exc()


DOCUMENTATION = '''
---
module: solace_get_available

short_description: Check if broker/service is reachable and responsive.

description: >
  Check if broker/service is reachable and responsive.
  Calls "GET /about" and sets "is_available=True/False".

extends_documentation_fragment:
- solace.broker

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''
-
  name: "Check/wait until brokers available"
  hosts: "{{ brokers }}"
  gather_facts: no
  any_errors_fatal: true
  module_defaults:
    solace_get_available:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"

  tasks:

    - name: "Pause Until Broker/Service available"
      solace_get_available:
      register: _result
      until: "_result.is_available"
      retries: 25 # 25 * 5 seconds
      delay: 5 # Every 5 seconds
'''

RETURN = '''
is_available:
    description: Flag indicating whether broker was reachable or not.
    type: bool
msg:
    description: The response from the HTTP call or error description.
    type: str

samples:

    "is_available": false,
    "msg": "('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))",


'''


class SolaceGetAvailableTask(su.SolaceTask):

    def __init__(self, module):
        if HAS_IMPORT_ERROR:
            exceptiondata = traceback.format_exc().splitlines()
            exceptionarray = [exceptiondata[-1]] + exceptiondata[1:-1]
            module.fail_json(msg="failed: Missing module: %s" % exceptionarray[0], exception=IMPORT_ERR_TRACEBACK)
        su.SolaceTask.__init__(self, module)
        return

    def get_available(self):
        ok, resp = make_get_request(self.solace_config, [su.SEMP_V2_CONFIG] + ["about"])
        if not ok:
            return False, resp
        return True, resp


def make_get_request(solace_config, path_array):

    path = su.compose_path(path_array)

    try:
        resp = requests.get(
                    solace_config.vmr_url + path,
                    json=None,
                    auth=solace_config.vmr_auth,
                    timeout=solace_config.vmr_timeout,
                    headers={'x-broker-name': solace_config.x_broker},
                    params=None
        )
        if su.ENABLE_LOGGING:
            su.log_http_roundtrip(resp)
        if resp.status_code != 200:
            return False, su.parse_bad_response(resp)
        return True, su.parse_good_response(resp)

    except requests.exceptions.ConnectionError as e:
        return False, str(e)


def run_module():
    module_args = dict(
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        rc=0,
        is_available=True
    )

    solace_task = SolaceGetAvailableTask(module)
    ok, resp = solace_task.get_available()
    result['is_available'] = ok
    module.exit_json(msg=resp, **result)


def main():
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
