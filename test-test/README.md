# Tests

Run all tests.

## Pre-requisites

#### Brokers:
- 1 cloud instance
  - must exist
  - create API token and add to `./lib/broker.inventories/cloud.broker.inventory.json`
- pulls down multiple versions of Solace PubSub+ standard docker images

#### Others:
  - Docker
  - Python 3
  - Ansible

### Configure Solace Cloud Instance

````bash
cd ./lib/broker.inventories
cp template.cloud.broker.inventory.json cloud.broker.inventory.json
vi cloud.broker.inventory.json

>>> enter values

````

### Set the Ansible Python Interpreter

Required Python version: >= 3.6

````bash
export ANSIBLE_PYTHON_INTERPRETER={path to python}

# example:
export ANSIBLE_PYTHON_INTERPRETER=/usr/local/bin/python

````

## Run Tests

````bash
./run.sh
````

---
The End.
