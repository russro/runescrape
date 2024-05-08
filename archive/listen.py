
import socket

def listen():
    # specify Host and Port
    HOST = ''
    PORT = 8888

    # create a socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind the socket to the host and port
    server.bind((HOST, PORT))

    # start listening for connections
    server.listen(1)

    print('Listening for client...')
    conn, addr = server.accept()
    print('Connected with', addr)