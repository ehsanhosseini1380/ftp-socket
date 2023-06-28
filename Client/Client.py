import socket
import os
import struct
import hashlib

# Initialize socket stuff
TCP_IP = "127.0.0.1"  # Server IP address
TCP_PORT = 1456  # Server port
BUFFER_SIZE = 1024  # Standard size
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

def receive_data(size):
    data = s.recv(size)
    if not data:
        raise ConnectionError("Connection closed by server.")
    return data

def send_data(data):
    s.send(data)

def authenticate(username, password):
    send_data("AUTH {}:{}".format(username, password).encode())
    response = receive_data(BUFFER_SIZE).decode()
    if response == "OK":
        return True
    else:
        print("Authentication failed.")
        return False

def upld(file_path):
    # Send command to server
    send_data(b"UPLD")

    # Wait for server response before sending file details
    receive_data(1)

    # Send file name length and file name
    file_name = os.path.basename(file_path)
    file_name_bytes = file_name.encode()
    send_data(struct.pack("h", len(file_name_bytes)))
    send_data(file_name_bytes)

    # Wait for server response before sending file size
    receive_data(1)

    # Send file size
    file_size = os.path.getsize(file_path)
    send_data(struct.pack("i", file_size))

    # Send file content
    print("\nUploading file: {}".format(file_name))
    with open(file_path, "rb") as file:
        for data in iter(lambda: file.read(BUFFER_SIZE), b""):
            send_data(data)
    print("Upload complete.")

    # Receive and display upload performance details
    upload_time = struct.unpack("f", receive_data(4))[0]
    received_file_size = struct.unpack("i", receive_data(4))[0]
    print("\nUpload time: {:.2f} seconds".format(upload_time))
    print("Received file size: {} bytes".format(received_file_size))

    # Receive and compare MD5 hash of the uploaded file
    md5_hash_digest = receive_data(32)
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(BUFFER_SIZE), b""):
            md5_hash.update(chunk)
    if md5_hash.digest() == md5_hash_digest:
        print("MD5 hash verification: Passed")
    else:
        print("MD5 hash verification: Failed")

def list_files(sock):
    # Send command to server
    send_data(sock, b"LIST")

    # Receive number of files
    num_files = struct.unpack("i", receive_data(sock, 4))[0]
    print("\nNumber of files in directory: {}\n".format(num_files))

    total_directory_size = 0
    for _ in range(num_files):
        # Receive file name size
        file_name_size = struct.unpack("i", receive_data(sock, 4))[0]

        # Receive file name
        file_name = receive_data(sock, file_name_size).decode()

        # Receive file size
        file_size = struct.unpack("i", receive_data(sock, 4))[0]
        total_directory_size += file_size

        # Receive file creation time
        creation_time = receive_data(sock, 19).decode()

        # Receive file modification time
        modification_time = receive_data(sock, 19).decode()

        print("File Name: {}".format(file_name))
        print("Size: {} bytes".format(file_size))
        print("Creation Time: {}".format(creation_time))
        print("Modification Time: {}\n".format(modification_time))

    # Receive total directory size
    total_directory_size = struct.unpack("q", receive_data(sock, 8))[0]
    print("Total Directory Size: {} bytes\n".format(total_directory_size))

def quit_ftp():
    # Send command to server
    send_data(b"QUIT")

    # Wait for server response before closing the connection
    receive_data(1)

    # Close the connection
    s.close()
    print("\nDisconnected from server.")
    exit()

# Main program loop
while True:
    print("\n--- FTP Client Menu ---")
    print("1. Authenticate")
    print("2. Upload file")
    print("3. List files")
    print("4. Quit")

    choice = input("Enter your choice (1-4): ")
    if choice == "1":
        username = input("Username: ")
        password = input("Password: ")
        if authenticate(username, password):
            print("\nAuthentication successful.")
        else:
            print("\nAuthentication failed.")
    elif choice == "2":
        file_path = input("Enter the file path: ")
        if os.path.isfile(file_path):
            upld(file_path)
        else:
            print("Invalid file path.")
    elif choice == "3":
        list_files(s)
    elif choice == "4":
        quit_ftp()
    else:
        print("Invalid choice. Please try again.")
