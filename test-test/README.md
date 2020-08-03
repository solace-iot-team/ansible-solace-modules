# Tests

## Run all Tests

Brokers:
- 1 cloud instance
  - must exist
  - create API token and add to `./lib/broker.inventories/cloud.broker.inventory.json`
- pulls down multiple versions of Solace PubSub+ standard docker images

### Configure Solace Cloud Instance

````bash
cd ./lib/broker.inventories
cp template.cloud.broker.inventory.json cloud.broker.inventory.json
vi cloud.broker.inventory.json

>>> enter values

````

### Run Tests

````bash
./run.sh
````

---
The End.
