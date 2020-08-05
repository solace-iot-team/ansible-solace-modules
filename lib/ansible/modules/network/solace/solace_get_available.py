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
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    REQUESTS_IMP_ERR = traceback.format_exc()
    HAS_REQUESTS = False


DOCUMENTATION = '''
---
module: solace_get_available

short_description: Check if broker/service is reachable and responsive.

description: >
  Check if broker/service is reachable and responsive.
  Calls "GET /about" and sets "rc=0" if reachable, "rc=-1" if not.

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

    - name: Pause Until Broker/Service available
      solace_get_available:
      register: _result
      until: _result.rc != -1
      retries: 25 # 25 * 5 seconds
      delay: 5 # Every 5 seconds
'''

RETURN = '''
rc:
    description: Return code.
    type: int
    rc = 0 : broker / service is reachable
    rc = -1 : broker / service is not reachable

'''


class SolaceGetAvailableTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)
        self._module_check_imports()

    def _module_check_imports(self):
        if not HAS_REQUESTS:
            self.module.fail_json(msg=su.EX_MSG_MISSING_REQUESTS_MODULE, **su.EX_RESULT, exception=REQUESTS_IMP_ERR)

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
        rc=0
    )

    solace_task = SolaceGetAvailableTask(module)
    ok, resp = solace_task.get_available()
    if not ok:
        result['rc'] = -1
        module.fail_json(msg=resp, **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
