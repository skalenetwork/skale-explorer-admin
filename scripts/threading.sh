#!/bin/bash

if [ $# -ne 3 ]; then
    echo "Usage: $0 <schain_name> <threads> <table_name>"
    exit 1
fi

schain_name="$1"
threads="$2"
table_name="$3"
directory_path="dumps/${schain_name}"
file_path="${directory_path}/${table_name}.sql"
number_of_lines=$(wc -l < "$file_path")
number_of_lines_per_thread=$((number_of_lines / threads))

mkdir -p "${directory_path}/${table_name}/logs"
mkdir -p "${directory_path}/${table_name}/errors"

split -l $number_of_lines_per_thread -d -a 3 $file_path "${directory_path}/${table_name}/${table_name}_"
spiltted_file_path="${directory_path}/${table_name}"

for ((i = 0; i <= threads; i++)); do
    nohup docker exec -i "${schain_name}_db" psql -U blockscout -d blockscout \
        < "${spiltted_file_path}/${table_name}_$(printf "%03d" $i)" \
        > "${spiltted_file_path}/logs/${table_name}_$(printf "%03d" $i)" \
        2> "${spiltted_file_path}/errors/${table_name}_$(printf "%03d" $i)" &
done
