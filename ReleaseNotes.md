# Release Notes

## Version: 0.7.7
Release Purpose: New Module.

**New:**
* **solace_get_vpn_clients**

## Version: 0.7.6
Release Purpose: Test Framework Enhancements.
#### Test Framework:
      updated:
        - added prepare & teardown for
          - tests-1-broker
          - tests-2-brokers

## Version: 0.7.5
Release Purpose: Enhancement to solace_cloud_get_facts.
#### Modules:
      updated:
        - solace_cloud_get_facts:
          - added mandatory 'meta' argument to function: get_formattedHostInventory

## Version: 0.7.4
Release Purpose: Maintenance release.
#### Framework:
      updated:
        - fixed import error solace_common.py in case of ansible interpreter version issue

## Version: 0.7.3
Release Purpose: Maintenance release.
#### Modules:
      updated:
        - solace_client_profile:
          - added elidingEnabled=false to default values for Solace Cloud
#### Framework:
      updated:
        - added request timeout handling
        - fixed python imports & interpreter checking

## Version: 0.7.2

Release Purpose: Maintenance release.

### Modules:

      new:
        - solace_get_magic_queues
      updated:
        - solace_mqtt_session_subscription:
          - ensures that the magic queue for a qos=1 subscription is ON, regardless of Broker version
          - bug fix for MQTT topic wildcards chars # and +

## Version: 0.7.1

Release Purpose: Maintenance release.

### Modules:

      new:
        - none.
      updated:
        - solace_get_facts:
          - new function: get_allClientConnectionDetails

## Version: 0.7.0

Release Purpose: Create/Delete Solace Cloud Services

### Modules:

      new:
        - solace_cloud_service
        - solace_cloud_get_service
        - solace_cloud_account_gather_facts
        - solace_cloud_get_facts
      updated:
        - none.

### Framework:
    - solace_cloud_utils: new utility module for solace cloud
    - solace_common: new common functions across solace_cloud_utils and solace_utils

## Version: 0.6.1

Release Purpose: Maintenance Release & Links to `ansible-solace-samples`

    - pypi home page: references samples github project
    - logging: new env var: ANSIBLE_SOLACE_LOG_PATH: the log filename
    - README now points to ansible-solace-samples
    - examples: marked as deprecated

## Version: 0.6.0

Release Purpose: Bridge Setup: local <-> Solace Cloud.

### Versions
|SEMP API Versions|Ansible Version| Python Version|
|--|--|---|
|2.13 to 2.17 | >=2.9.10   | >= 3.6  |

### Modules
    new:
      - solace_get_bridges
      - solace_get_bridge_remote_vpns
      - solace_get_bridge_remote_subscriptions
      - solace_get_available

    updated:
      - solace_bridge_remote_vpn - update: added support for optional parameter: remoteMsgVpnInterface
      - solace_get_* - update: monitor api added
        - solace_get_client_profiles
        - solace_get_client_usernames
        - solace_get_mqtt_session_subscriptions
        - solace_get_mqtt_session
        - solace_get_queues

    gather solace facts / getting solace facts:
        - solace_gather_facts: new, was previously: solace_get_facts
            - about api - as before
            - service - retrieves the service info. supports solace cloud & brokers
            - virtual router - retrieves virtual router from brokers via SEMP v1
        - solace_get_facts:
            - new
            - convenience functions to retrieve facts gathered by solace_gather_facts
            - retrieve facts from ansible_facts.solace
              - by field name
              - by convenience function
### Framework
    - added monitor api option for all solace_get_* modules
    - added support for SEMP V1 calls and XML return parsing
    - added graceful handling of import errors
    - added check of python version >= 3.6
### Tests
    - solace_bridges - new
    - solace_facts - new
    - solace_get_* - update: added monitor api call
### Test Framework
    - refactored to be agnostic of directory
    - created categories of tests: 1-broker, 2-brokers, general
### Other
    - new python module required: xmltodict>=0.12.0

## Version: 0.5.0
### Modules
    new:
      - solace_get_client_profiles
    updated:
      - solace_client_profile: added Solace Cloud API
          1) Create API Token Manually in Solace Cloud Console
          2) Set in inventory:
              - api_token
              - service_id
### Framework
    - added Solace Cloud API functionality
### Tests
    new:
      - solace_client_profile
      - solace_get_client_profiles
### Test Framework
    - none
### Other
    - none

---------------------
## Version: 0.4.1
### New Modules
    - none
### Removed Modules
    - none
### Framework Changes
    - none
### Test Framework Changes
    - added choice to run tests against dev or installed package
### Test Updates
    -none
### Other Updates
    - minor changes to Readmes
---------------------

## Version: 0.4.0
### New Modules
    - solace_mqtt_session
    - solace_mqtt_session_subscription
    - solace_get_mqtt_sessions
    - solace_get_mqtt_session_subscriptions
### Removed Modules
    - none
### Framework Changes
    - none
### Tests
    - solace_mqtt_session:
      - covers new modules
---------------------
## Version: 0.3.0
### New Modules
    - solace_get_queues
    - solace_get_client_usernames
    - solace_client_username
### Removed Modules
    - solace_client
### Framework Changes
    - none
#### solace_utils
- framework for get_list() - to support get_xxxx modules
- modularized argument spec:
````python
def arg_spec_broker():
def arg_spec_vpn():
def arg_spec_settings():
def arg_spec_semp_version():
def arg_spec_state():
def arg_spec_name():
def arg_spec_crud():
def arg_spec_query():
````
#### Document Fragments
Introduced `ansible/plugins/doc_fragments/solace.py`. Modularized documentation fragments.

## Version: 0.2.1

### New Modules
    - solace_get_facts
    - solace_acl_publish_topic_exception
    - solace_acl_subscribe_topic_exception
    - solace_acl_client_connect_exception
    - solace_rdp_rest_consumer_trusted_cn
    - solace_queue_subscription
    - solace_topic_endpoint
    - solace_dmr_cluster
    - solace_dmr_cluster_link
    - solace_dmr_cluster_link_remote_address
    - solace_dmr_cluster_link_trusted_cn

#### Module: `solace_get_facts`

Some modules require the Semp API version number to switch behaviour depending on the version.
This module uses the /about/api resource to retrieve the version number and add it to `ansible_facts`.
Subsequent modules can use the output stored in `ansible_facts`.
See example playbooks:

- [Solace Get Facts Playbook](examples/solace_get_facts.playbook.yml)
- [ACL Profile Playbook](examples/solace_acl_profile.playbook.yml)

### Removed Modules

    - solace_acl_publish
    - solace_acl_publish_exception
    - solace_acl_subscribe
    - solace_acl_subscribe_exception
    - solace_acl_connect
    - solace_rdp_rest_consumer_trusted_common_name
    - solace_subscription
    - solace_topic
    - solace_dmr
    - solace_link
    - solace_link_trusted_cn

### Framework Changes

#### solace_utils

    - modules can now switch based on semp API version
    - logging (ansible-solace.log) now controllable via env var: ANSIBLE_SOLACE_ENABLE_LOGGING=[true|false]
    - added 'compose_module_args' so each module only has to provide their own specific arguments


---
The End.
