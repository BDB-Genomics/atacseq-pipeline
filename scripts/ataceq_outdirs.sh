#!/bin/bash

read user
WORKDIR="/home/${user}/ATACseq_Pipeline"
export WORKDIR 
cd "$WORKDIR" || {echo "Failed to change the working directory"; exit 1; }
 

echo "Enter rules separated by space into an array"
read -a rules # Reads into an array
create_dir() {
 for rule in "$@"; do     
     if [ "$rule" = "samtools_index" ]; then 
       mkdir -p results/samtools_index/post_markdup
       echo "Directory created successfully for ${rule}."
     elif [ "$rule" = "picard" ]; then
       mkdir -p results/picard/CollectAlignmentSummaryMetrics 
       #cd results/picard &&
       mkdir -p results/picard/CollectInsertSizeMetrics
       #cd ..
       echo "Directory created successfully for ${rule}."
     else
        mkdir -p "results/${rule}" 
        echo "Directory created successfully for ${rule}."
     fi 
            
     if [ $? -eq 0 ]; then
       echo "Command successfully executed."
     else 
       echo "Command not executed successfully."
     fi 
 done
}

create_dir "${rules[@]}" . Verify rigorously. Put a tick mark at the end of each line. 
