#!/bin/bash
#
# This script increments the application version, commits the version file and tag the source at repository.
# The script works by reading the property 'application.version' from the file 'build.properties'
# It expects a verion in the format MAJOR.MID.MINOR (e.g. 1.0.2)
#
# Requirements:
# - build.properties file with a property called 'application.version'
# - Version is numeric only
# - Should be using a Subversion repository that follows the standard logical structure (trunk, branches, tags)
# - Single project SVN (svn root is the parent of the trunk directory)

PROPERTIES_FILE=build.properties
PROPERTY_NAME=application.version

if [ $# != 0 ]
then
    echo "This script increments the application version, commits the version file and tag the source at repository."
    echo "usage: `basename $0`"
    exit 0
fi

OLD_VERSION=`grep "$PROPERTY_NAME" $PROPERTIES_FILE |cut -d= -f2`
MAJOR_VERSION=`echo $OLD_VERSION |cut -d. -f1`
MID_VERSION=`echo $OLD_VERSION |cut -d. -f2`
MINOR_VERSION=`echo $OLD_VERSION |cut -d. -f3`

VALUE=`dialog --stdout --menu "Release type" 0 0 2 1 Bugs 2 Requirements`

if [ $VALUE -eq 1 ]
then
    INCREMENT=`expr $MINOR_VERSION + 1`
    NEW_VERSION=$MAJOR_VERSION.$MID_VERSION.$INCREMENT
elif [ $VALUE -eq 2 ]
then
    INCREMENT=`expr $MID_VERSION + 1`
    NEW_VERSION=$MAJOR_VERSION.$INCREMENT.0
fi

read_version() {
    clear 
    echo "Last Version was $OLD_VERSION"
    read -p "What is the release version ? (default: $NEW_VERSION): " NEXT_VERSION

    NEXT_VERSION=${NEXT_VERSION:-$NEW_VERSION}

    echo $NEXT_VERSION | grep -qxE '[0-9]*\.[0-9]*\.[0-9]*'
    if [ $? != 0 ]
    then
        clear
        echo "Version does not match the pattern 'M.m.d'"
        read -p "Are you sure you want to use the version '$NEXT_VERSION' ? (y/[n]) " OPTION
        OPTION=${OPTION:-"n"}
        if [ $OPTION != "y" -a $OPTION != "Y" ]
        then
            read_version
        fi
    fi
}

read_version

SVN_ROOT=`svn info | grep -E "^Repository Root: "| sed 's/^Repository Root: \(.*\)$/\1/g'`
SVN_URL=`svn info | grep -E "^URL: "| sed 's/^URL: \(.*\)$/\1/g'`

TAG_URL=$SVN_ROOT/tags/$NEXT_VERSION

LIST=`svn list $TAG_URL 2>/dev/null`
RESULT=$?

if [ $RESULT = 0 ]
then
    clear
    echo "[ERROR] Version '$NEXT_VERSION' already exists at repository: $TAG_URL"
    exit 1
fi

sed  -i "s/$PROPERTY_NAME=$OLD_VERSION/$PROPERTY_NAME=$NEXT_VERSION/g" $PROPERTIES_FILE
echo "Version is now $NEXT_VERSION" 

echo
echo "Going to commit file '$PROPERTIES_FILE'..."
echo "Press any <ENTER> to continue or CTRL+C to abort"
read

echo svn commit -m "[release-plugin] Version $NEXT_VERSION" $PROPERTIES_FILE

echo
echo "Going to create tag '$NEXT_VERSION'..."
echo "Target: '$TAG_URL'"
echo "Press any <ENTER> to continue or CTRL+C to abort"
read
echo svn copy -m "[release-plugin] tag version $NEXT_VERSION" $SVN_URL $TAG_URL

