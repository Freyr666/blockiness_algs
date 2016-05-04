#!/usr/bin/bash

function get_data(){
    local result=$(cat $1 | grep $2)
    echo $result
}

function map_value() {
    if  [ $(echo "$1 >= 0.0" | bc -l) -eq 1 ]  &&  [ $(echo "$1 <= 25.0" | bc -l) -eq 1 ]
    then
	local result="Excellent"
    elif [ $(echo "$1 > 25.0" | bc -l) -eq 1 ] && [ $(echo "$1 <= 50.0" | bc -l) -eq 1 ]
    then
	local result="Acceptable"
    else
	local result="Bad"
    fi
    echo $result
}

function compute() {
    data=$(get_data $DATABASE $1)
    results=$($PROGRAMM $IMAGE_PATH $1)
    value=$(echo $data | awk '{print $4}')
    grade=$(map_value $value)
    #echo "$grade $value"
    echo "$grade $data" | awk '{print "\n" "Picture: " $2 " " $3 "\n" "reference value:\t" $5 " (" $1 ")"}'
    echo $results | awk '{print "old (bad) algorithm:\t" $3 "\n" "new (diff) algorithm:\t" $5 " (" $6 ")"}'
    if [ "$grade" = "$(echo $results | awk '{print $6}')" ]
    then
	echo "Correct_guess"
    else
	echo "Wrong_guess"
    fi
}

# main
if [ $# -ne 2 ]
then
    printf "Usage: %s database path/to/pictures\n" $0
    exit 1
fi

export DATABASE=$1
export IMAGE_PATH=$2
export PROGRAMM="./analysis.py"

export -f get_data
export -f map_value
export -f compute

ls $IMAGE_PATH | grep bmp | parallel -P 16 --progress compute {} > result.temp

CORRECT=$(cat result.temp | grep Correct_guess | wc -l)
WRONG=$(cat result.temp | grep Wrong_guess | wc -l)
printf "Result: %d%% hits\nSee result.temp for more details\n" $(echo "$CORRECT*100 / ($WRONG+$CORRECT)" | bc)
