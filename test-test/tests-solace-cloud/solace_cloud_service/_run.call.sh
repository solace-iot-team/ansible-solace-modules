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

solaceCloudAccountsInventoryFile=$(assertFile "$SCRIPT_PATH/lib/solace-cloud-accounts.inventory.yml") || exit
solaceCloudAccounts="all"

playbooks=(
  "$SCRIPT_PATH/create.playbook.yml"
  "$SCRIPT_PATH/create.playbook.yml" # run it twice, to test idempotency
  "$SCRIPT_PATH/facts.playbook.yml"
  "$SCRIPT_PATH/ex_1.playbook.yml"
  "$SCRIPT_PATH/ex_2.playbook.yml"
  "$SCRIPT_PATH/ex_3.playbook.yml"
  "$SCRIPT_PATH/delete.playbook.yml"
  "$SCRIPT_PATH/delete.playbook.yml" # run it twice, to test idempotency
)

##############################################################################################################################
# Prepare
mkdir $SCRIPT_PATH/tmp > /dev/null 2>&1
rm -f $SCRIPT_PATH/tmp/*.*
##############################################################################################################################
# Run
for playbook in ${playbooks[@]}; do
  ansible-playbook \
                    -i $solaceCloudAccountsInventoryFile \
                    $playbook \
                    --extra-vars "SOLACE_CLOUD_ACCOUNTS=$solaceCloudAccounts" \

  if [[ $? != 0 ]]; then echo ">>> ERR: $AS_TEST_SCRIPT_PATH"; echo; exit 1; fi
done



###
# The End.
