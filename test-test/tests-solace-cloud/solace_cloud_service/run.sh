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
    # logging & debug: ansible
      # ansibleLogFile="./tmp/ansible.log"
      # export ANSIBLE_LOG_PATH="$ansibleLogFile"
      # export ANSIBLE_DEBUG=False
      export ANSIBLE_VERBOSITY=3
    # logging: ansible-solace
      export ANSIBLE_SOLACE_LOG_PATH="./tmp/ansible-solace.log"
      export ANSIBLE_SOLACE_ENABLE_LOGGING=True
    # select inventory
      solaceCloudAccountsInventoryFile=$(assertFile "$AS_TEST_HOME/lib/broker.inventories/solace-cloud-accounts.inventory.yml") || exit
    # select account(s) inside inventory
      solaceCloudAccounts="all"

    # playbook
    playbooks=(
      "./create.playbook.yml"
      "./create.playbook.yml" # run it twice, to test idempotency
      "./facts.playbook.yml"
      "./ex_1.playbook.yml"
      "./ex_2.playbook.yml"
      "./ex_3.playbook.yml"
      # "./delete.playbook.yml"
      # "./delete.playbook.yml" # run it twice, to test idempotency
    )

  # END SELECT


x=$(showEnv)
x=$(wait4Key)

##############################################################################################################################
# Prepare

mkdir ./tmp > /dev/null 2>&1
rm -f ./tmp/*.*

##############################################################################################################################
# Run
for playbook in ${playbooks[@]}; do

  ansible-playbook \
                    -i $solaceCloudAccountsInventoryFile \
                    $playbook \
                    --extra-vars "SOLACE_CLOUD_ACCOUNTS=$solaceCloudAccounts"

  if [[ $? != 0 ]]; then echo ">>> ERR: $AS_TEST_SCRIPT_PATH"; echo; exit 1; fi

done

###
# The End.
