import os
import sys
import time
from socket import *
from packet import Packet

def send_file(emulator_addr, emulator_port, sender_port, timeout, window_size, file_name):
    
    # Create the UDP sockets to send data to the emulator and recieve ACKs from the emulator
    sender_socket = socket(AF_INET, SOCK_DGRAM)
    ack_socket = socket(AF_INET, SOCK_DGRAM)
    ack_socket.bind(('', sender_port))

    # Read in the contents of the file
    with open(file_name, 'rb') as file:
        file_data = file.read()
    
    # Divide the file into 500 byte packets 
    packets = []
    nofpackets = 0
    for i in range(0, len(file_data), 500):
        packet = create_packet(file_data[i:i+500].decode(), nofpackets)
        packets.append(packet)
        nofpackets += 1

    # Intialize transmission variables
    base = 0        # sequence number of oldest unACKed packet
    nofunack = 0    # number of unACKed packets
    acks = set()    # set of sequence numbers that have been ACKed
    
    # Keep sending packets to reciever if not all packets have been ACKed
    while base < nofpackets:
        nofunack = 0
        for i in range(base, nofpackets):
            # Break when max number of packets have already been sent
            if nofunack == window_size:
                break
            # Transmit any packets that have not been ACKed yet
            if i not in acks:
                encoded_packet = packets[i].encode()
                sender_socket.sendto(encoded_packet, ((emulator_addr, emulator_port)))
                nofunack += 1
                write_to_seqnum(i, False)
        
        # Start a timer for group of packets 
        start = time.time()
        while time.time() - start < timeout / 1000:
            remaining_time = timeout / 1000 - (time.time() - start)
            ack_socket.settimeout(remaining_time)

            try:
                ack, _ = ack_socket.recvfrom(1024)
                typ, seqnum, length, data = Packet(ack).decode()

                # Check if ACK is for new sequence number
                if seqnum not in acks:
                    acks.add(seqnum)
                print(f'Recieved ACK for {seqnum}')
                write_to_ack(seqnum, False)

            except TimeoutError:
                break
        
        # Update value of base to sequence number of older unACKed packet
        while base in acks and base < nofpackets:
            base += 1
    
    # Send EOT packet to the receiver
    encoded_eot = Packet(2, -1, 0, '').encode()
    sender_socket.sendto(encoded_eot, ((emulator_addr, emulator_port)))
    write_to_seqnum(-1, True)

    # Wait to recieve EOT packet from receiver before closing sockets
    while True:
        ack_socket.settimeout(None)
        eot, _ = ack_socket.recvfrom(1024)
        typ, seqnum, length, data = Packet(eot).decode()
        if typ == 2:
            write_to_ack(-1, True)
            print(f'Recieved EOT')
            break

    sender_socket.close()
    ack_socket.close()


def create_packet(bytes, seqnum):

    length = len(bytes)
    packet = Packet(1, seqnum, length, bytes)
    
    return packet


def write_to_seqnum(seqnum, isEOT):

    if isEOT:
        write_string = f'EOT\n'
    else:
        write_string = f'{seqnum}\n'

    with open('seqnum.log', 'a') as file:
        file.write(write_string)


def write_to_ack(seqnum, isEOT):

    if isEOT:
        write_string = f'EOT\n'
    else:
        write_string = f'{seqnum}\n'

    with open('ack.log', 'a') as file:
        file.write(write_string)


if __name__ == "__main__":

    try:
        emulator_address = sys.argv[1]
        emulator_port = int(sys.argv[2])
        sender_port = int(sys.argv[3])
        timeout_interval = int(sys.argv[4])
        window_size = int(sys.argv[5])
        file_name = sys.argv[6]
    except IndexError as e:
        print("ERROR: NOT ENOUGH COMMAND LINE ARGUMENTS PROVIDED")
        sys.exit(1)
    except ValueError as e:
        print("ERROR: ONE OR MORE INVALID COMMAND LINE ARGUMENTS")
        sys.exit(1)

    if not os.path.exists(file_name):
        print(f'ERROR: FILE {file_name} DOES NOT EXIST')
        sys.exit(1)
    if os.path.exists('seqnum.log'):
        os.remove('seqnum.log')
    if os.path.exists('ack.log'):
        os.remove('ack.log')

    if window_size <= 0:
        print(f'ERROR: INVALID WINDOW SIZE')
        sys.exit(1)
    
    if timeout_interval <= 0:
        print(f'ERROR: INVALID TIMEOUT INTERVAL')
        sys.exit(1)

    send_file(emulator_address, emulator_port, sender_port, timeout_interval, window_size, file_name)
