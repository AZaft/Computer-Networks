import dpkt

f = open('assignment2.pcap', 'rb')
pcap = dpkt.pcap.Reader(f)

old_time = 0


#iter = 10

#array to hold tcp flows and their info
tcp_flows = []

flow_count = 1

#these ips are used to determine direction of flow
sender = '130.245.145.12'
receiver = '128.208.2.198'

transactions = {}

for time, buf in pcap:

    

    #read bytes into objects using dpkt
    eth = dpkt.ethernet.Ethernet(buf)
    ip = eth.data
    tcp = ip.data

    #convert ip bytes to text for printing
    source_ip = '.'.join(f'{c}' for c in ip.src)
    dest_ip = '.'.join(f'{c}' for c in ip.dst)

    #how much time current request took
    request_time = time - old_time
    #print(request_time)

    #tcp flags
    is_syn = False
    is_fin = False
    is_ack = False

    #check what type of flags in current request
    if tcp.flags & dpkt.tcp.TH_SYN: is_syn = True

    if tcp.flags & dpkt.tcp.TH_FIN: is_fin = True

    if tcp.flags & dpkt.tcp.TH_ACK: is_ack = True

    # print(is_syn)
    # print(is_fin)
    # print("\n")


    #if SYN add flow to tcp_flows
    if is_syn:
        flow = [2, tcp.sport, source_ip, tcp.dport, dest_ip, 0]

        #don't add to tcp_flows if duplicate flow
        dup = False
        for f in tcp_flows:
            if tcp.sport in f and tcp.dport in f and source_ip in f and dest_ip:
                dup = True

        if not dup: tcp_flows.append(flow)

    

    #get first two sends with real data
    if is_ack and source_ip == sender and len(tcp.data) > 0 and not is_syn:
        #find for what flow this ack belongs to and append transaction (done only twice for each flow)
        for f in range(len(tcp_flows)):
            flow = tcp_flows[f]

            if tcp.sport in flow and tcp.dport in flow and source_ip in flow and dest_ip in flow and flow[0] > 0: 

                id = str(f+1) + ":" + str(flow[0])

                transactions[ id ] = {
                    "sent": {
                        "SPORT": tcp.sport,
                        "SEQ": tcp.seq,
                        "ACK": tcp.ack,
                        "WIN": tcp.win
                    }
                }

                flow[0] -= 1

    #get responses of first two sends of each flow based on sequence and ack numbers
    #use source port/destination port to determine response is for the right flows
    if is_ack and source_ip == receiver and not is_syn:
        for key in transactions:
            t = transactions[key]
            if t["sent"]["SEQ"] < tcp.ack and t["sent"]["SPORT"] == tcp.dport:
                if "received" not in t:
                    res = {
                        "SEQ": tcp.seq,
                        "ACK": tcp.ack,
                        "WIN": tcp.win
                    }
                    t["received"] = res


    #calculate total data sent for each flow (througput)
    if is_ack and source_ip == sender and len(tcp) > 0 and not is_syn:
        for f in tcp_flows:
            if tcp.sport in f and tcp.dport in f and source_ip in f and dest_ip in f:
                f[5] += len(tcp)


    old_time = time



    

#print tcp_flows in readable format
print(tcp_flows)
print(transactions)
for i in range(len(tcp_flows)):
    print("FLOW #" + str(i+1) + ":")
    print("   Source port: " + str(tcp_flows[i][1]))
    print("   Source IP: " + str(tcp_flows[i][2]))
    print("   Destination port: " + str(tcp_flows[i][3]))
    print("   Destination IP: " + str(tcp_flows[i][4]))

    #print transaction information
    print("FIRST TWO TRANSACTIONS:")

    print("   SENT: ")

    for j in range(1, -1, -1):
        id = str(i+1) + ":" + str(j+1)
        transaction = transactions[id]
        print("     SEQ: " + str(transaction["sent"]["SEQ"]) + ", ACK: " +  str(transaction["sent"]["ACK"]) + ", WINDOW: " +  str(transaction["sent"]["WIN"]) )

    print("   RECEIVED: ")

    for j in range(1, -1, -1):
        id = str(i+1) + ":" + str(j+1)
        transaction = transactions[id]
        print("     SEQ: " + str(transaction["received"]["SEQ"]) + ", ACK: " +  str(transaction["received"]["ACK"]) + ", WINDOW: " +  str(transaction["received"]["WIN"]) )
    
    #print throughput
    print("SENDER THROUGHPUT: " + str(tcp_flows[i][5]))

    

    print("\n")