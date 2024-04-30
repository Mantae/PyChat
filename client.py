import socket
import threading

# Function to handle incoming messages from the server
def receive_messages(sock):
    while True:
        try:
            # Blocking call, waiting for new messages
            message = sock.recv(1024).decode('utf-8')
            # Print any message received from the server
            print(message)
        except OSError:  # An error occurred, likely the client has disconnected
            break

# Function to handle sending commands to the server
def send_commands(sock):
    while True:
        # Wait for user input in the console
        message = input("")
        if message:
            # Send the input message to the server
            sock.send(message.encode('utf-8'))
            # If the command is QUIT, disconnect and stop the loop
            if message.split(' ')[0] == 'QUIT':
                sock.close()
                break
#connection check and User Feedbakc 
def send_commands(sock):
    while True:
        command = input("Enter command: ").strip()
        if command:
            try:
                if command.startswith("JOIN"):
                    username = input("Enter your username: ").strip()
                    if username:
                        command += " " + username
                sock.send(command.encode('utf-8'))
                if command.split(' ')[0] == 'QUIT':
                    print("Disconnecting from the server.")
                    sock.close()
                    break
            except socket.error as e:
                print(f"Failed to send message: {e}")
                break

# Main function to setup and start the client
def main(server_host, server_port):
    # Create a socket object for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Establish a connection to the server
    client_socket.connect((server_host, server_port))

    # Indicate successful connection
    print("Connected to the server. You can start sending commands.")
    
    # Start a thread to keep listening for messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Start the command sending loop
    send_commands(client_socket)

# If this script is executed (not imported), run the main function
if __name__ == '__main__':
    HOST = '127.0.0.1'  # Define the server's hostname or IP address
    PORT = 8080        # Define the port used by the server for this client
    main(HOST, PORT)  # Start the main function with the host and port
