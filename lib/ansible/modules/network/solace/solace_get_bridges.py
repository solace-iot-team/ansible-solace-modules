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

DOCUMENTATION = '''
---
module: solace_get_bridges

version_added: '2.9.11'

short_description: Get a list of Bridge objects.

description:
- "Get a list of Bridge objects."

notes:
- "Reference Config: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge/getMsgVpnBridges)."
- "Reference Monitor: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/bridge/getMsgVpnBridges)."

extends_documentation_fragment:
- solace.broker
- solace.vpn
- solace.get_list

seealso:
- module: solace_bridge

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''

# Config:

  - name: Get List of all Bridges
    solace_get_bridges:
      msg_vpn: "{{ vpn }}"
      query_params:
        where:
          - "bridgeName==*ansible*"
        select:
    register: pre_existing_bridges

  - name: Print pre-existing Bridges
    debug:
      msg:
        - "pre-exising bridges:"
        - "{{ pre_existing_bridges.result_list }}"

  - name: Print count of pre-existing Bridges
    debug:
      msg: "pre-existing bridges, count= {{ pre_existing_bridges.result_list_count }}"

'''

RETURN = '''
Config API:
result_list:
    description: The list of objects found containing requested fields.
    returned: on success
    type: list
    elements: complex
    sample: [
        {
            "bridgeName": "default_ansible-test",
            "bridgeVirtualRouter": "auto",
            "enabled": true,
            "maxTtl": 8,
            "msgVpnName": "ansible-test",
            "remoteAuthenticationBasicClientUsername": "default",
            "remoteAuthenticationScheme": "basic",
            "remoteConnectionRetryCount": 0,
            "remoteConnectionRetryDelay": 3,
            "remoteDeliverToOnePriority": "p1",
            "tlsCipherSuiteList": "default"
        },
        {
            "bridgeName": "test_ansible_solace",
            "bridgeVirtualRouter": "auto",
            "enabled": false,
            "maxTtl": 8,
            "msgVpnName": "ansible-test",
            "remoteAuthenticationBasicClientUsername": "test_ansible_solace",
            "remoteAuthenticationScheme": "basic",
            "remoteConnectionRetryCount": 0,
            "remoteConnectionRetryDelay": 3,
            "remoteDeliverToOnePriority": "p1",
            "tlsCipherSuiteList": "default"
        }
    ]

Monitor API:
result_list:
    description: The list of objects found containing requested fields.
    returned: on success
    type: list
    elements: complex
    sample: [
        {
            "averageRxByteRate": 0,
            "averageRxMsgRate": 0,
            "averageTxByteRate": 0,
            "averageTxMsgRate": 0,
            "boundToQueue": true,
            "bridgeName": "ansible-solace__test_bridge",
            "bridgeVirtualRouter": "auto",
            "clientName": "#bridge/remote/ansible-solace__test_bridge/v:ansible-solace__test/270/775",
            "compressed": false,
            "controlRxByteCount": 1193,
            "controlRxMsgCount": 9,
            "controlTxByteCount": 1268,
            "controlTxMsgCount": 9,
            "counter": {
                "controlRxByteCount": 1193,
                "controlRxMsgCount": 9,
                "controlTxByteCount": 1268,
                "controlTxMsgCount": 9,
                "dataRxByteCount": 0,
                "dataRxMsgCount": 0,
                "dataTxByteCount": 0,
                "dataTxMsgCount": 0,
                "discardedRxMsgCount": 0,
                "discardedTxMsgCount": 0,
                "loginRxMsgCount": 1,
                "loginTxMsgCount": 1,
                "msgSpoolRxMsgCount": 0,
                "rxByteCount": 1193,
                "rxMsgCount": 9,
                "txByteCount": 1268,
                "txMsgCount": 9
        }
    ]


result_list_count:
    description: Number of items in result_list.
    returned: on success
    type: int

'''


class SolaceGetBridgesTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_list(self):
        # GET /msgVpns/{msgVpnName}/bridges
        vpn = self.module.params['msg_vpn']
        path_array = [su.MSG_VPNS, vpn, su.BRIDGES]
        return self.execute_get_list(path_array)


def run_module():
    module_args = dict(
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_get_list())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        changed=False
    )

    solace_task = SolaceGetBridgesTask(module)
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
