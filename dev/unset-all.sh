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
# usage: source unset-all.sh
#
# Unsets all variables

unset ANSIBLE_PYTHON_INTERPRETER
unset ANSIBLE_MODULE_UTILS
unset ANSIBLE_LIBRARY
unset ANSIBLE_DOC_FRAGMENT_PLUGINS
unset ANSIBLE_SOLACE_HOME
unset ANSIBLE_SOLACE_ENABLE_LOGGING

clear
echo
echo "Ansible env vars:"; echo
echo " - ANSIBLE_PYTHON_INTERPRETER=$ANSIBLE_PYTHON_INTERPRETER"
echo " - ANSIBLE_SOLACE_HOME=$ANSIBLE_SOLACE_HOME"
echo " - ANSIBLE_MODULE_UTILS=$ANSIBLE_MODULE_UTILS"
echo " - ANSIBLE_LIBRARY=$ANSIBLE_LIBRARY"
echo " - ANSIBLE_DOC_FRAGMENT_PLUGINS=$ANSIBLE_DOC_FRAGMENT_PLUGINS"
echo " - ANSIBLE_SOLACE_ENABLE_LOGGING=$ANSIBLE_SOLACE_ENABLE_LOGGING"
echo
