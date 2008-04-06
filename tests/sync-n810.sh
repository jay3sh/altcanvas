#!/bin/bash

N810=192.168.1.104
LOCAL_MUSIC_STORE=/home/jayesh/limewire
REMOTE_MUSIC_STORE=/media/mmc2/music

show_config()
{
    echo "LOCAL_MUSIC_STORE      : $LOCAL_MUSIC_STORE"
    echo "REMOTE_MUSIC_STORE     : $REMOTE_MUSIC_STORE"
    echo "N810 IP                : $N810"

    USED_SPACE=`ssh root@$N810 "df -h $REMOTE_MUSIC_STORE" | awk '/mmc2/ { printf "Used " $3 " - Available " $4 }'`
    echo "N810 Music store usage : $USED_SPACE"
}

search_music_store()
{
    results=`find $LOCAL_MUSIC_STORE | grep -i $1 | sed 's/\s/*/g'`

    let i=0
    for songfile in $results
    do
        printf "$i) $songfile\n"
	    SONG_ARR[$i]=$songfile;
        let i=$i+1
    done
}

deploy_music()
{
    SONG_=`echo $1 | sed 's/\s/\*/g'`
    rsync --progress $SONG_ root@$N810:$REMOTE_MUSIC_STORE/
}

select_song()
{
    indices=`echo $1 | sed 's/,/ /g'`
    for index in $indices
    do
        SONG=`echo ${SONG_ARR[$index]} | sed 's/\s/\*/g'`
        deploy_music $SONG
    done
}

usage()
{
cat << "EOF"  
List of commands you can use:
config        - display configuration variables
find <search> - Find files with "search" in their name
sync <list>   - comma seperated list of indices from previous search results.
                Files pointed by the indices will be synced to destination.
quit          - Quit
help          - Help
EOF

}


while [[ 1 ]]
do
    printf "\033[1mcmd > \033[0m"
    read command arg1 arg2

    case $command in
        "config" ) show_config ;;
        "quit"   ) break;;
        "q"      ) break;;
        "help"   ) usage;;
        "sync"   ) select_song $arg1;;
        "find"   ) search_music_store $arg1;; 
    esac

done
