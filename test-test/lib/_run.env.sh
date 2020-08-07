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

###############################################################################################
# sets the base env for the test
# - env vars
# - test for required packages
# - source the lib/functions.sh
#
# call: from {test}/_run.env.sh:
#       source ./_run.env.sh

# unset all vars first
# save python interpreter
if [ -z "${ANSIBLE_PYTHON_INTERPRETER-unset}" ]; then
    echo ">>> ERR: env var: ANSIBLE_PYTHON_INTERPRETER is set to the empty string. Either unset or set properly."; echo
    exit 1
fi
ansiblePythonInterpreter=$ANSIBLE_PYTHON_INTERPRETER
envVars=$(env | cut -d= -f1 | grep ANSIBLE)
for envVar in ${envVars[@]}; do
  unset $envVar
done
if [ ! -z "$ansiblePythonInterpreter" ]; then
    #echo "ansiblePythonInterpreter=$ansiblePythonInterpreter is not empty"; echo;
    export ANSIBLE_PYTHON_INTERPRETER=$ansiblePythonInterpreter
fi

# test jq is installed
res=$(jq --version)
if [[ $? != 0 ]]; then echo "ERR >>> jq not found. aborting."; echo; exit 1; fi

# load the functions
source $AS_TEST_HOME/lib/functions.sh

# choose env if not pre-set
env=$(chooseTestRunnerEnv $AS_TEST_RUNNER_ENV)
if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi
echo; echo "Running tests with environment: $env "; echo
export AS_TEST_RUNNER_ENV=$env

if [[ $AS_TEST_RUNNER_ENV == "dev" ]]; then
  export ANSIBLE_MODULE_UTILS="$AS_TEST_PROJECT_HOME/lib/ansible/module_utils"
  export ANSIBLE_LIBRARY="$AS_TEST_PROJECT_HOME/lib/ansible/modules"
  export ANSIBLE_DOC_FRAGMENT_PLUGINS="$AS_TEST_PROJECT_HOME/lib/ansible/plugins/doc_fragments"
fi


###
# The End.
