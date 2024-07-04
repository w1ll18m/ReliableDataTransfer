#!/bin/bash

#Run script for the sender as a part of 
#Assignment 2
#Computer Networks (CS 456)
#Number of parameters: 6
#Parameters:
#    $1: <emulator_address>
#    $2: <emulator_port>
#    $3: <sender_port>
#    $4: <timeout_interval>
#    $5: <window_size>
#    $6: <file_name>

#For Python implementation
python sender.py "$1" "$2" "$3" "$4" "$5" "$6" 