from socket import *

#local host only
HOST = "127.0.0.1"
PORT = 8888
file_cache = {}

def sendRequest(url): 
    host, seperator, path = url.partition('/')
    try:
        serverName = host
        serverPort = 80
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName,serverPort))

        #request to send to server
        request = f"GET /{path} HTTP/1.1\r\nHost:{host}\r\n\r\n"
        clientSocket.send(request.encode())

        #response from server
        response = clientSocket.recv(64000)
        clientSocket.close()
        return response
    except:
        #get request was not successful
        return 'HTTP/1.1 404 Not Found\n\n'.encode()

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind((HOST,PORT))
serverSocket.listen(1)
print("Server is listening on port: " + str(PORT))
while True:
    connectionSocket, addr = serverSocket.accept()
    request = connectionSocket.recv(1024).decode()

    #parsing http request
    fields = request.split('\r\n', 1)
    requestInfo = fields[0].split(" ")

    #if its not a get request or file is not found send 404 not found 
    response = 'HTTP/1.1 404 Not Found\n\n'.encode()
    
    #sometimes empty request is sent causing error
    if len(requestInfo) < 2:
        print("empty error")
        continue

    request_url = requestInfo[1][1:]
     #getting rid of https:// or http:// if it exists
    if "://" in request_url:
        request_url = request_url.split("://",1)[-1]
    
    check_cache = file_cache.get(request_url)
    if check_cache != None:
        #if response is cached send that
        print("Sent cached request")
        response = check_cache
    else:
        #if response if not cached, sent request to url and cache the response
        response = sendRequest(request_url)
        file_cache[request_url] = response
        print("Was not cached, made request")


    connectionSocket.send(response)
    connectionSocket.close()

serverSocket.close()