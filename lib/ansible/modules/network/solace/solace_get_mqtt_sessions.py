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
module: solace_get_mqtt_sessions

version_added: '2.9.10'

short_description: Get a list of MQTT Session objects

description:
- "Get a list of MQTT Session objects."

notes:
- "Reference Config: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/mqttSession/getMsgVpnMqttSessions)."
- "Reference Monitor: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/mqttSession/getMsgVpnMqttSessions)."

extends_documentation_fragment:
- solace.broker
- solace.vpn
- solace.get_list

seealso:
- module: solace_mqtt_session

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''

# Config:

    - name: Get List of MQTT Sessions
      solace_get_mqtt_sessions:
        msg_vpn: "{{ vpn }}"
        query_params:
          where:
            - "mqttSessionClientId==ansible-solace_test_mqtt*"
          select:
            - "mqttSessionClientId"
            - "mqttSessionVirtualRouter"
            - "enabled"
            - "owner"
      register: get_sessions_result

    - name: Print existing list
      debug:
        msg: "{{ get_sessions_result.result_list }}"

    - name: Print count of existing queue list
      debug:
        msg: "{{ get_sessions_result.result_list_count }}"

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
            "enabled": true,
            "mqttSessionClientId": "ansible-solace_test_mqtt__1__",
            "mqttSessionVirtualRouter": "primary",
            "owner": "ansible-solace_test_mqtt_client_username"
        },
        {
            "enabled": true,
            "mqttSessionClientId": "ansible-solace_test_mqtt__4__",
            "mqttSessionVirtualRouter": "primary",
            "owner": "ansible-solace_test_mqtt_client_username"
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
            "clean": false,
            "clientName": "#mqtt/ansible-solace_test_mqtt__1__/30",
            "counter": {
                "mqttConnackErrorTxCount": 0,
                "mqttConnackTxCount": 0,
                "mqttConnectRxCount": 0,
                "mqttDisconnectRxCount": 0,
                "mqttPubcompTxCount": 0,
                "mqttPublishQos0RxCount": 0,
                "mqttPublishQos0TxCount": 0,
                "mqttPublishQos1RxCount": 0,
                "mqttPublishQos1TxCount": 0,
                "mqttPublishQos2RxCount": 0,
                "mqttPubrecTxCount": 0,
                "mqttPubrelRxCount": 0
            },
            "createdByManagement": true,
            "enabled": true
        }
    ]

result_list_count:
    description: Number of items in result_list.
    returned: on success
    type: int

'''


class SolaceGetMqttSessionsTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_list(self):
        # GET /msgVpns/{msgVpnName}/mqttSessions
        vpn = self.module.params['msg_vpn']
        path_array = [su.MSG_VPNS, vpn, su.MQTT_SESSIONS]
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

    solace_task = SolaceGetMqttSessionsTask(module)
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
