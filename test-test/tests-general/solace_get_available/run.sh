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

  ############################################################################################################################
  # SELECT
    # logging
    export ANSIBLE_SOLACE_ENABLE_LOGGING=true
    # export ANSIBLE_LOG_PATH=./ansible.log
    # export ANSIBLE_DEBUG=True
    # images
    brokerDockerImagesFile="$AS_TEST_HOME/lib/brokerDockerImages.json"
    # select inventory
    localBrokerInventoryFile="$AS_TEST_HOME/lib/broker.inventories/local.broker.inventory.json"
    cloudBrokerInventoryFile="$AS_TEST_HOME/lib/broker.inventories/cloud.broker.inventory.json"
    # select broker(s) inside inventory
    export brokers="all"
    # playbook
    playbook="./playbook.yml"

  # END SELECT


x=$(showEnv)
x=$(wait4Key)

##############################################################################################################################
# Prepare

ANSIBLE_SOLACE_LOG_FILE="$AS_TEST_SCRIPT_PATH/ansible-solace.log"
rm -f $ANSIBLE_SOLACE_LOG_FILE
rm -f $AS_TEST_SCRIPT_PATH/*.log

##############################################################################################################################
# Run Cloud

ansible-playbook \
                  -i $cloudBrokerInventoryFile \
                  $playbook \
                  --extra-vars "brokers=$brokers" \
                  -vvvv

if [[ $? != 0 ]]; then echo ">>> ERR: $SCRIPT_PATH. aborting."; echo; exit 1; fi

##############################################################################################################################
# Run Local
brokerDockerImages=$(cat $brokerDockerImagesFile | jq -r ".brokerDockerImages[]")
for brokerDockerImage in ${brokerDockerImages[@]}; do

  $AS_TEST_HOME/lib/_start.local.broker.sh $brokerDockerImage
  if [[ $? != 0 ]]; then echo ">>> ERR: $SCRIPT_PATH. aborting."; echo; exit 1; fi

  x=$(wait4BrokerStart)

  ansible-playbook \
                    -i $localBrokerInventoryFile \
                    $playbook \
                    --extra-vars "brokers=$brokers" \
                    -vvvv

  if [[ $? != 0 ]]; then echo ">>> ERR: $SCRIPT_PATH. aborting."; echo; exit 1; fi

done

###
# The End.