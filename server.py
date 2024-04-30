import socket
import threading

# Dictionary to keep track of clients
clients = {}
# A lock to ensure thread-safe operations on the clients dictionary
lock = threading.Lock()

# Function to send a message to all clients except the sender
def broadcast(message, _sender=None):
    for username, client_socket in clients.items():
        if username != _sender:
            client_socket.send(message)

# Function to handle individual client communication
def handle_client(client_socket, addr):
    username = None
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("No message received, client may have disconnected.")
                break

            parts = message.strip().split(' ')
            command = parts[0]

            if command == 'JOIN':
                if len(parts) < 2:
                    client_socket.send("Error: JOIN command requires a username.".encode('utf-8'))
                    continue
                username_temp = parts[1]
                lock.acquire()
                if username_temp in clients:
                    client_socket.send("Error: Username already in use. Try a different one.".encode('utf-8'))
                    lock.release()
                    continue
                clients[username_temp] = client_socket
                username = username_temp
                lock.release()
                print(f"{username} has joined the chat room.")
                client_socket.send(f"Welcome {username}, you have joined the chat room.".encode('utf-8'))

            elif command == 'LIST':
                if username is None:
                    client_socket.send("Error: You must JOIN before using LIST.".encode('utf-8'))
                    continue
                client_list = '\n'.join(clients.keys())
                client_socket.send(client_list.encode('utf-8'))

            elif command == 'MESG':
                if len(parts) < 3:
                    client_socket.send("Error: MESG command format is MESG <recipient> <message>.".encode('utf-8'))
                    continue
                _, recipient, *msg_content = parts
                msg_content = ' '.join(msg_content)
                if recipient in clients:
                    clients[recipient].send(f"{username}: {msg_content}".encode('utf-8'))
                else:
                    client_socket.send("Error: Recipient not found.".encode('utf-8'))

            elif command == 'BCST':
                if len(parts) < 2:
                    client_socket.send("Error: BCST command format is BCST <message>.".encode('utf-8'))
                    continue
                _, *msg_content = parts
                msg_content = ' '.join(msg_content)
                broadcast(f"{username}: {msg_content}".encode('utf-8'), _sender=username)

            elif command == 'QUIT':
                print(f"{username} has left the chat room.")
                break  # Exit loop to close socket

            else:
                client_socket.send("Unknown command.".encode('utf-8'))

    finally:
        if username:
            lock.acquire()
            if username in clients:
                del clients[username]
            lock.release()
            print(f"{username} disconnected.")
        client_socket.close()


#Fix BrokenPipe Error
def handle_client(client_socket, addr):
    username = None
    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                break  # Properly handle the closing of connection from client
            message = message.decode('utf-8')
            command = message.split(' ')[0]
            # Command processing here
    except Exception as e:
        print(f"Error handling client {username}: {e}")
    finally:
        if username:
            lock.acquire()
            if username in clients:
                del clients[username]
            lock.release()
        client_socket.close()
        print(f"{username} connection closed")

# Main server function to set up and run the server
def server_main(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to listen for connections on all interfaces
    server_socket.bind(('', port))
    server_socket.listen()

    print(f"Server listening on port {port}")

    # Accept connections in a loop and start a new thread for each client
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

# Entry point of the server application
if __name__ == '__main__':
    PORT = 8080  # Default port number to run the server on
    server_main(PORT)
