# Setup Development Environment

* Set up ansible environment to point to the project:

````bash

vi set-ansible-env.sh
# edit python path
export ANSIBLE_PYTHON_INTERPRETER=/usr/local/bin/python

# set the env
source set-ansible-env.sh
````

* Unset the environment

````bash
source unset-ansible-env.sh

# or

source unset-all.sh
````



---
The End.
