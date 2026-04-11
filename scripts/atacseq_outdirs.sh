#!/bin/bash

read user
WORKDIR="/home/${user}/ATACseq_Pipeline"
export WORKDIR 
cd "$WORKDIR"
 

read rules
create_dir() {
 for rule in rules; do
   mkdir -p results/"$rule"
   echo "Directory created successfully for ${rule}."
     if [ $? -eq 0 ]; then
       echo "Command successfully executed."
     else 
       echo "Command not executed successfully."
     fi 
 done
}

create_dir ${rules[@]}" 
