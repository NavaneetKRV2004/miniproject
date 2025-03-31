import socket

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5005       # Arbitrary non-privileged port

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}...")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                conn.sendall(b"Welcome! Type your message:\n")
                while True:
                    data = conn.recv(1024).decode()
                    if not data:
                        break  # Connection closed
                    print(f"Received from client: {data.strip()}")

                    # Send a response
                    response = input("Enter a message to send back to the client: ")
                    conn.sendall(response.encode())

if __name__ == "__main__":
    start_server()
