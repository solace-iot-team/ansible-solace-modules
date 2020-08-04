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
  #export AS_TEST_RUNNER_ENV="dev"
  #export AS_TEST_RUNNER_ENV="package"

source $AS_TEST_HOME/lib/_run.env.sh $AS_TEST_RUNNER_ENV

##############################################################################################################################
# Configure

runCallDirs=(
  "tests-1-broker"
  "tests-2-brokers"
)

##############################################################################################################################
# show & wait
x=$(showEnv)
x=$(wait4Key)

##############################################################################################################################
# Run tests
#

  for runCallDir in ${runCallDirs[@]}; do

    runScript="$AS_TEST_HOME/$runCallDir/_run.call.sh"

    echo; echo "##############################################################################################################"
    echo "# Running Tests: $runCallDir"
    echo "# calling: $runScript"

    $runScript

    if [[ $? != 0 ]]; then echo ">>> ERR:$runScript. aborting."; echo; exit 1; fi

  done

echo;
echo "##############################################################################################################"
echo "# All tests completed successfully!"
echo;

###
# The End.
