# Programming Assignment #2

## Running program

The program can be run in the terminal with the command "python analysis_pcap_tcp.py" depending on the python installation. Library dpkt must also be installed (pip install dpkt). The HW was completed in python version 3.10.8.

## High level summary
There are comments throughout the code that explain each general step in what I do

### Part A
To find number of flows, I check the tcp SYN flags and find flows from sender to receiver; there were 3.

To find the first two transactions for each flow:
I first find the first two transactions sent from sender that aren't part of the handshake using data from tcp object.
Then I find the responses to these requests from the receiver using sequence and ack values; I also make sure source/dest ports match up to make sure responses are for the right flow when doing this.
transactions are stored in dictionary object organized by flows.

To find throughput:
I check total data sent from the sender (source_ip == sender) including size of headers using len(tcp) for each flow for the duration of the flow.

### Part B


