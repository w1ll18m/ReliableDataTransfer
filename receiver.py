import os
import sys
from socket import *
from packet import Packet

def receive_file(emulator_addr, emulator_port, receiver_port, buffer_size, file_name):

    # Create the UDP sockets to send data to the emulator and recieve ACKs from the emulator
    receiver_socket = socket(AF_INET, SOCK_DGRAM)
    receiver_socket.bind(('', receiver_port))
    ack_socket = socket(AF_INET, SOCK_DGRAM)

    # Initialize transmission variables
    buffer = {}
    last_written = -1

    while True:
        packet, addr = receiver_socket.recvfrom(1024)
        typ, seqnum, length, data = Packet(packet).decode()

        if typ == 1:
            print(f'Received packet {seqnum}')

            # Drop the packet if the buffer is full
            if seqnum > last_written + buffer_size:
                write_to_arrival(seqnum, False, False, True)
                continue
            # Send an ACK for packets with sequence numbers that have already been written to file
            if seqnum <= last_written:
                encoded_ack = Packet(0, seqnum, 0, '').encode()
                ack_socket.sendto(encoded_ack, (emulator_addr, emulator_port))
                write_to_arrival(seqnum, False, False, True)
                continue
            # Add packet to the buffer if it is not full or hasn't been written to file yet
            if seqnum not in buffer:
                buffer[seqnum] = data
                write_to_arrival(seqnum, False, True, False)
            else:
                write_to_arrival(seqnum, False, False, True)
            
            # Write data from buffered packets if it follows the last packet written to file
            while last_written + 1 in buffer:
                write_to_file(file_name, buffer[last_written + 1])
                del buffer[last_written + 1]
                last_written += 1

            # Send an ACK for the packet
            encoded_ack = Packet(0, seqnum, 0, '').encode()
            ack_socket.sendto(encoded_ack, (emulator_addr, emulator_port))

        # Send own EOT packet before closing sockets
        elif typ == 2:
            print('Received EOT')
            encoded_eot = Packet(2, -1, 0, '').encode()
            ack_socket.sendto(encoded_eot, ((emulator_addr, emulator_port)))
            write_to_arrival(seqnum, True, False, False)
            break
        
    receiver_socket.close()
    ack_socket.close()


def write_to_file(file_name, write_string):

    bytes = write_string.encode('ASCII')

    with open(file_name, 'ab') as file:
        file.write(bytes)


def write_to_arrival(seqnum, isEOT, isBuffered, isDropped):

    if isEOT:
        write_string = f'EOT\n'
    else:
        write_string = f'{seqnum}'
        if isBuffered:
            write_string += ' B\n'
        elif isDropped:
            write_string += ' D\n'

    with open('arrival.log', 'a') as file:
        file.write(write_string)


if __name__ == "__main__":

    try:
        emulator_address = sys.argv[1]
        emulator_port = int(sys.argv[2])
        receiver_port = int(sys.argv[3])
        buffer_size = int(sys.argv[4])
        file_name = sys.argv[5]
    except IndexError as e:
        print("ERROR: NOT ENOUGH COMMAND LINE ARGUMENTS PROVIDED")
        sys.exit(1)
    except ValueError as e:
        print("ERROR: ONE OR MORE INVALID COMMAND LINE ARGUMENTS")
        sys.exit(1)

    if os.path.exists(file_name):
        os.remove(file_name)
    if os.path.exists('arrival.log'):
        os.remove('arrival.log')
    
    if buffer_size <= 0:
        print(f'ERROR: INVALID BUFFER SIZE')
        sys.exit(1)

    receive_file(emulator_address, emulator_port, receiver_port, buffer_size, file_name)