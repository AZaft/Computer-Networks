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


requests_sent = {}
requests_received = {}

#holds rtt for each request split by flow
rtt = {0:[], 1:[], 2:[]}


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
        flow = [2, tcp.sport, source_ip, tcp.dport, dest_ip, 0, [], 0, 0]

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
            id = str(f+1) + ":" + str(flow[0])

            if tcp.sport in flow and tcp.dport in flow and source_ip in flow and dest_ip in flow: 
                
                if flow[0] > 0:
                    transactions[ id ] = {
                        "sent": {
                            "SPORT": tcp.sport,
                            "SEQ": tcp.seq,
                            "ACK": tcp.ack,
                            "WIN": tcp.win
                        },
                    }
                    flow[0] -= 1
                    
            #if not congestion_windows[f][1]: congestion_windows[f][0] += 1


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
                    #congestion_windows[int(key[0:1]) - 1][1] = True


    #calculate total data sent for each flow (througput)
    if is_ack and source_ip == sender and len(tcp.data) > 0 and not is_syn and not is_fin:
        for f in tcp_flows:
            if tcp.sport in f and tcp.dport in f and source_ip in f and dest_ip in f:
                f[5] += len(tcp)




    #calculate how many times triple duplicates are sent to the receiver for each flow
    if is_ack and source_ip == receiver and not is_syn and not is_fin:
         for f in range(len(tcp_flows)):
            flow = tcp_flows[f]
            if tcp.sport in flow and tcp.dport in flow and source_ip in flow and dest_ip in flow : 
                if tcp.ack == flow[8]:
                    flow[6].append(tcp.ack)

                else: 
                    if len(flow[6]) >= 3:
                        flow[7] += 1
                        flow[6] = []

                flow[8] = tcp.ack


    #record first 3 requests sent for each flow in object (requests_sent)
    if is_ack and source_ip == sender and len(tcp.data) > 0 and not is_syn and not is_fin:
        for f in range(len(tcp_flows)):
            flow = tcp_flows[f]
            if tcp.sport in flow and tcp.dport in flow and source_ip in flow and dest_ip in flow: 
                expected_ack = tcp.seq + len(tcp.data)
                currentRequest = {
                    "expected": expected_ack,
                    "SEQ": tcp.seq,
                    "ACK": tcp.ack,
                    "TIME": time
                }

                if f in requests_sent:
                    if len(requests_sent[f][0]) < 3:
                        requests_sent[f][0].append(currentRequest)
                else:
                    requests_sent[f] = [[currentRequest], 1]

                
    
    # capture 3 responses for the above requests (requests_sent) for each flow in object and record rtt for each
    if is_ack and source_ip == receiver and not is_syn and not is_fin:
        for r in requests_sent:
            flow_requests = requests_sent[r][0]
        
            for request in flow_requests:
                #corresponding ack found
                if tcp.ack >= request["expected"]:
                    currentRequest = {
                        "SEQ": tcp.seq,
                        "ACK": tcp.ack,
                        "TIME": time
                    }
                    
                    if r in requests_received: 
                        if len(requests_received[r]) < 3:
                            rtt[r].append(time - request["TIME"])
                            requests_received[r].append(currentRequest)
                    else:
                        rtt[r].append(time - request["TIME"])
                        requests_received[r] = [currentRequest]

    

    old_time = time    


#Array to hold congestion windows for first three request
congestion_windows = [[0,0,0],[0,0,0],[0,0,0]]

#helper to check when rtt is over
end_times = [[0,0,0],[0,0,0],[0,0,0]]
congestion_index = [0,0,0]

f = open('assignment2.pcap', 'rb')
pcap = dpkt.pcap.Reader(f)

for time, buf in pcap:
    
    eth = dpkt.ethernet.Ethernet(buf)
    ip = eth.data
    tcp = ip.data
    source_ip = '.'.join(f'{c}' for c in ip.src)
    dest_ip = '.'.join(f'{c}' for c in ip.dst)
    request_time = time - old_time
    is_syn = False
    is_fin = False
    is_ack = False
    if tcp.flags & dpkt.tcp.TH_SYN: is_syn = True
    if tcp.flags & dpkt.tcp.TH_FIN: is_fin = True
    if tcp.flags & dpkt.tcp.TH_ACK: is_ack = True

    if is_ack and source_ip == sender and len(tcp.data) and not is_syn:
        for f in range(len(tcp_flows)):
            flow = tcp_flows[f]
            if tcp.sport in flow and tcp.dport in flow and source_ip in flow and dest_ip in flow: 
                cwnd = congestion_windows[f]
                end = end_times[f]
                i = congestion_index[f]

                if i >= 3: continue

                
                
                if not cwnd[i]:
                    end[i] = rtt[f][i] + time
                    cwnd[i] += 1
                        

                
                if cwnd[i] and end[i]:
                    if end[i]:
                        if end[i] >= time:
                            cwnd[i] += 1
                        else: congestion_index[f] += 1
                
               
# print(tcp_flows)
# print(transactions)
# print(requests_sent)
# print(requests_received)
# print(rtt)
# print(rtt)
# print(congestion_windows)


#print tcp_flows in readable format
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

    #print first three congestion windows from flow
    print("FIRST THREE CONGESTION WINDOWS: " + str(congestion_windows[i]))

    #print timeouts from triple duplicate acks
    print("TRIPLE DUPLICATE ACK RETRANSMISSIONS: " + str(tcp_flows[i][7]))

   

    print("\n")