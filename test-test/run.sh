#!/bin/bash
# ---------------------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
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

clear
echo; echo "##############################################################################################################"
echo

source ./_run.env.sh

##############################################################################################################################
# Choose Environment

# select here or interactively
  #export AS_TEST_RUNNER_ENV="dev"
  #export AS_TEST_RUNNER_ENV="package"

source $AS_TEST_HOME/lib/_run.env.sh $AS_TEST_RUNNER_ENV

##############################################################################################################################
# Configure
brokerDockerImages=(
    "solace/solace-pubsub-standard:9.3.1.28"
    "solace/solace-pubsub-standard:9.5.0.30"
    "solace/solace-pubsub-standard:9.6.0.27"
    "solace/solace-pubsub-standard:latest"
)
runCallDirs=(
  "tests-2-brokers"
  "tests-1-broker"
)
brokerDockerContainerName="pubSubStandardSingleNode"

##############################################################################################################################
# show & wait
x=$(showEnv)
echo; echo "Local Brokers:"; echo
for brokerDockerImage in "${brokerDockerImages[@]}"; do
  echo " - $brokerDockerImage"
done
echo; echo "Broker docker container:"; echo;
echo " name: '$brokerDockerContainerName'"
echo
echo; echo "Solace Cloud:"; echo
scInventory=$(cat $AS_TEST_HOME/lib/broker.inventories/cloud.broker.inventory.json | jq . )
echo $scInventory | jq -r ".all.hosts[].meta"
echo
x=$(wait4Key)

##############################################################################################################################
# prepare brokers

echo "##############################################################################################################"

dockerComposeYmlFile="$AS_TEST_HOME/lib/PubSubStandard_singleNode.yml"
if [ ! -f "$dockerComposeYmlFile" ]; then echo "ERR >>> aborting. $dockerComposeYmlFile does not exist."; exit 1; fi

brokerDockerImageLatest="solace/solace-pubsub-standard:latest"

echo; echo "Removing all docker containers ..."
docker rm -f "$brokerDockerContainerName"
echo "Done."

echo; echo "Removing latest docker image: $brokerDockerImageLatest ..."
docker rmi -f "$brokerDockerImageLatest"
echo "Done."

echo; echo "Pulling all docker images from docker hub..."; echo
for brokerDockerImage in "${brokerDockerImages[@]}"; do
  echo; docker pull $brokerDockerImage
  if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi
done
echo; echo "List of docker images:"; echo
docker images | grep solace/
echo

##############################################################################################################################
# Run tests
# - start container, run tests
#

for brokerDockerImage in "${brokerDockerImages[@]}"; do
  echo; echo "Starting container with image: $brokerDockerImage ..."
  docker rm -f $brokerDockerContainerName
  export brokerDockerImage
  export brokerDockerContainerName
  docker-compose -f $dockerComposeYmlFile up -d
  if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi

  for runCallDir in ${runCallDirs[@]}; do

    runScript="$AS_TEST_HOME/$runCallDir/_run.call.sh"

    echo; echo "##############################################################################################################"
    echo "# Running Tests:"
    echo "# Cloud broker + Local Image: $brokerDockerImage"
    echo "# calling: $runScript"

    $runScript

    if [[ $? != 0 ]]; then echo ">>> ERR:$runScript. aborting."; echo; exit 1; fi

  done

done

echo;
echo "##############################################################################################################"
echo "# All tests completed successfully!"
echo;
##############################################################################################################################
# loop 3:
# - remove all containers, remove all images

echo; echo "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"; echo
echo "! WARNING: NOT REMOVING CONTAINERS NOR IMAGES !"
echo; echo


###
# The End.
