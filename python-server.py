import socket
import threading

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5555

def handle_client(client_socket, addr):
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"received: {message}")
    except KeyboardInterrupt:
        print("closing connection")
    finally:
        client_socket.close()
        

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()

    try:
        while True:
            print("awaiting connections...")
            client_socket, addr = server_socket.accept()
            print("client connected!")

            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("shutting down")
    finally:
        server_socket.close()

if __name__=="__main__":
    main()
