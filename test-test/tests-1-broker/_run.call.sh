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

SCRIPT_PATH=$(cd $(dirname "$0") && pwd);
source $AS_TEST_HOME/lib/functions.sh

##############################################################################################################################
# Configure
export ANSIBLE_SOLACE_ENABLE_LOGGING=false

brokerDockerImagesFile="$AS_TEST_HOME/lib/brokerDockerImages.json"
localBrokerInventoryFile="$AS_TEST_HOME/lib/broker.inventories/local.broker.inventory.json"
cloudBrokerInventoryFile="$AS_TEST_HOME/lib/broker.inventories/cloud.broker.inventory.json"

ansibleSolaceTests=(
  "solace_get_available"
  "solace_get_vpn_clients"
  "solace_facts"
  "solace_rdp"
  "solace_queue"
  "solace_mqtt_session"
  "solace_get_queues"
  "solace_get_client_usernames"
  "solace_get_client_profiles"
  "solace_acl_profile"
  "solace_client_profile"
)

##############################################################################################################################
# prepare test
  echo ">>> preparing test ..."
  runScript="$SCRIPT_PATH/prepare/_run.call.sh"
  $runScript
  if [[ $? != 0 ]]; then echo ">>> ERROR:$runScript"; echo; exit 1; fi
##############################################################################################################################
# Run Cloud

  brokerInventoryFile=$(assertFile $cloudBrokerInventoryFile) || exit
  for ansibleSolaceTest in ${ansibleSolaceTests[@]}; do
    runScript="$SCRIPT_PATH/$ansibleSolaceTest/_run.call.sh $brokerInventoryFile"
    echo; echo "##############################################################################################################"
    echo "# test: $ansibleSolaceTest"
    echo "# cloud broker: "$(cat $brokerInventoryFile | jq -r ".[].hosts[].meta")
    echo "# calling: $runScript"
    $runScript
    if [[ $? != 0 ]]; then echo ">>> ERROR:$runScript"; echo; exit 1; fi
  done

##############################################################################################################################
# Run Local
brokerInventoryFile=$localBrokerInventoryFile
brokerDockerImages=$(cat $brokerDockerImagesFile | jq -r ".brokerDockerImages[]")
for brokerDockerImage in ${brokerDockerImages[@]}; do
  $AS_TEST_HOME/lib/_start.local.broker.sh $brokerDockerImage
    if [[ $? != 0 ]]; then echo ">>> ERROR starting local broker: $brokerDockerImage"; echo; exit 1; fi
  $AS_TEST_HOME/tests-embeddable/wait-until-broker-available/_run.call.sh $localBrokerInventoryFile
    if [[ $? != 0 ]]; then echo ">>> ERROR: $SCRIPT_PATH"; echo; exit 1; fi
  for ansibleSolaceTest in ${ansibleSolaceTests[@]}; do
      runScript="$SCRIPT_PATH/$ansibleSolaceTest/_run.call.sh $brokerInventoryFile"
      echo; echo "##############################################################################################################"
      echo "# script: $SCRIPT_PATH"
      echo "# test: $ansibleSolaceTest"
      echo "# broker: local"
      echo "# image: $brokerDockerImage"
      echo "# calling: $runScript"
      $runScript
        if [[ $? != 0 ]]; then echo ">>> ERROR:$runScript"; echo; exit 1; fi
    done
done

##############################################################################################################################
# teardown test
echo ">>> tearing down test ..."
runScript="$SCRIPT_PATH/teardown/_run.call.sh"
$runScript
  if [[ $? != 0 ]]; then echo ">>> ERROR:$runScript"; echo; exit 1; fi

###
# The End.
