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

function assertNoFile() {
  if [[ $# -lt 1 ]]; then
      echo "Usage: fileVar='\$(assertNoFile {full-path/filename})'" 1>&2
      return 1
  fi
  local file=$1
  if [[ -f "$file" ]]; then
    echo ">>> ERR: file='$file' exist. aborting" > /dev/tty
    return 1;
  fi
  echo $file
  return 0
}
function assertFile() {
  if [[ $# -lt 1 ]]; then
      echo "Usage: fileVar='\$(assertFile {full-path/filename})'" 1>&2
      return 1
  fi
  local file=$1
  if [[ ! -f "$file" ]]; then
    echo ">>> ERR: file='$file' does not exist. aborting" > /dev/tty
    return 1;
  fi
  echo $file
  return 0
}
function getCloudBrokerInventoryMeta() {
  if [[ $# -lt 2 ]]; then
      echo "Usage: metaJson='\$(getCloudBrokerInventoryMeta {full-path/inventory.json})'" 1>&2
      return 1
  fi
  local inventoryFile="$1"
  meta=$(cat $inventoryFile | jq -r ".[].hosts[].meta")
  echo $meta
  return 0
}

function chooseFromArray() {
  if [[ $# -lt 2 ]]; then
      echo "Usage: userChoice='\$(chooseFromArray descr list-of-choices)'" 1>&2
      return 1
  fi
  local descr="$1"
  shift
  local choices=("$@")

  let num=${#choices[@]}-1
  if [ $num -lt 1 ]; then echo ">>> ERR-chooseFromArray(): no choices for '$descr' found." 1>&2; exit 1; fi

  echo 1>&2
  echo "Choose a $descr: " 1>&2
  echo 1>&2

  for i in "${!choices[@]}"; do
    echo "($i): ${choices[$i]}" 1>&2
  done

  echo 1>&2

  read -p "Enter 0-$num: " choice

  if [[ ! "$choice" =~ ^[0-9]+$ ]] || [ ! "$choice" -ge 0 ] || [ ! "$choice" -le "$num" ]; then
    echo "Choose 0-$num, your choice:'$choice' is not valid" 1>&2
    return 1
  fi

  echo ${choices[$choice]}
  return 0

}

function showEnv() {
  echo > /dev/tty
  echo "# Test Environment:" > /dev/tty
  env | grep AS_TEST  > /dev/tty
  echo > /dev/tty
  echo "# Ansible Environment:" > /dev/tty
  env | grep ANSIBLE > /dev/tty
  echo > /dev/tty
  return 0
}

function wait4Key() {
  read -n 1 -p "press space to continue, CTRL-C to exit ..." x
  echo "$x" > /dev/tty
  return 0
}

function wait4BrokerStart() {
  echo "pausing: " > /dev/tty
  local -a marks=( '/' '-' '\' '|' );
  local counter=0
  while [ $counter -le 20 ]; do
   # echo -ne "${marks[i++ % ${#marks[@]}]}" > /dev/tty
   sleep 1s;
   #echo -ne "\b" > /dev/tty
   echo -n " $counter" > /dev/tty
   counter=$(( $counter + 1 ))
  done;
  echo  > /dev/tty;
  echo  > /dev/tty
}

# if arg exists, return it
# otherwise, ask the user
function chooseTestRunnerEnv() {
  testRunnerEnv=$1
  envs=(
    "dev"
    "package"
  )
  if [ ! -z "$testRunnerEnv" ]; then
    let found=-1
    for i in "${!envs[@]}"; do
      if [ ${envs[$i]} == $testRunnerEnv ]; then let found=$i; echo $testRunnerEnv; return 0; fi
    done
    echo "testRunnerEnv=$testRunnerEnv is not valid. Choose one of '${envs[@]}'." 1>&2; return 1
  fi

  echo "Choose the test runner environment:" 1>&2
  echo 1>&2
  for i in "${!envs[@]}"; do
    echo "($i): ${envs[$i]}" 1>&2
  done
  echo 1>&2
  read -p "Enter 0-$i: " choice
  if [[ ! "$choice" =~ ^[0-9]+$ ]] || [ ! "$choice" -ge 0 ] || [ ! "$choice" -le "$i" ]; then
    echo "Choose 0-$i, your choice:'$choice' is not valid" 1>&2
    return 1
  fi
  echo ${envs[$choice]}
  return 0
}

function chooseBrokerDockerImage() {
  if [[ $# != 1 ]]; then
      echo "Usage: brokerDockerImage='\$(chooseBrokerDockerImage images-json-file)'" 1>&2
      return 1
  fi
  brokerDockerImagesFile=$1
  brokerDockerImagesJSON=$(cat $brokerDockerImagesFile | jq -r '.brokerDockerImages' )
  brokerDockerImagesArray=($(echo $brokerDockerImagesJSON | jq -r '.[]'))
  # echo "brokerDockerImagesArray=${brokerDockerImagesArray[@]}" 1>&2
  # echo "brokerDockerImagesArray.length=${#brokerDockerImagesArray[@]}" 1>&2

  let numImages=${#brokerDockerImagesArray[@]}-1
  if [ $numImages -lt 1 ]; then echo "ERR >>> no images found." 1>&2; exit 1; fi

  echo 1>&2
  echo "Choose a broker docker image: " 1>&2
  echo 1>&2

  for i in "${!brokerDockerImagesArray[@]}"; do
    echo "($i): ${brokerDockerImagesArray[$i]}" 1>&2
  done

  echo 1>&2

  read -p "Enter 0-$numImages: " choice

  if [[ ! "$choice" =~ ^[0-9]+$ ]] || [ ! "$choice" -ge 0 ] || [ ! "$choice" -le "$numImages" ]; then
    echo "Choose 0-$numImages, your choice:'$choice' is not valid" 1>&2
    return 1
  fi

  echo ${brokerDockerImagesArray[$choice]}
  return 0

}

###
# The End.
