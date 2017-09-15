#!/bin/bash

fileName=''
suffix=''
supportTypes='.c .h .m'
lines=0

function getFileSuffix()
{
	if [ $# -lt 1 ]
	then
		fileName=''
		suffix=''
		echo 'you must pass filename'
		return 1
	fi

	baseName=$(basename "$1")
	fileName=${baseName%.*}
	suffix=${baseName##*.}
	
	if [ "$baseName" = "$suffix" ]
	then
		suffix=''
	fi
	return 0
}

function getFileLines()
{
	lines=`sed -n '$=' $1`
}

function enumFilesInPath()
{
	for file in $1/*
	do
		if test -d "$file"
		then
			echo -e "$file is folder \n"
			getFileSuffix "$file"
			if [[ $baseName =~ " " ]]
			then
				echo -e "folder name '$file' is invalid! Contain space!" >> ./log
				return 1
			fi
			enumFilesInPath "$file"
		else
			echo -e "$file is file \n"
			getFileSuffix "$file"
			if [[ $supportTypes =~ $suffix ]]
			then 
				getFileLines $file
				echo $file $lines >> ./log
			fi
		fi
	done

	return 0
}




enumFilesInPath $1
