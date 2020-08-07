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

##############################################################################################################################
# Configure
brokerDockerImagesFile="$AS_TEST_HOME/lib/brokerDockerImages.json"
localBrokerInventoryFile="$AS_TEST_HOME/lib/broker.inventories/local.broker.inventory.json"
cloudBrokerInventoryFile="$AS_TEST_HOME/lib/broker.inventories/cloud.broker.inventory.json"
export brokers="all"
playbook="$SCRIPT_PATH/playbook.yml"

##############################################################################################################################
# Prepare

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

  ansible-playbook \
                      -i $localBrokerInventoryFile \
                      $playbook \
                      --extra-vars "brokers=$brokers" \
                      -vvvv

  if [[ $? != 0 ]]; then echo ">>> ERR: $SCRIPT_PATH. aborting."; echo; exit 1; fi

done

###
# The End.
