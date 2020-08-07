# Tests: General

## Pre-requisites

[See ../README](../README)

## Run Tests

Run tests interactively.

````bash
# adjust interactive tests
vi ./run.sh

# run interactive tests
./run.sh
````

## Run Single Test

````bash
# start & stop a local broker
cd {ansible-solace-home}/test-test

./start.local.broker.sh

./stop.local.broker.sh

````

````bash
cd <test-directory>

./run.sh
````

---
The End.
