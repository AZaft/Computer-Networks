from socket import *

#local host only
HOST = "127.0.0.1"
PORT = 6789

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
    response = 'HTTP/1.1 404 Not Found\n\n'
    if (requestInfo[0] == 'GET'):
        try:
            file = open(requestInfo[1][1:])
            response = 'HTTP/1.1 200 OK\n\n' + file.read()
            file.close()
        except:
            #file was not found
            pass


    connectionSocket.send(response.encode())
    connectionSocket.close()

serverSocket.close()