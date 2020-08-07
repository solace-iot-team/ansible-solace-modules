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
    # select inventory
    localBrokerInventoryFile="$AS_TEST_HOME/lib/broker.inventories/local.broker.inventory.json"
    cloudBrokerInventoryFile=$(assertFile "$AS_TEST_HOME/lib/broker.inventories/cloud.broker.inventory.json") || exit
    # select broker(s) inside inventory
    export brokers="all"
    # playbook
    playbooks=(
      "./exceptions.1.playbook.yml"
      "./exceptions.2.playbook.yml"
      "./examples.playbook.yml"
      "./playbook.yml"
    )

  # END SELECT


x=$(showEnv)
x=$(wait4Key)

##############################################################################################################################
# Prepare

ANSIBLE_SOLACE_LOG_FILE="$AS_TEST_SCRIPT_PATH/ansible-solace.log"
rm -f $ANSIBLE_SOLACE_LOG_FILE
rm -f hostvars*.json

$AS_TEST_HOME/tests-embeddable/wait-until-broker-available/_run.call.sh $localBrokerInventoryFile
if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi
$AS_TEST_HOME/tests-embeddable/wait-until-broker-available/_run.call.sh $cloudBrokerInventoryFile
if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi

##############################################################################################################################
# Run

for playbook in ${playbooks[@]}; do

  ansible-playbook \
                    --forks 1 \
                    -i $localBrokerInventoryFile \
                    -i $cloudBrokerInventoryFile \
                    $playbook \
                    --extra-vars "brokers=$brokers" \
                    -vvv

  if [[ $? != 0 ]]; then

    echo ">>> ERROR";
    echo; echo "log: $ANSIBLE_SOLACE_LOG_FILE"
    echo

  fi

done

###
# The End.
