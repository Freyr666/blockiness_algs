#!/usr/bin/bash

function get_data(){
    local result=$(cat $1 | grep $2)
    echo $result
}

# main
if [ $# -ne 2 ]
then
    printf "Usage: %s database path/to/pictures\n" $0
    exit 1
fi

DATABASE=$1
IMAGE_PATH=$2
PROGRAMM="./analysis.py"

SEP=" "

for image in $(ls $IMAGE_PATH | grep bmp); do
    data=$(get_data $DATABASE $image)
    results=$($PROGRAMM $IMAGE_PATH $image)
    echo $data | awk '{print "\n" "Picture: " $1 " " $2 "\n" "reference value:\t" $4}'
    echo $results | awk '{print "old (bad) algorithm:\t" $3 "\n" "new (diff) algorithm:\t" $5}'
done
