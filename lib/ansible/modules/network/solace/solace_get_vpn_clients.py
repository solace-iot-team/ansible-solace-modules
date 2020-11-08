#!/usr/bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
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

DOCUMENTATION = '''
---
module: solace_get_vpn_clients

version_added: '2.9.11'

short_description: Get a list of VPN Client Objects.

description:
- "Get a list of VPN Client objects."

notes:
- "Reference Monitor: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/client/getMsgVpnClients)."

extends_documentation_fragment:
- solace.broker
- solace.vpn
- solace.get_list_monitor

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''

# Config:

    - name: Get a list of all VPN Client Objects
      solace_get_vpn_clients:
        msg_vpn: "{{ vpn }}"
        query_params:
          where:
            - "clientUsername==*ansible*"
          select:
              - txByteCount
              - clientAddress
              - clientName
              - uptime
      register: pre_existing_list

    - name: Print pre-existing list
      debug:
        msg: "{{ pre_existing_list.result_list }}"

    - name: Print count of pre-existing list
      debug:
        msg: "{{ pre_existing_list.result_list_count }}"


'''

RETURN = '''
Monitor API:
result_list:
    description: The list of objects found containing requested fields.
    returned: on success
    type: list
    elements: complex
    sample: [
        {
            "clientAddress": "127.0.0.1:51794",
            "clientName": "test-ansible-1",
            "txByteCount": 296,
            "uptime": 5626
        }
    ]


result_list_count:
    description: Number of items in result_list.
    returned: on success
    type: int

'''


class SolaceGetVpnClientsTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_list(self):
        # GET monitor/msgVpns/{msgVpnName}/clients
        # only exists on monitor
        self.module.params['api'] = 'monitor'
        vpn = self.module.params['msg_vpn']
        path_array = [su.MSG_VPNS, vpn, su.CLIENTS]
        return self.execute_get_list(path_array)


def run_module():
    module_args = dict(
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_get_list_monitor())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        changed=False
    )

    solace_task = SolaceGetVpnClientsTask(module)
    ok, resp_or_list = solace_task.get_list()
    if not ok:
        module.fail_json(msg=resp_or_list, **result)

    result['result_list'] = resp_or_list
    result['result_list_count'] = len(resp_or_list)
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
