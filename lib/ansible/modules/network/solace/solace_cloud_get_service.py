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

import ansible.module_utils.network.solace.solace_cloud_utils as scu
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: solace_cloud_get_service

version_added: '2.9.11'

short_description: Get the Solace Cloud Service details.

description: Get the Solace Cloud Service details by name or serviceId.

notes:
- "Reference: U(https://docs.solace.com/Solace-Cloud/ght_use_rest_api_services.htm)."

options:
  name:
    description: The name of the service.
    required: false
    type: str
    notes:
        - if name is not provided, service_id must.
  service_id:
    description: The service id.
    required: false
    type: str
    notes:
        - if service_id is not provided, name must.

extends_documentation_fragment:
- solace.solace_cloud_service_config

seealso:
- module: solace_cloud_service

author:
- Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)

'''

EXAMPLES = '''

    - name: "Get service details"
      solace_cloud_get_service:
        api_token: "{{ api_token_all_permissions }}"
        service_id: "{{ sc_service_created_id }}"
      register: get_service_result

    - set_fact:
        sc_service_created_info: "{{ result.response }}"

    - name: "Save Solace Cloud Service Facts to File"
      local_action:
        module: copy
        content: "{{ sc_service_created_info | to_nice_json }}"
        dest: "./tmp/facts.solace_cloud_service.{{ sc_service.name }}.json"

'''

RETURN = '''

rc:
    description: return code, either 0 (ok), 1 (not ok)
    type: int
msg:
    description: error message if not ok
    type: str
response:
    description: The response from the get call. Differs depending on state of service.
    type: complex


'''


class SolaceCloudGetServiceTask(scu.SolaceCloudTask):

    LOOKUP_ITEM_KEY_SERVICE_ID = 'serviceId'
    LOOKUP_ITEM_KEY_NAME = 'name'

    def __init__(self, module):
        scu.SolaceCloudTask.__init__(self, module)
        self._service_id = None
        self.validate_args(*(self.get_args() + self.lookup_item_kv()))
        return

    def lookup_item_kv(self):
        # state=present: name is required, return key=name, value=name
        # state=absent: name or service_id required. service_id takes precedence. return k,v depending on presence
        # return [k, v]
        # fail module on error
        # exception on code error
        if self.module.params['service_id'] is not None:
            return [self.LOOKUP_ITEM_KEY_SERVICE_ID, self.module.params['service_id']]
        elif self.module.params['name'] is not None:
            return [self.LOOKUP_ITEM_KEY_NAME, self.module.params['name']]
        else:
            msg = "Neither key specified: 'service_id' nor 'name'. At least one is required."
            result = dict(changed=False, rc=1)
            self.module.fail_json(msg=msg, **result)
        return

    def validate_args(self, lookup_item_key, lookup_item_value):
        return

    def get(self, sc_config, lookup_item_key, lookup_item_value):
        service_id = None
        if lookup_item_key == self.LOOKUP_ITEM_KEY_NAME:
            # GET https://api.solace.cloud/api/v0/services
            # retrieves a list of services (either 'owned by me' or 'owned by org', depending on permissions)
            path_array = [scu.SOLACE_CLOUD_API_SERVICES_BASE_PATH]
            ok, resp = self.get_configuration(sc_config, path_array, lookup_item_key, lookup_item_value)
            if not ok:
                return False, resp
            # if found, retrieve the full configuration
            if resp is not None:
                if self.LOOKUP_ITEM_KEY_SERVICE_ID in resp:
                    service_id = resp[self.LOOKUP_ITEM_KEY_SERVICE_ID]
                else:
                    raise KeyError("Could not find key:'{}' in Solace Cloud GET services response. Pls raise an issue.".format(self.LOOKUP_ITEM_KEY_SERVICE_ID))
            else:
                return True, None
        elif lookup_item_key == self.LOOKUP_ITEM_KEY_SERVICE_ID:
            service_id = lookup_item_value
        else:
            raise ValueError("unknown lookup_item_key='{}'. pls raise an issue.".format(lookup_item_key))

        # not found
        if not service_id:
            return True, None
        # save service_id
        self._service_id = service_id
        # GET https://api.solace.cloud/api/v0/services/{{serviceId}}
        # retrieves a single service
        path_array = [scu.SOLACE_CLOUD_API_SERVICES_BASE_PATH, service_id]
        return self.get_configuration(sc_config, path_array)

    def get_configuration(self, sc_config, path_array, lookup_item_key=None, lookup_item_value=None):
        """Return ok flag and dict of object if found, otherwise None."""
        ok, resp = scu.make_get_request(sc_config, path_array)
        if not ok:
            return False, resp
        if lookup_item_key and lookup_item_value:
            service = self._find_service(resp, lookup_item_key, lookup_item_value)
        else:
            service = resp
        return True, service

    def _find_service(self, resp, lookup_item_key, lookup_item_value):
        """Return a dict of object if found, otherwise None."""
        if type(resp) is dict:
            value = resp.get(lookup_item_key)
            if value == lookup_item_value:
                return resp
        elif type(resp) is list:
            for item in resp:
                value = item.get(lookup_item_key)
                if value == lookup_item_value:
                    return item
        else:
            raise TypeError("argument 'resp' is not a 'dict' nor 'list' but {}. Pls raise an issue.".format(type(resp)))
        return None


def run_module():

    module_args = dict(
        name=dict(type='str', required=False, default=None),
        service_id=dict(type='str', required=False, default=None)
    )
    arg_spec = scu.arg_spec_solace_cloud()
    # module_args override standard arg_specs
    arg_spec.update(module_args)

    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=True
    )

    result = dict(
        rc=0,
        exists=False,
        changed=False
    )

    solace_task = SolaceCloudGetServiceTask(module)
    ok, resp = solace_task.get(solace_task.sc_config, *solace_task.lookup_item_kv())
    if not ok:
        result['rc'] = 1
        module.fail_json(msg=resp, **result)

    if resp:
        result['exists'] = True
    result['response'] = resp

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

###
# The End.
