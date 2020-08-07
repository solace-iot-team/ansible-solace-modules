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
module: solace_bridge

version_added: "2.9.10"

short_description: Configure a Bridge object.

description:
  - "Configure a Bridge object. Allows addition, removal and update of a Bridge Object in an idempotent manner."

notes:
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge)."

options:
  name:
    description: The bridge name. Maps to 'bridgeName' in the API.
    required: true
    type: str
  virtual_router:
    description: The virtual router.
    required: false
    type: str
    default: auto
    choices:
      - primary
      - backup
      - auto

extends_documentation_fragment:
- solace.broker
- solace.vpn
- solace.settings
- solace.state

author:
  - Mark Street (mkst@protonmail.com)
  - Swen-Helge Huber (swen-helge.huber@solace.com)
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''
  - name: Remove Bridge
    solace_bridge:
      name: "{{ bridge }}"
      msg_vpn: "{{ msg_vpn }}"
      virtual_router: "{{ virtual_router }}"
      state: absent

  - name: Add Bridge
    solace_bridge:
      name: "{{ bridge }}"
      msg_vpn: "{{ msg_vpn }}"
      virtual_router: "{{ virtual_router }}"
      settings:
        enabled: false
        remoteAuthenticationBasicClientUsername: default
        remoteAuthenticationBasicPassword: password
        remoteAuthenticationScheme: basic

  - name: Update bridge
    solace_bridge:
      name: "{{ bridge }}"
      msg_vpn: "{{ msg_vpn }}"
      virtual_router: "{{ virtual_router }}"
      settings:
        enabled: true

'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
'''


class SolaceBridgeTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'bridgeName'
    WHITELIST_KEYS = ['remoteAuthenticationBasicPassword',
                      'remoteAuthenticationClientCertPassword']
    REQUIRED_TOGETHER_KEYS = [
        ['remoteAuthenticationBasicClientUsername', 'remoteAuthenticationBasicPassword'],
        ['remoteAuthenticationClientCertPassword', 'remoteAuthenticationClientCertContent']
    ]

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['virtual_router']]

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, vpn, virtual_router, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}
        bridge_uri = ','.join([lookup_item_value, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, virtual_router, bridge_name, settings=None):
        # POST /msgVpns/{msgVpnName}/bridges
        defaults = {
            'msgVpnName': vpn,
            'bridgeVirtualRouter': virtual_router
        }
        mandatory = {
            self.LOOKUP_ITEM_KEY: bridge_name
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, vpn, virtual_router, lookup_item_value, settings=None):
        # PATCH /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}
        bridge_uri = ','.join([lookup_item_value, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, virtual_router, lookup_item_value):
        # DELETE /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}
        bridge_uri = ','.join([lookup_item_value, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri]
        return su.make_delete_request(solace_config, path_array, None)


def run_module():
    """Entrypoint to module."""
    module_args = dict(
        name=dict(type='str', required=True),
        virtual_router=dict(type='str', default='auto', choices=['primary', 'backup', 'auto'])
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_crud())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceBridgeTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
