#!/bin/bash
#
# menu_generator.sh - display a dialog menu to allow user to select one of given arguments
#
# Author : Daniel Saran
#
# -------------------------------------------------------------------------
#
# This program receives a list of arguments that are displayed in a 'dialog'
# menu allowing user to select one of the arguments.
#
# Example:
#  $ menu_generator.sh element1 element2 element3
#  ___________________
#  |  Items found (3) |
#  |__________________|
#  | 1   |   element1 |
#  | 2   |   element2 |
#  | 3   |   element3 |
#  |------------------|
#  |  (OK)  (CANCEL)  |
#  |__________________|
#
#  The exit code is 1 if cancel button is pressed and 0 if an item is selected.
#  The selected value is sent to stdout.
#

# Enable debug
#set -xv
#trap read DEBUG


FILES=""
COUNT=0
FILE_LIST[0]=0
DIALOG_COMMAND=dialog

SHOW=0

for f in $@
do
    COUNT=$(($COUNT+1))
    FILE_LIST[$COUNT]=$f
    # Reimplemented using awk for performance issues
    #FILES="$FILES $COUNT $f"
done
FILES=`(for file in $@; do echo $file; done) |awk 'BEGIN {count = 1; result = ""} {result = result" "count" "$1; count += 1} END {print result}'`

MESSAGE="Items found ($COUNT)"
if [ $COUNT == 0 ]
then
    $DIALOG_COMMAND --stdout --infobox "No item to display." 0 0
    exit 1
elif [ $COUNT == 1 ]
then
    SELECTED=1
else
    SELECTED=$($DIALOG_COMMAND --colors --stdout --menu "$MESSAGE" 0 0 0 $FILES)
fi

RESULT=$?

if [ $RESULT == 0 ]
then
    echo ${FILE_LIST[SELECTED]}
else
    TMP=$($DIALOG_COMMAND --infobox --stdout "No item selected." 0 0)
    exit 1
fi
