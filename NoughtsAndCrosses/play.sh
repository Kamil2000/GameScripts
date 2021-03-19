#!/bin/bash

BOARD=("0" "0" "0" "0" "0" "0" "0" "0" "0")
PLAYER="0"
WINNER="0"

function display_board() {
    printf "Board:\n"
    echo "${BOARD[0]}|${BOARD[1]}|${BOARD[2]}"
    echo "${BOARD[3]}|${BOARD[4]}|${BOARD[5]}"
    echo "${BOARD[6]}|${BOARD[7]}|${BOARD[8]}"

}

function get_board_value() {
    echo "${BOARD[$(($1 + $2*3))]}"
}


function check_win_condition() {
    local index_x=0
    local index_y=0
    local player_to_verify=${1}
    local current_value=0
    local is_row_selected=1

    # verify x and y rows 
    while [ $index_x -ne 3 ]
    do
        index_y=0
        is_row_selected=1
        while [ $index_y -ne 3 ]
        do
            if [ "$player_to_verify" != "$(get_board_value $index_x $index_y)" ]
            then
                is_row_selected=0
                break
            fi
            index_y=$(($index_y + 1))
        done
        if [ $is_row_selected -eq 1 ]
        then
            WINNER=$player_to_verify
            return
        fi
        index_x=$(($index_x + 1))
    done

    index_y=0
    while [ $index_y -ne 3 ]
    do
        index_x=0
        is_row_selected=1
        while [ $index_x -ne 3 ]
        do
            if [ "$player_to_verify" != "$(get_board_value $index_x $index_y)" ]
            then
                is_row_selected=0
                break
            fi
            index_x=$(($index_x + 1))
        done
        if [ $is_row_selected -eq 1 ]
        then
            WINNER=$player_to_verify
            return
        fi
        index_y=$(($index_y + 1))
    done
    is_row_selected=1
    index_x=0
    index_y=0

    # check cross paths
    while [ $index_x -ne 3 ]
    do
        if [ "$player_to_verify" != "$(get_board_value $index_x $index_y)" ]
        then
            is_row_selected=0
            break
        fi
        index_x=$(($index_x + 1))
        index_y=$(($index_y + 1))
    done
    if [ $is_row_selected -eq 1 ]
    then
        WINNER=$player_to_verify
        return
    fi

    is_row_selected=1
    index_x=2
    index_y=0

    while [ $index_y -ne 3 ]
    do
        if [ "$player_to_verify" != "$(get_board_value $index_x $index_y)" ]
        then
            is_row_selected=0
            break
        fi
        index_x=$(($index_x - 1))
        index_y=$(($index_y + 1))
    done

    if [ $is_row_selected -eq 1 ]
    then
        WINNER=$player_to_verify
        return
    fi

}


function switch_player() {
    if [ $PLAYER -eq 1 ];
    then
        PLAYER="2"
    else
        PLAYER="1"
    fi
}

function validate_input_coord()
{
    if [ -z "$1" ]
    then
        echo "0"
        exit 0
    fi
    if [ $1 -lt  0 ]
    then
        echo "0"
        exit 0
    fi
    if [ $1 -ge  3 ]
    then
        echo "0"
        exit 0
    fi 
}

function validate_input_coords()
{
    if [ "$(validate_input_coord $1)" == "0" ]
    then
        echo "0"
        exit 0
    fi
    if [ "$(validate_input_coord $2)" == "0" ]
    then
        echo "0"
        exit 0
    fi
    if [ "$(get_board_value $1 $2)" != "0" ]
    then
        echo "0"
        exit 0
    fi
    echo "1"
}

function main() {
    switch_player
    while [ $WINNER -eq "0" ]
    do
        display_board
        local input_x=""
        local input_y=""
        echo -e "\nEnter coord field to mark for player ${PLAYER} (x coord and then y coord separated by nl):"
        read input_x
        read input_y
        # prform validation including avabaility of field
        if [ "$(validate_input_coords $input_x $input_y)" == "0" ]
        then
            echo "Entered coords are incorrect. Each coord should be integer value in range [0-2]."
            continue
        fi

        BOARD[$(( $input_x + input_y*3 ))]=$PLAYER
        check_win_condition $PLAYER
        if [ $WINNER -eq $PLAYER ]
        then
            echo "Player ${PLAYER} won the game. Exiting..."
            break
        fi
        switch_player
    done
}

main
