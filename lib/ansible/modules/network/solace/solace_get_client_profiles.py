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
module: solace_get_client_profiles

version_added: '2.9.11'

short_description: Get a list of Client Profile objects.

description:
- "Get a list of Client Profile objects."

notes:
- "Reference Config: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/clientProfile/getMsgVpnClientProfiles)."
- "Reference Monitor: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/monitor/index.html#/clientProfile/getMsgVpnClientProfiles)."

extends_documentation_fragment:
- solace.broker
- solace.vpn
- solace.get_list

seealso:
- module: solace_client_profile

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)

'''

EXAMPLES = '''

# Config:
-
  name: "Test module: solace_get_client_profiles"
  hosts: "{{ brokers }}"
  gather_facts: no
  module_defaults:
    solace_client_profile:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
      solace_cloud_api_token: "{{ solace_cloud_api_token | default(omit) }}"
      solace_cloud_service_id: "{{ solace_cloud_service_id | default(omit) }}"
    solace_get_client_profiles:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"

  tasks:

    - name: Get pre-existing client profiles
      solace_get_client_profiles:
        query_params:
          where:
            - "clientProfileName==ansible-solace__test*"
          select:
            - "clientProfileName"
      register: pre_existing_list

    - name: Print pre-existing list
      debug:
        msg: "{{ pre_existing_list.result_list }}"

    - name: Print count of pre-existing list
      debug:
        msg: "{{ pre_existing_list.result_list_count }}"

    - name: Remove all found client profiles
      solace_client_profile:
        name: "{{ item.clientProfileName }}"
        state: absent
      register: result
      loop: "{{ pre_existing_list.result_list }}"


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
            "clientProfileName": "ansible-solace__test__1__"
        },
        {
            "clientProfileName": "ansible-solace__test__4__"
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
            "allowBridgeConnectionsEnabled": false,
            "allowCutThroughForwardingEnabled": false,
            "allowGuaranteedEndpointCreateEnabled": false,
            "allowGuaranteedMsgReceiveEnabled": false,
            "allowGuaranteedMsgSendEnabled": false,
            "allowSharedSubscriptionsEnabled": false,
            "allowTransactedSessionsEnabled": false,
            "apiQueueManagementCopyFromOnCreateName": "",
            "apiTopicEndpointManagementCopyFromOnCreateName": "",
            "clientProfileName": "ansible-solace__test__1__",
            "compressionEnabled": true,
            "elidingDelay": 0,
            "elidingEnabled": false,
            "elidingMaxTopicCount": 256,
            "eventClientProvisionedEndpointSpoolUsageThreshold": {
                "clearPercent": 60,
                "setPercent": 80
            },
            "eventConnectionCountPerClientUsernameThreshold": {
                "clearPercent": 60,
                "setPercent": 80
            }
        }
    ]

result_list_count:
    description: Number of items in result_list.
    returned: on success
    type: int

'''


class SolaceGetClientProfilesTask(su.SolaceTask):

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_list(self):
        # GET /msgVpns/{msgVpnName}/clientProfiles
        vpn = self.module.params['msg_vpn']
        path_array = [su.MSG_VPNS, vpn, su.CLIENT_PROFILES]
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

    solace_task = SolaceGetClientProfilesTask(module)
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
