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

import ansible.module_utils.network.solace.solace_common as sc
from ansible.module_utils.basic import AnsibleModule
import traceback
HAS_IMPORT_ERROR = False
IMPORT_ERR_TRACEBACK = None
try:
    from ansible.errors import AnsibleError
    from urllib.parse import urlparse
    import json
    from json.decoder import JSONDecodeError
except ImportError:
    HAS_IMPORT_ERROR = True
    IMPORT_ERR_TRACEBACK = traceback.format_exc()


DOCUMENTATION = '''
---
module: solace_cloud_get_facts

short_description: Provides convenience functions to access solace facts gathered with M(solace_cloud_account_gather_facts).

description: >
    Provides convenience functions to access Solace Cloud service facts gathered with M(solace_cloud_account_gather_facts).
    Call M(solace_cloud_account_gather_facts) first.

options:
  from_dict:
    description: The JSON object (dict) which holds the facts. This is direct result from the GET {service} call.
    required: True
    type: dict
  field_funcs:
    description: List of pre-built field functions that retrieve values from the 'from_dict'.
    required: True
    type: list
    default: []
    elements: str
    choices:
      - get_serviceSEMPManagementEndpoints
    functions:
      get_serviceSEMPManagementEndpoints:
        description: >
            Retrieves the SEMP management endpoint.

seealso:
- module: solace_cloud_account_gather_facts
- module: solace_cloud_get_service

author:
  - Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
'''

EXAMPLES = '''

    - name: "Get Service: {{ sc_service.name }}"
      solace_cloud_get_service:
        api_token: "{{ api_token_all_permissions }}"
        service_id: "{{ sc_service.serviceId }}"
      register: result

    - name: "Set Fact: Solace Service Details"
      set_fact:
        sc_service_details: "{{ result.response }}"
        - name: "Get Semp Management Endpoints for: {{ sc_service.name }}"
          solace_cloud_get_facts:
            from_dict: "{{ sc_service_details }}"
            field_funcs:
              - get_serviceSEMPManagementEndpoints
          register: semp_enpoints_facts

    - name: "Save Solace Cloud Service SEMP Management Endpoints to File"
      local_action:
        module: copy
        content: "{{ semp_enpoints_facts | to_nice_json }}"
        dest: "./tmp/facts.solace_cloud_service.{{ sc_service.name }}.semp.json"

    - name: "Set Fact: Solace Service SEMP"
      set_fact:
        sempv2_host: "{{ semp_enpoints_facts.facts.serviceManagementEndpoints.SEMP.SecuredSEMP.uriComponents.host }}"
        sempv2_port: "{{ semp_enpoints_facts.facts.serviceManagementEndpoints.SEMP.SecuredSEMP.uriComponents.port }}"
        sempv2_is_secure_connection: True
        sempv2_username: "{{ semp_enpoints_facts.facts.serviceManagementEndpoints.SEMP.username }}"
        sempv2_password: "{{ semp_enpoints_facts.facts.serviceManagementEndpoints.SEMP.password }}"
        sempv2_timeout: 60

    - name: "Gather Solace Facts from Service"
      solace_gather_facts:
        host: "{{ sempv2_host }}"
        port: "{{ sempv2_port }}"
        secure_connection: "{{ sempv2_is_secure_connection }}"
        username: "{{ sempv2_username }}"
        password: "{{ sempv2_password }}"
        timeout: "{{ sempv2_timeout }}"
        solace_cloud_api_token: "{{ api_token_all_permissions }}"
        solace_cloud_service_id: "{{ sc_service.serviceId }}"

    - name: "Show ansible_facts.solace"
      debug:
        msg:
          - "ansible_facts.solace:"
          - "{{ ansible_facts.solace }}"

    - name: "Save Solace Cloud Service Facts to File"
      local_action:
        module: copy
        content: "{{ ansible_facts.solace | to_nice_json }}"
        dest: "./tmp/solace_facts.solace_cloud_service.{{ sc_service.name }}.json"
'''

RETURN = '''

    rc:
        description: return code, either 0 (ok), 1 (not ok)
        type: int
    msg:
        description: error message if not ok
        type: str
    facts:
        description: The facts retrieved from the input.
        type: complex

'''


class SolaceCloudGetFactsTask():

    def __init__(self, module):
        sc.module_fail_on_import_error(module, HAS_IMPORT_ERROR, IMPORT_ERR_TRACEBACK)
        self.module = module
        return

    FIELD_FUNCS = [
        "get_serviceSEMPManagementEndpoints"
    ]

    def get_facts(self):
        from_dict = self.module.params['from_dict']
        field_funcs = self.module.params['field_funcs']
        # either fields or field_funcs must have at least one element
        if field_funcs is None or len(field_funcs) == 0:
            return False, "No 'field_funcs' provided."
        for field_func in field_funcs:
            exists = (True if field_func in self.FIELD_FUNCS else False)
            if not exists:
                return False, "Unknown field_func='{}'. Valid field functions are: {}.".format(field_func, str(self.FIELD_FUNCS))

        search_object = from_dict
        facts = dict()
        try:
            for field_func in field_funcs:
                field, value = globals()[field_func](search_object)
                facts[field] = value
        except AnsibleError as e:
            try:
                e_msg = json.loads(str(e))
            except JSONDecodeError:
                e_msg = [str(e)]
            ex_msg = [
                "field_func:'{}'".format(field_func),
                e_msg
            ]
            raise AnsibleError(json.dumps(ex_msg))

        return True, facts

#
# field funcs
#


def get_serviceSEMPManagementEndpoints(search_dict):
    eps = dict(
        SEMP=dict(
            SecuredSEMP=dict()
        )
    )
    mgmt_protocols_dict = _get_field(search_dict, 'managementProtocols')
    if mgmt_protocols_dict is None:
        raise AnsibleError("Could not find '{}' in 'from_dict'.".format('managementProtocols'))
    semp_dict = _find_nested_dict(mgmt_protocols_dict, field="name", value='SEMP')
    if semp_dict is None:
        raise AnsibleError("Could not find 'name={}' in 'managementProtocols' in 'from_dict'.".format('SEMP'))
    sec_semp_end_point_dict = _get_protocol_endpoint(semp_dict, field='name', value='Secured SEMP Config')
    sec_semp_uri = _get_protocol_endpoint_uri(sec_semp_end_point_dict)
    t = urlparse(sec_semp_uri)
    sec_semp_protocol = t.scheme
    sec_semp_host = t.hostname
    sec_semp_port = t.port
    # put the dict together
    sec_semp = dict()
    sec_semp_ucs = dict()
    sec_semp_ucs['protocol'] = sec_semp_protocol
    sec_semp_ucs['host'] = sec_semp_host
    sec_semp_ucs['port'] = sec_semp_port
    sec_semp['uriComponents'] = sec_semp_ucs
    sec_semp['uri'] = sec_semp_uri
    eps['SEMP']['SecuredSEMP'] = sec_semp
    eps['SEMP']['username'] = semp_dict['username']
    eps['SEMP']['password'] = semp_dict['password']
    return 'serviceManagementEndpoints', eps

#
# field func helpers
#


def _get_protocol_endpoint(search_dict, field, value):
    element = 'endPoints'
    if element not in search_dict:
        raise AnsibleError("Could not find '{}' in dict:{}.".format(element, json.dumps(search_dict)))
    end_points = search_dict[element]
    if len(end_points) == 0:
        raise AnsibleError("Empty list:'{}' in dict:{}.".format(element, json.dumps(search_dict)))
    end_point_dict = _find_nested_dict(end_points, field, value)
    if end_point_dict is None:
        raise AnsibleError("Could not find end point with '{}={}'.".format(field, value))
    return end_point_dict


def _get_protocol_endpoint_uri(search_dict):
    element = 'uris'
    if element not in search_dict:
        errs = [
            "Could not find '{}' in end point:".format(element),
            search_dict
        ]
        raise AnsibleError(json.dumps(errs))
    if len(search_dict['uris']) != 1:
        errs = [
            "'{}' list contains != 1 elements in end point:".format(element),
            "{}".format(json.dumps(search_dict))
        ]
        raise AnsibleError(errs)
    return search_dict['uris'][0]


def _find_nested_dict(search_dict, field, value):
    if isinstance(search_dict, dict):
        if field in search_dict and search_dict[field] == value:
            return search_dict
        for key in search_dict:
            item = _find_nested_dict(search_dict[key], field, value)
            if item is not None:
                return item
    elif isinstance(search_dict, list):
        for element in search_dict:
            item = _find_nested_dict(element, field, value)
            if item is not None:
                return item
    return None


def _get_field(search_dict, field):
    if isinstance(search_dict, dict):
        if field in search_dict:
            return search_dict[field]
        for key in search_dict:
            item = _get_field(search_dict[key], field)
            if item is not None:
                return item
    elif isinstance(search_dict, list):
        for element in search_dict:
            item = _get_field(element, field)
            if item is not None:
                return item
    return None


def run_module():
    module_args = dict(
        from_dict=dict(type='dict', required=True),
        field_funcs=dict(type='list', required=True, elements='str')
    )
    arg_spec = dict()
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        facts=dict(),
        rc=0
    )

    solace_task = SolaceCloudGetFactsTask(module)
    try:
        ok, resp = solace_task.get_facts()
        if not ok:
            result['rc'] = 1
            module.fail_json(msg=resp, **result)
    except AnsibleError as e:
        ex = traceback.format_exc()
        try:
            ex_msg = json.loads(str(e))
        except JSONDecodeError:
            ex_msg = [str(e)]
        msg = ["Pls raise an issue including the full traceback. (hint: use -vvv)"] + ex_msg + ex.split('\n')
        module.fail_json(msg=msg, exception=ex)

    result['facts'] = resp
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
