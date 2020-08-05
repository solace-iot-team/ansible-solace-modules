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
module: solace_bridge_remote_vpn

version_added: "2.9.10"

short_description: Configure a Remote Message VPN object on a bridge.

description:
- "Configure a Remote Message VPN object on a bridge.. Allows addition and removal of Remote Message VPN objects on a bridge in an idempotent manner."

notes:
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/bridge/createMsgVpnBridgeRemoteMsgVpn)."

options:
  name:
    description: The remote message VPN name on the remote broker. Maps to 'remoteMsgVpnName' in the API.
    required: true
    type: str
    aliases: [remote_msg_vpn_name]
  bridge_name:
    description: The bridge. Maps to 'bridgeName' in the API.
    required: true
    type: str
  bridge_virtual_router:
    description: The bridge virtual router. Maps to 'bridgeVirtualRouter' in the API.
    required: false
    type: str
    default: auto
    choices:
      - primary
      - backup
      - auto
    aliases: [virtual_router]
  remote_vpn_location:
    description: The remote vpn location. Maps to 'remoteMsgVpnLocation' in the API.
    required: true
    type: str
  remote_vpn_interface:
    description: The remote message VPN interface. Maps to 'remoteMsgVpnInterface' in the API.
    required: false
    type: str
    default: None

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

  - name: Add Remote Message VPN to Bridge
    solace_bridge_remote_vpn:
      msg_vpn: "{{ vpn }}"
      remote_msg_vpn_name: "{{ remote_vpn.remote_msg_vpn_name }}"
      bridge_name: "{{ bridge_name }}"
      bridge_virtual_router: auto
      remote_vpn_location: "{{ remote_vpn.remote_vpn_location }}"
      settings:
        enabled: true
        queueBinding: "ansible-solace__test_bridge"
      state: present

  - name: Remove Bridge Remote VPN
    solace_bridge_remote_vpn:
      msg_vpn: "{{ vpn }}"
      remote_msg_vpn_name: "{{ remote_vpn.remote_msg_vpn_name }}"
      bridge_name: "{{ bridge_name }}"
      remote_vpn_location: "{{ remote_vpn.remote_vpn_location }}"
      state: absent

'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
'''


class SolaceBridgeRemoteVpnTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'remoteMsgVpnName'

    def __init__(self, module):
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'],
                self.module.params['bridge_virtual_router'],
                self.module.params['bridge_name'],
                self.module.params['remote_vpn_location'],
                self.module.params['remote_vpn_interface']]

    def lookup_item(self):
        return self.module.params['name']

    def get_func(self, solace_config, vpn, bridge_virtual_router, bridge_name, remote_vpn_location, remote_vpn_interface, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteMsgVpns/{remoteMsgVpnName},{remoteMsgVpnLocation},{remoteMsgVpnInterface}
        bridge_uri = ','.join([bridge_name, bridge_virtual_router])
        remote_vpn_uri = ','.join([lookup_item_value, remote_vpn_location]) + ',' + (remote_vpn_interface if remote_vpn_interface is not None else '')
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_MSG_VPNS, remote_vpn_uri]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, bridge_virtual_router, bridge_name, remote_vpn_location, remote_vpn_interface, remote_vpn, settings=None):
        # POST /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteMsgVpns
        defaults = {
            'msgVpnName': vpn,
            'remoteMsgVpnLocation': remote_vpn_location,
            **({'remoteMsgVpnInterface': remote_vpn_interface} if remote_vpn_interface is not None else {})
        }
        mandatory = {
            'bridgeName': bridge_name,
            self.LOOKUP_ITEM_KEY: remote_vpn
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        bridge_uri = ','.join([bridge_name, bridge_virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_MSG_VPNS]
        return su.make_post_request(solace_config, path_array, data)

    def update_func(self, solace_config, vpn, bridge_virtual_router, bridge_name, remote_vpn_location, remote_vpn_interface, lookup_item_value, settings=None):
        # PATH /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteMsgVpns/{remoteMsgVpnName},{remoteMsgVpnLocation},{remoteMsgVpnInterface}
        bridge_uri = ','.join([bridge_name, bridge_virtual_router])
        remote_vpn_uri = ','.join([lookup_item_value, remote_vpn_location]) + ',' + (remote_vpn_interface if remote_vpn_interface is not None else '')
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_MSG_VPNS, remote_vpn_uri]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, bridge_virtual_router, bridge_name, remote_vpn_location, remote_vpn_interface, lookup_item_value):
        # DELETE /msgVpns/{msgVpnName}/bridges/{bridgeName},{bridgeVirtualRouter}/remoteMsgVpns/{remoteMsgVpnName},{remoteMsgVpnLocation},{remoteMsgVpnInterface}
        bridge_uri = ','.join([bridge_name, bridge_virtual_router])
        remote_vpn_uri = ','.join([lookup_item_value, remote_vpn_location]) + ',' + (remote_vpn_interface if remote_vpn_interface is not None else '')
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.BRIDGES, bridge_uri, su.BRIDGES_REMOTE_MSG_VPNS, remote_vpn_uri]
        return su.make_delete_request(solace_config, path_array, None)


def run_module():
    module_args = dict(
        name=dict(type='str', required=True, aliases=['remote_msg_vpn_name']),
        bridge_name=dict(type='str', required=True),
        bridge_virtual_router=dict(type='str', default='auto', choices=['primary', 'backup', 'auto'], aliases=['virtual_router']),
        remote_vpn_location=dict(type='str', required=True),
        remote_vpn_interface=dict(type='str', default=None, required=False)
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

    solace_task = SolaceBridgeRemoteVpnTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
