# Tests against 1 Broker




## Run Tests

Run tests interactively.

````bash
# adjust interactive tests
vi ./run.sh

# run interactive tests
./run.sh
````

---
The End.


## Run all Tests
Multiple brokers:
- 1 cloud instance
- pulls down multiple versions of pubsub+ standard docker images

````bash
# run all tests
./run.sh
````

## Run Single Test

````bash
# start & stop a local broker
./start.local.broker.sh
./stop.local.broker.sh
````

````bash
cd <test-directory>

./run.sh
````
