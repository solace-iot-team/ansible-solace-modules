# Ansible Modules for Solace PubSub+ Event Brokers SEMP(v2) REST API

Ansible modules to configure [Solace PubSub+ Event Brokers](https://solace.com/products/event-broker/) with [SEMP v2](https://docs.solace.com/SEMP/Using-SEMP.htm).

## Links
* [Ansible Solace Samples](https://github.com/solace-iot-team/ansible-solace-samples): Sample projects and documentation.
* [Issues & Help](https://github.com/solace-iot-team/ansible-solace/issues)
* [Release Notes](./ReleaseNotes.md)

# Using `ansible-solace` in your Project

Sample projects and documentation: [Ansible Solace Samples](https://github.com/solace-iot-team/ansible-solace-samples).

# Developing Modules

## Install

Install ansible & python3.
Check that python points to the right version:
````bash
python -V   # ==> must be >=3.6
````

Install / upgrade ansible-solace:
````bash
pip3 install ansible-solace
````

**Package location:**

Get the location of the package:
````bash
pip3 show ansible-solace

Name: ansible-solace
...
Location: {your-install-path}/site-packages
...
````
If your Ansible install location is different to the ansible-solace package, you have to tell Ansible about these modules.
You can find a description here: [Adding modules and plugins locally](https://docs.ansible.com/ansible/latest/dev_guide/developing_locally.html#adding-a-module-locally)
or you can set the `ANSIBLE_MODULE_UTILS` and `ANSIBLE_LIBRARY` environment variables:

```bash
export ANSIBLE_MODULE_UTILS={your-install-path}/ansible/module_utils
export ANSIBLE_LIBRARY={your-install-path}/ansible/modules

# check:
ansible-doc -l | grep solace
```

_Note: You can also have a look at [set-ansible-env.sh](./set-ansible-env.sh)._

**Python interpreter:**

Depending on your OS/environment, you may have to set the python interpreter explicitly.
For example, set the `ANSIBLE_PYTHON_INTERPRETER` variable:
````bash
# find the location of your python installation
brew info python
# or
which python
# set the location
# e.g.
export ANSIBLE_PYTHON_INTERPRETER=/usr/local/bin/python
````


## Run the Example

### Pre-requisites

* a Solace PubSub+ Broker (Cloud or Software)
* credentials for the admin (sempv2) interface

### Configure the Inventory

Copy the example below to `brokers.inventory.json` and enter the values:

````json
{
  "all": {
    "hosts": {
      "{your broker name}": {
        "ansible_connection": "local",
        "sempv2_host": "{host, e.g. xxxx.messaging.solace.cloud}",
        "sempv2_port": 943,
        "sempv2_is_secure_connection": true,
        "sempv2_username": "{admin user name}",
        "sempv2_password": "{admin user password}",
        "sempv2_timeout": "60",
        "vpn": "{message vpn}"
      }
    }
  }
}
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
ansible-playbook -i brokers.inventory.json setup-queue.playbook.yml
````

# MODULES

List all modules:
````bash
ansible-doc -l | grep solace
````

# Writing New Modules

[See Guide to Creating new Modules.](./GuideCreateModule.md)

# Enhancements

[See Potential Enhancements](./Enhancements.md).

---
The End.
