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
import ansible.module_utils.network.solace.solace_common as sc
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: solace_get_magic_queues

version_added: '2.9.11'

short_description: Get a list of 'magic' Queue Objects (#mqtt, #rdp, ...)

description:
- "Get a list of 'magic' Queue Objects that are generated by the Broker, e.g. #mqtt, #rdp, ..."

options:
    where_name:
        description: Query for queue name. Maps to <name> in the API.
        required: true
        type: str
        examples: "#mqtt/*, #rdp/*"
notes:
- Uses SEMP v1.
- "Reference: U(https://docs.solace.com/Configuring-and-Managing/Monitoring-Guaranteed-Messaging.htm#Viewing)."

extends_documentation_fragment:
- solace.broker
- solace.vpn

seealso:
- module: solace_get_queues

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''

    - name: "Get MQTT Magic Queues"
      solace_get_magic_queues:
        where_name: "#mqtt/*"
      register: result

    - set_fact:
        magic_queues: "{{ result.result_list }}"

    - name: "Save Queues to File"
      local_action:
        module: copy
        content: "{{ magic_queues | to_nice_json }}"
        dest: "./tmp/magic_queues.{{ inventory_hostname }}.json"
      no_log: true
      changed_when: false

    - name: "Check: All magic Queues are ON/ON"
      fail:
        msg: "Magic queue: ingress or egress is 'Down' for magic_queue: {{ magic_queue.name }} "
      when: magic_queue.info['ingress-config-status'] == "Down" or magic_queue.info['egress-config-status'] == "Down"
      loop: "{{ magic_queues }}"
      loop_control:
        loop_var: magic_queue

'''

RETURN = '''

rc:
    description: return code. on success: rc=0, on failure: rc=1
    type: int

result_list:
    description: The list of objects found containing requested fields.
    returned: on success
    type: list
    elements: complex
    sample: [
        {
            "info": {
                "access-type": "exclusive",
                "bind-count": "0",
                "current-spool-usage-in-mb": "0",
                "durable": "true",
                "egress-config-status": "Down",
                "egress-selector-present": "No",
                "high-water-mark-in-mb": "0",
                "ingress-config-status": "Down",
                "message-vpn": "default",
                "num-messages-spooled": "0",
                "topic-subscription-count": "3",
                "type": "Primary"
            },
            "name": "#mqtt/ansible_solace_test_mqtt__1__/180"
        },
        {
            "info": {
                "access-type": "exclusive",
                "bind-count": "0",
                "current-spool-usage-in-mb": "0",
                "durable": "true",
                "egress-config-status": "Down",
                "egress-selector-present": "No",
                "high-water-mark-in-mb": "0",
                "ingress-config-status": "Down",
                "message-vpn": "default",
                "num-messages-spooled": "0",
                "topic-subscription-count": "3",
                "type": "Primary"
            },
            "name": "#mqtt/ansible_solace_test_mqtt__3__/184"
        }
    ]

result_list_count:
    description: Number of items in result_list.
    returned: on success
    type: int

'''


class SolaceGetMagicQueuesTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_list(self):
        # SEMP v1
        request = {
            'rpc': {
                'show': {
                    'queue': {
                        'name': self.module.params['where_name'],
                        'vpn-name': self.module.params['msg_vpn'],
                        # not found tests
                        # 'name': "does-not-exist",
                        # 'vpn-name': "does-not-exist",
                        # keep for paging test
                        # 'count': '',
                        # 'num-elements': 1
                    }
                }
            }
        }
        list_path_array = ['rpc-reply', 'rpc', 'show', 'queue', 'queues', 'queue']
        return sc.execute_sempv1_get_list(self.solace_config, request, list_path_array)


def run_module():
    module_args = dict(
        where_name=dict(type='str', required=True)
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        rc=0,
        changed=False
    )

    solace_task = SolaceGetMagicQueuesTask(module)
    ok, resp_or_list = solace_task.get_list()
    if not ok:
        result['rc'] = 1
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
