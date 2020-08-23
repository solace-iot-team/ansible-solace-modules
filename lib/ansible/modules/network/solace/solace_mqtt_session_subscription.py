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
import traceback
HAS_IMPORT_ERROR = False
IMPORT_ERR_TRACEBACK = None
try:
    import xmltodict
except ImportError:
    HAS_IMPORT_ERROR = True
    IMPORT_ERR_TRACEBACK = traceback.format_exc()

DOCUMENTATION = '''
---
module: solace_mqtt_session_subscription

short_description: Configure a MQTT Session Subscription object.

version_added: "2.9.10"

description:
- "Configure a MQTT Session Subscription object. Allows addition, removal and update of a MQTT Session Subscription object in an idempotent manner."
notes:
- >
    Depending on the Broker version, a QoS=1 subscription results in the 'magic queue' ('#mqtt/{client_id}/{number}') to
    have ingress / egress ON or OFF. Module uses SEMP v1 <no><shutdown><full/> to ensure they are ON.
- "Reference: U(https://docs.solace.com/API-Developer-Online-Ref-Documentation/swagger-ui/config/index.html#/mqttSession/createMsgVpnMqttSessionSubscription)."

options:
  name:
    description: The subscription topic. Maps to 'subscriptionTopic' in the API.
    type: str
    required: true
    aliases: [mqtt_session_subscription_topic, topic]
  mqtt_session_client_id:
    description: The MQTT session client id. Maps to 'mqttSessionClientId' in the API.
    type: str
    required: true
    aliases: [client_id, client]

extends_documentation_fragment:
- solace.broker
- solace.vpn
- solace.virtual_router
- solace.settings
- solace.state

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''

    - name: Add / Update subscription
      solace_mqtt_session_subscription:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        msg_vpn: "{{ vpn }}"
        virtual_router: "{{ virtual_router }}"
        client_id: "{{ mqtt_session_item.mqttSessionClientId }}"
        topic: "test/v1/event/+"
        state: present

    - name: Update subscription
      solace_mqtt_session_subscription:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        msg_vpn: "{{ vpn }}"
        virtual_router: "{{ virtual_router }}"
        client_id: "{{ mqtt_session_item.mqttSessionClientId }}"
        topic: "test/+/#"
        settings:
          subscriptionQos: 1
        state: present

    - name: Delete subscription
      solace_mqtt_session_subscription:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        msg_vpn: "{{ vpn }}"
        virtual_router: "{{ virtual_router }}"
        client_id: "{{ mqtt_session_item.mqttSessionClientId }}"
        topic: "test/v1/#"
        state: absent

'''

RETURN = '''
response:
    description: The response from the Solace Sempv2 request.
    type: dict
'''


class SolaceMqttSessionSubscriptionTask(su.SolaceTask):

    LOOKUP_ITEM_KEY = 'subscriptionTopic'

    def __init__(self, module):
        sc.module_fail_on_import_error(module, HAS_IMPORT_ERROR, IMPORT_ERR_TRACEBACK)
        su.SolaceTask.__init__(self, module)

    def get_args(self):
        return [self.module.params['msg_vpn'], self.module.params['mqtt_session_client_id'], self.module.params['virtual_router']]

    def lookup_item(self):
        return self.module.params['name']

    def get_magic_queue(self, where_name, vpn):
        request = {
            'rpc': {
                'show': {
                    'queue': {
                        'name': where_name,
                        'vpn-name': vpn,
                    }
                }
            }
        }
        list_path_array = ['rpc-reply', 'rpc', 'show', 'queue', 'queues', 'queue']
        return sc.execute_sempv1_get_list(self.solace_config, request, list_path_array)

    def execute_queue_no_shutdown(self, queue_name, vpn):
        request = {
            'rpc': {
                'message-spool': {
                    'vpn-name': vpn,
                    'queue': {
                        'name': queue_name,
                        'no': {
                            'shutdown': {
                                'full': None
                            }
                        }
                    }
                }
            }
        }
        xml_data = xmltodict.unparse(request)
        ok, semp_resp = sc.make_sempv1_post_request(self.solace_config, xml_data)
        if not ok:
            resp = dict(request=xml_data, response=semp_resp)
        else:
            resp = semp_resp
        return ok, resp

    def get_func(self, solace_config, vpn, client_id, virtual_router, lookup_item_value):
        # GET /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions/{subscriptionTopic}
        uri_ext = ','.join([client_id, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.MQTT_SESSIONS, uri_ext, su.MQTT_SESSION_SUBSCRIPTIONS, lookup_item_value]
        return su.get_configuration(solace_config, path_array, self.LOOKUP_ITEM_KEY)

    def create_func(self, solace_config, vpn, client_id, virtual_router, topic, settings=None):
        # POST /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions
        defaults = {
            'msgVpnName': vpn,
            'mqttSessionClientId': client_id,
            'mqttSessionVirtualRouter': virtual_router
        }
        mandatory = {
            self.LOOKUP_ITEM_KEY: topic
        }
        data = su.merge_dicts(defaults, mandatory, settings)
        uri_ext = ','.join([client_id, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.MQTT_SESSIONS, uri_ext, su.MQTT_SESSION_SUBSCRIPTIONS]
        ok, resp = su.make_post_request(solace_config, path_array, data)
        if not ok:
            return False, resp
        # QoS==1? ==> ensure magic queue is ON/ON
        if settings and settings['subscriptionQos'] == 1:
            # search = "#mqtt/" + client_id + "/does-not-exist"
            search = "#mqtt/" + client_id + "/*"
            ok_gmq, resp_gmq = self.get_magic_queue(search, vpn)
            if not ok_gmq:
                resp['error'] = dict(
                    msg="error retrieving magic queue: {}".format(search),
                    details=resp_gmq
                )
                return False, resp
            elif len(resp_gmq) != 1:
                resp['error'] = dict(
                    msg="could not find magic queue: {}".format(search)
                )
                return False, resp
            # make sure magic queue is ON/ON
            # depending on Broker version, no-shutdown is allowed or not.
            # here: ignore error
            mq_name = resp_gmq[0]['name']
            ok_no_shut, resp_no_shut = self.execute_queue_no_shutdown(mq_name, vpn)
            # if not ok_no_shut:
            #     resp['error'] = dict(
            #         msg="error executing no-shutdown for magic queue: {}".format(mq_name),
            #         details=resp_no_shut
            #     )
            #     return False, resp
        return True, resp

    def update_func(self, solace_config, vpn, client_id, virtual_router, lookup_item_value, settings=None):
        # PATCH /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions/{subscriptionTopic}
        uri_ext = ','.join([client_id, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.MQTT_SESSIONS, uri_ext, su.MQTT_SESSION_SUBSCRIPTIONS, lookup_item_value]
        return su.make_patch_request(solace_config, path_array, settings)

    def delete_func(self, solace_config, vpn, client_id, virtual_router, lookup_item_value):
        # DELETE /msgVpns/{msgVpnName}/mqttSessions/{mqttSessionClientId},{mqttSessionVirtualRouter}/subscriptions/{subscriptionTopic}
        uri_ext = ','.join([client_id, virtual_router])
        path_array = [su.SEMP_V2_CONFIG, su.MSG_VPNS, vpn, su.MQTT_SESSIONS, uri_ext, su.MQTT_SESSION_SUBSCRIPTIONS, lookup_item_value]
        return su.make_delete_request(solace_config, path_array, None)


def run_module():
    module_args = dict(
        name=dict(type='str', aliases=['mqtt_session_subscription_topic', 'topic'], required=True),
        mqtt_session_client_id=dict(type='str', aliases=['client_id', 'client'], required=True),
    )
    arg_spec = su.arg_spec_broker()
    arg_spec.update(su.arg_spec_vpn())
    arg_spec.update(su.arg_spec_virtual_router())
    arg_spec.update(su.arg_spec_crud())
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    solace_task = SolaceMqttSessionSubscriptionTask(module)
    result = solace_task.do_task()

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
