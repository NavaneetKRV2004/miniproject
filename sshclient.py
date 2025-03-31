import socket

SERVER_IP = '127.0.0.1'  # Replace with server's IP
PORT = 5005

def communicate_with_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, PORT))
        
        # Receive welcome message from server
        welcome_message = s.recv(1024).decode()
        print(welcome_message)
        
        while True:
            # Send a message to the server
            message = input("Enter your message to send to the server: ")
            if message.strip().lower() == "exit":
                print("Exiting the chat.")
                break
            s.sendall(message.encode())
            
            # Receive and print server's response
            data = s.recv(1024).decode()
            print(f"Server: {data.strip()}")

if __name__ == "__main__":
    communicate_with_server()
