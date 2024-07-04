#!/bin/bash

#Run script for the receiver as a part of 
#Assignment 2
#Computer Networks (CS 456)
#Number of parameters: 5
#Parameters:
#    $1: <emulator_address>
#    $2: <emulator_port>
#    $3: <receiver_port>
#    $4: <buffer_size>
#    $5: <file_name>

#For Python implementation
python receiver.py "$1" "$2" "$3" "$4" "$5"
