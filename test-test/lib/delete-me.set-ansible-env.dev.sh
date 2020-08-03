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

################################################################################
# usage: source set-ansible-env.dev.sh
#

export ANSIBLE_PYTHON_INTERPRETER=/usr/local/bin/python

exit

export ANSIBLE_SOLACE_PROJECT_PATH="/Users/rjgu/Dropbox/Solace-Contents/Solace-IoT-Team/ansible-dev/ansible-solace"

export ANSIBLE_SOLACE_ENABLE_LOGGING=true
# pip3 show ansible-solace
ANSIBLE_SOLACE_HOME="$ANSIBLE_SOLACE_PROJECT_PATH/lib"

export ANSIBLE_MODULE_UTILS="$ANSIBLE_SOLACE_HOME/ansible/module_utils"
export ANSIBLE_LIBRARY="$ANSIBLE_SOLACE_HOME/ansible/modules"
#export ANSIBLE_LOOKUP_PLUGINS="$ANSIBLE_SOLACE_HOME/ansible/plugins"



echo
echo "Ansible env vars:"; echo
env | grep ANSIBLE
echo

###
# The End.
