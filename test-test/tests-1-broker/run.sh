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
  export AS_TEST_RUNNER_ENV="dev"
  #export AS_TEST_RUNNER_ENV="package"
source $AS_TEST_HOME/lib/_run.env.sh $AS_TEST_RUNNER_ENV

##############################################################################################################################
# Settings

  # export ANSIBLE_SOLACE_ENABLE_LOGGING=false
  export ANSIBLE_SOLACE_ENABLE_LOGGING=true

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

  brokerDockerImagesFile="$AS_TEST_HOME/lib/brokerDockerImages.json"
  localBrokerInventoryFile="$AS_TEST_HOME/lib/broker.inventories/local.broker.inventory.json"
  cloudBrokerInventoryFile="$AS_TEST_HOME/lib/broker.inventories/cloud.broker.inventory.json"

brokerChoices=(
  "local-broker"
  "cloud-broker"
)
brokerChoice=$(chooseFromArray "broker" "${brokerChoices[@]}")
if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi
if [[ $brokerChoice == "local-broker" ]]; then
  brokerInventoryFile=$localBrokerInventoryFile
  brokerDockerImage=$(chooseBrokerDockerImage "$brokerDockerImagesFile")
  if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi
else
  brokerInventoryFile=$cloudBrokerInventoryFile
fi

x=$(showEnv)
echo "brokerInventoryFile=$brokerInventoryFile"
echo "brokerDockerImage=$brokerDockerImage"
echo
x=$(wait4Key)

##############################################################################################################################
# prepare test
echo ">>> preparing test ..."
if [[ $brokerChoice == "local-broker" ]]; then
  $AS_TEST_HOME/lib/_start.local.broker.sh $brokerDockerImage
  if [[ $? != 0 ]]; then echo ">>> ERROR starting local broker"; echo; exit 1; fi
else
  runScript="$AS_TEST_SCRIPT_PATH/prepare/_run.call.sh"
  $runScript
  if [[ $? != 0 ]]; then echo ">>> ERROR:$runScript"; echo; exit 1; fi
  brokerInventoryFile=$(assertFile $cloudBrokerInventoryFile) || exit
fi

##############################################################################################################################
# run tests

for ansibleSolaceTest in ${ansibleSolaceTests[@]}; do

  runScript="$AS_TEST_SCRIPT_PATH/$ansibleSolaceTest/_run.call.sh $brokerInventoryFile"

  echo; echo "##############################################################################################################"
  echo "# test: $ansibleSolaceTest"
  echo "# calling: $runScript"

  $runScript

  if [[ $? != 0 ]]; then echo ">>> ERR:$runScript. aborting."; echo; exit 1; fi

done

##############################################################################################################################
# teardown test
echo ">>> tearing down test ..."
if [[ $brokerChoice == "local-broker" ]]; then
  $AS_TEST_HOME/lib/_stop.local.broker.sh $brokerDockerImage
  if [[ $? != 0 ]]; then echo ">>> ERROR stopping local broker"; echo; exit 1; fi
else
  echo; echo ">>> WARNING: not tearing down test for Solace Cloud"; echo;
  # runScript="$AS_TEST_SCRIPT_PATH/teardown/_run.call.sh"
  # $runScript
  # if [[ $? != 0 ]]; then echo ">>> ERROR:$runScript"; echo; exit 1; fi
  # exists=$(assertNoFile $cloudBrokerInventoryFile) || exit
fi


echo;
echo "##############################################################################################################"
echo "# All tests completed successfully!"
echo;

###
# The End.
