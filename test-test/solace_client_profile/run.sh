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

SCRIPT_PATH=$(cd $(dirname "$0") && pwd);
# test jq is installed
res=$(jq --version)
if [[ $? != 0 ]]; then echo "ERR >>> jq not found. aborting."; echo; exit 1; fi


##############################################################################################################################
# Prepare

source $SCRIPT_PATH/../lib/unset-all.sh
if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi
source $SCRIPT_PATH/../lib/set-ansible-env.dev.sh
if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi

ANSIBLE_SOLACE_LOG_FILE="$SCRIPT_PATH/ansible-solace.log"
rm -f $ANSIBLE_SOLACE_LOG_FILE

##############################################################################################################################
# Run

# SELECT
  # select inventory
  BROKERS_INVENTORY="$SCRIPT_PATH/../lib/local.broker.inventory.json"
  BROKERS_INVENTORY="$SCRIPT_PATH/../lib/cloud.brokers.inventory.json"
  #BROKERS_INVENTORY="$SCRIPT_PATH/../lib/cloud.brokers.inventory.yml"
  # select broker(s) inside inventory
  BROKERS="all"

  PLAYBOOK="$SCRIPT_PATH/exceptions.playbook.yml"
  PLAYBOOK="$SCRIPT_PATH/playbook.yml"

# END SELECT



$SCRIPT_PATH/../wait_until_brokers_available/_run.call.sh $BROKERS_INVENTORY
if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi

# --step --check -vvv
ansible-playbook -i $BROKERS_INVENTORY \
                  $PLAYBOOK \
                  --extra-vars "brokers=$BROKERS" \
                  -vvv
if [[ $? != 0 ]]; then echo "ERR >>> aborting. check $ANSIBLE_SOLACE_LOG_FILE ..."; echo; exit 1; fi


##############################################################################################################################
# show log

echo; echo "Looks good?"
echo; echo "Show the log?"
echo; read -p 'Enter to continue, Ctrl-c to abort: ' continue; echo; echo

ANSIBLE_SOLACE_LOG_FILE="$SCRIPT_PATH/ansible-solace.log"
less $ANSIBLE_SOLACE_LOG_FILE

###
# The End.