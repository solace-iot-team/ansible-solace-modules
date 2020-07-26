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
module: solace_client_profile

version_added: "2.9.11"

short_description: Configure a Client Profile object.

description:
- "Configure a Client Profile object. Allows addition, removal and configuration of Client Profile objects on Solace Brokers in an idempotent manner."

notes:
- "Supports Solace Cloud Brokers as well as Solace Standalone Brokers."
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/clientProfile)."
- "Reference: U(https://docs.solace.com/Solace-Cloud/ght_use_rest_api_client_profiles.htm)."

options:
  name:
    description: Name of the client profile. Maps to 'clientProfileName' in the API.
    type: str
    required: true
    aliases: [client_profile, client_profile_name]

extends_documentation_fragment:
- solace.broker
- solace.vpn
- solace.settings
- solace.state
- solace.solace_cloud_config

author:
  - Mark Street (mkst@protonmail.com)
  - Swen-Helge Huber (swen-helge.huber@solace.com)
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''
-
  name: Create / Update / Delete Client Profile
  hosts: "all"
  gather_facts: no
  module_defaults:
    solace_get_facts:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
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


  tasks:

    - name: Get Solace Facts
      solace_get_facts:

    - name: Delete Client Profile
      solace_client_profile:
        name: "test_ansible_solace"
        state: absent

    - name: Create Client Profile
      solace_client_profile:
        name: "test_ansible_solace"
        state: present

    - name: Update Client Profile
      solace_client_profile:
        name: "test_ansible_solace"
        settings:
          allowGuaranteedMsgSendEnabled: true
          allowGuaranteedMsgReceiveEnabled: true
          allowGuaranteedEndpointCreateEnabled: true
        state: present

    - name: Delete Client Profile
      solace_client_profile:
        name: "test_ansible_solace"
        state: absent

'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 / Solace Cloud request.
    type: dict
'''


class SolaceClientProfileTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'clientProfileName'

    SOLACE_CLOUD_DEFAULTS = {
        'allowTransactedSessionsEnabled': False,
        'allowBridgeConnectionsEnabled': False,
        'allowGuaranteedEndpointCreateEnabled': False,
        'allowSharedSubscriptionsEnabled': False,
        'allowGuaranteedMsgSendEnabled': False,
        'allowGuaranteedMsgReceiveEnabled': False
    }

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn']]

    def lookup_item(self):
        return self.module.params['name']

    def _get_func_solace_cloud(self, solace_config, lookup_item_value):
        # GET /{paste-your-serviceId-here}/clientProfiles/{{clientProfileName}}
        path_array = [su.SOLACE_CLOUD_API_SERVICES_BASE_PATH, solace_config.solace_cloud_config['service_id'], su.CLIENT_PROFILES, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def _get_func(self, solace_config, vpn, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_PROFILES, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def get_func(self, solace_config, vpn, lookup_item_value):
        if(su.is_broker_solace_cloud(solace_config)):
            return self._get_func_solace_cloud(solace_config, lookup_item_value)
        else:
            return self._get_func(solace_config, vpn, lookup_item_value)

    def _create_func_solace_cloud(self, solace_config, client_profile_name, data):
        # POST /{paste-your-serviceId-here}/requests/clientProfileRequests
        body = su.compose_solace_cloud_body('create', 'clientProfile', data)
        path_array = [su.SOLACE_CLOUD_API_SERVICES_BASE_PATH,
                      solace_config.solace_cloud_config['service_id'],
                      su.SOLACE_CLOUD_REQUESTS,
                      su.SOLACE_CLOUD_CLIENT_PROFILE_REQUESTS]
        return su.make_post_request(solace_config, path_array, body)

    def _create_func(self, solace_config, vpn, client_profile_name, data):
        # POST /msgVpns/{msgVpnName}/clientProfiles
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_PROFILES]
        return su.make_post_request(solace_config, path_array, data)

    def create_func(self, solace_config, vpn, client_profile_name, settings=None):
        defaults = {
        }
        mandatory = {
            self.LOOKUP_ITEM_KEY: client_profile_name,
        }
        data = su.merge_dicts(self.SOLACE_CLOUD_DEFAULTS, defaults, mandatory, settings)
        if(su.is_broker_solace_cloud(solace_config)):
            return self._create_func_solace_cloud(solace_config, client_profile_name, data)
        else:
            return self._create_func(solace_config, vpn, client_profile_name, data)

    def _update_func_solace_cloud(self, solace_config, lookup_item_value, settings):
        # POST /{paste-your-serviceId-here}/requests/clientProfileRequests
        mandatory = {
            self.LOOKUP_ITEM_KEY: lookup_item_value,
        }
        data = su.merge_dicts(self.SOLACE_CLOUD_DEFAULTS, mandatory, settings)
        body = su.compose_solace_cloud_body('update', 'clientProfile', data)
        path_array = [su.SOLACE_CLOUD_API_SERVICES_BASE_PATH,
                      solace_config.solace_cloud_config['service_id'],
                      su.SOLACE_CLOUD_REQUESTS,
                      su.SOLACE_CLOUD_CLIENT_PROFILE_REQUESTS]
        return su.make_post_request(solace_config, path_array, body)

    def _update_func(self, solace_config, vpn, lookup_item_value, settings):
        # PATCH /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_PROFILES, lookup_item_value]
        return su.make_patch_request(solace_config, path_array, settings)

    def update_func(self, solace_config, vpn, lookup_item_value, settings=None):
        if(su.is_broker_solace_cloud(solace_config)):
            return self._update_func_solace_cloud(solace_config, lookup_item_value, settings)
        else:
            return self._update_func(solace_config, vpn, lookup_item_value, settings)

    def _delete_func_solace_cloud(self, solace_config, client_profile_name):
        # POST /{paste-your-serviceId-here}/requests/clientProfileRequests
        data = {
            self.LOOKUP_ITEM_KEY: client_profile_name,
        }
        body = su.compose_solace_cloud_body('delete', 'clientProfile', data)
        path_array = [su.SOLACE_CLOUD_API_SERVICES_BASE_PATH,
                      solace_config.solace_cloud_config['service_id'],
                      su.SOLACE_CLOUD_REQUESTS,
                      su.SOLACE_CLOUD_CLIENT_PROFILE_REQUESTS]
        return su.make_post_request(solace_config, path_array, body)

    def _delete_func(self, solace_config, vpn, lookup_item_value):
        # DELETE /msgVpns/{msgVpnName}/clientProfiles/{clientProfileName}
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.CLIENT_PROFILES, lookup_item_value]
        return su.make_delete_request(solace_config, path_array)

    def delete_func(self, solace_config, vpn, lookup_item_value):
        if(su.is_broker_solace_cloud(solace_config)):
            return self._delete_func_solace_cloud(solace_config, lookup_item_value)
        else:
            return self._delete_func(solace_config, vpn, lookup_item_value)


def run_module():
    """Entrypoint to module."""
    module_args = dict(
        name=dict(type='str', aliases=['client_profile', 'client_profile_name'], required=True)
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_crud())
    arg_spec.update(su.arg_spec_solace_cloud_config())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceClientProfileTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():

    run_module()


if __name__ == '__main__':
    main()


###
# The End.
