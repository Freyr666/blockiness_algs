#!/usr/bin/bash

function get_data(){
    local result=$(cat $1 | grep $2)
    echo $result
}

function map_value() {
    if  [ $(echo "$1 >= 0.0" | bc) -eq 1 ]  &&  [ $(echo "$1 <= 20.0" | bc) -eq 1 ]
    then
	local result="Excellent"
    elif [ $(echo "$1 > 20.0" | bc) -eq 1 ] && [ $(echo "$1 <= 40.0" | bc) -eq 1 ]
    then
	local result="Good"
    elif [ $(echo "$1 > 40.0" | bc) -eq 1 ] && [ $(echo "$1 <= 60.0" | bc) -eq 1 ]
    then
	local result="Rather_good"
    elif [ $(echo "$1 > 60.0" | bc) -eq 1 ] && [ $(echo "$1 <= 80.0" | bc) -eq 1 ]
    then
	local result="Poor"
    elif [ $(echo "$1 > 80.0" | bc) -eq 1 ] && [ $(echo "$1 <= 100.0" | bc) -eq 1 ]
    then
	local result="Bad"
    else
	local result="Bad"
    fi
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
    value=$(echo $data | awk '{print $4}')
    grade=$(map_value $value)
    #echo "$grade $value"
    echo "$grade $data" | awk '{print "\n" "Picture: " $2 " " $3 "\n" "reference value:\t" $5 " (" $1 ")"}'
    echo $results | awk '{print "old (bad) algorithm:\t" $3 "\n" "new (diff) algorithm:\t" $5}'
done
