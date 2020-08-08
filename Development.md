# Developing `ansible-solace`

## Install
- Python >= 3.6
- Ansible >= 2.10
- Fork & Clone `ansible-solace`

### Set Python for Ansible
````bash
export ANSIBLE_PYTHON_INTERPRETER={your-python}
# for example:
export ANSIBLE_PYTHON_INTERPRETER=/usr/local/bin/python
````

### Set `ansible-solace` Location

```bash
export ANSIBLE_MODULE_UTILS={your-clone-path}/lib/ansible/module_utils
export ANSIBLE_LIBRARY={your-clone-path}/lib/ansible/modules

# check:
ansible-doc -l | grep solace
```

_Note: You can also have a look at [set-ansible-env.sh](./set-ansible-env.sh)._


## Run the Example

### Pre-requisites

* a Solace PubSub+ Broker (Cloud or Software)
* credentials for the admin (sempv2) interface

### Configure the Inventory

Copy the example below to `brokers.inventory.yml` and enter the values:

````yaml
---
all:
  hosts:
    local:
      ansible_connection: local
      sempv2_host: localhost
      sempv2_port: 8080
      sempv2_is_secure_connection: false
      sempv2_username: admin
      sempv2_password: admin
      sempv2_timeout: '60'
      virtual_router: primary
    # solace-cloud-template:
    #   meta:
    #     account: "{account-name}"
    #     service: "{service-name}"
    #   ansible_connection: local
    #   solace_cloud_api_token: "{api-token}"
    #   solace_cloud_service_id: "{service-id}"
    #   sempv2_host: "{host}.messaging.solace.cloud"
    #   sempv2_port: 943
    #   sempv2_is_secure_connection: true
    #   sempv2_username: "{username}"
    #   sempv2_password: "{password}"
    #   sempv2_timeout: '60'
    #   virtual_router: primary


###
# The End.
````

Copy the example below to `setup-queue.playbook.yml`:

````yaml
-
  name: Setup A Queue with a Subscription

  hosts: all

  module_defaults:
    solace_queue_subscription:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"
    solace_queue:
      host: "{{ sempv2_host }}"
      port: "{{ sempv2_port }}"
      secure_connection: "{{ sempv2_is_secure_connection }}"
      username: "{{ sempv2_username }}"
      password: "{{ sempv2_password }}"
      timeout: "{{ sempv2_timeout }}"
      msg_vpn: "{{ vpn }}"

  tasks:

    - name: Add / update the queue
      solace_queue:
        name: "my-queue"
        settings:
          egressEnabled: true
          ingressEnabled: true
          permission: "consume"
        state: present

    - name: Create subscription on queues
      solace_queue_subscription:
        queue: "my-queue"
        name: "my/subscription/topic"
        state: present

````
### Run the playbook

````bash
ansible-playbook -i brokers.inventory.yml setup-queue.playbook.yml
````

# MODULES

List all existing modules:
````bash
ansible-doc -l | grep solace
````

# Writing New Modules

[See Guide to Creating new Modules.](./GuideCreateModule.md)

# Enhancements

[See Potential Enhancements](./Enhancements.md).

---
The End.
