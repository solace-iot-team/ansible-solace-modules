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
if [[ $# != 1 ]]; then echo "Usage: '$SCRIPT_PATH/_run.call.sh {full_path}/{broker_inventory}'"; exit 1; fi
BROKERS_INVENTORY=$1
source $AS_TEST_HOME/lib/functions.sh

##############################################################################################################################
# Prepare

##############################################################################################################################
# Run
brokers="all"
playbooks=(
  "$SCRIPT_PATH/playbook.yml"
)

for playbook in ${playbooks[@]}; do
  ansible-playbook \
                    -i $BROKERS_INVENTORY \
                    $playbook \
                    --extra-vars "brokers=$brokers"
  if [[ $? != 0 ]]; then echo ">>> ERR: $AS_TEST_SCRIPT_PATH"; echo; exit 1; fi
done

###
# The End.
