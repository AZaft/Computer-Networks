import dpkt

f = open('assignment2.pcap', 'rb')
pcap = dpkt.pcap.Reader(f)

old_time = 0


iter = 5

for time, buf in pcap:

    eth = dpkt.ethernet.Ethernet(buf)
    ip = eth.data
    tcp = ip.data


    print(time - old_time)
    old_time = time

    iter -= 1
    if iter == 0:
        break



    

f.close()