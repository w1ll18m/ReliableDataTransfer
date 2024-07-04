# Reliable Data Transfer Protocol Over Unreliable Channel

The sender and receiver programs were tested on:
1. ubuntu2204-002.student.cs.uwaterloo.ca running the network emulator program
2. ubuntu2204-004.student.cs.uwaterloo.ca running the receiver program
3. ubuntu2204-006.student.cs.uwaterloo.ca running the sender program

The testing process was as follows:
1. run "python network_emulator.py 1313 ubuntu2204-004.student.cs.uwaterloo.ca 1314 1315 ubuntu2204-006.student.cs.uwaterloo.ca 1316 1000 0.9" in the 002 terminal
2. run "python receiver.py ubuntu2204-002.student.cs.uwaterloo.ca 1315 1314 5 my_long_output.txt" in the 004 terminal
3. run "python sender.py ubuntu2204-002.student.cs.uwaterloo.ca 1313 1316 70 5 my_long_input.txt" in the 006 terminal

Note that ports 1314-1316 may not be available at another time so choose other ports for UDP socket as needed.
Input files "my_short_input.txt" and "my_long_input.txt" are included as part of the submission.

python receiver.py $1 $2 $3 $4 $5 
Parameters:
    $1: emulator_address
    $2: emulator_port
    $3: receiver_port
    $4: buffer_size
    $5: file_name

python sender.py $1 $2 $3 $4 $5 $6
Parameters:
    $1: emulator_address
    $2: emulator_port
    $3: sender_port
    $4: timeout_interval
    $5: window_size
    $6: file_name
