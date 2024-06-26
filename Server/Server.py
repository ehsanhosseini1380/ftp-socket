import socket
import sys
import time
import os
import struct
import ssl

print("\nWelcome to the FTP server.\n\nTo get started, connect a client.")

TCP_IP = "127.0.0.1"  # Only a local server
TCP_PORT = 1456  # Just a random choice
BUFFER_SIZE = 1024  # Standard size
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile="certificate.crt", keyfile="private.key")

s_ssl = ssl_context.wrap_socket(s, server_side=True)

s_ssl.bind((TCP_IP, TCP_PORT))
s_ssl.listen(1)
conn, addr = s_ssl.accept()
print("\nConnected to by address: {}".format(addr))
VALID_USERNAME = "admin"
VALID_PASSWORD = "password"


def receive_data(size):
    data = conn.recv(size)
    if not data:
        raise ConnectionError("Connection closed by client.")
    return data


def send_data(data):
    conn.send(data)


def handle_auth_request(request):
    _, credentials = request.split(" ")
    username, password = credentials.split(":")
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        send_data("OK".encode())
        return True
    else:
        send_data("FAIL".encode())
        return False


authenticated = False

while not authenticated:
    data = receive_data(BUFFER_SIZE)
    if data.startswith(b"AUTH"):
        if handle_auth_request(data.decode()):
            authenticated = True
        # else:
        #     conn.close()
        #     sys.exit(1)
        #     continue

# def upld():
#     # Send message once server is ready to receive file details
#     send_data(b"1")

#     # Receive file name length, then file name
#     file_name_size = struct.unpack("h", receive_data(2))[0]
#     file_name = receive_data(file_name_size)

#     # Send message to let client know server is ready for document content
#     send_data(b"1")

#     # Receive file size
#     file_size = struct.unpack("i", receive_data(4))[0]

#     # Initialize and enter loop to receive file content
#     start_time = time.time()
#     with open(file_name, "wb") as output_file:
#         print("\nReceiving...")
#         bytes_received = 0
#         while bytes_received < file_size:
#             data = receive_data(min(BUFFER_SIZE, file_size - bytes_received))
#             output_file.write(data)
#             bytes_received += len(data)
#     print("\nReceived file: {}".format(file_name))

#     # Send upload performance details
#     send_data(struct.pack("f", time.time() - start_time))
#     send_data(struct.pack("i", file_size))

def upld():
    # Send message once server is ready to receive file details
    send_data(b"1")

    # Receive file name length, then file name
    file_name_size = struct.unpack("h", receive_data(2))[0]
    file_name = receive_data(file_name_size)

    # Send message to let client know server is ready for document content
    send_data(b"1")

    # Receive file size
    file_size = struct.unpack("i", receive_data(4))[0]

        # Decode file name from bytes to string
    file_name = file_name.decode("utf-8")

    # Split file_name into directory path and file name components
    file_dir, file_name = os.path.split(file_name)

    # Create directory path if it does not exist
    # if file_dir:
    #     # os.makedirs(os.path.join("Files", file_dir), exist_ok=True)
    #     file_path = os.path.join("Files", file_dir, file_name)
    # else:

    file_path = os.path.join(os.path.dirname(os.getcwd()), "Files", file_name)
    # Initialize and enter loop to receive file content
    start_time = time.time()
    with open(file_path, "wb") as output_file:
        print("\nReceiving...")
        bytes_received = 0
        while bytes_received < file_size:
            data = receive_data(min(BUFFER_SIZE, file_size - bytes_received))
            output_file.write(data)
            bytes_received += len(data)
    print("\nReceived file: {}".format(file_path))

    # Send upload performance details
    send_data(struct.pack("f", time.time() - start_time))
    send_data(struct.pack("i", file_size))


def list_files():
    print("Listing files...")
    # Get list of files in directory
    base_dir = os.path.join(os.path.dirname(os.getcwd()), "Files")
    file_list = os.listdir(base_dir)

    # Send over the number of files, so the client knows what to expect (and avoid some errors)
    send_data(struct.pack("i", len(file_list)))

    total_directory_size = 0
    for file_name in file_list:
        file_abs_path = os.path.join(base_dir, file_name)
        file_name_bytes = file_name.encode()
        file_size = os.path.getsize(file_abs_path)
        file_modify_time = os.path.getmtime(file_abs_path)
        file_create_time = os.path.getctime(file_abs_path)
        total_directory_size += file_size

        # File name size
        send_data(struct.pack("i", len(file_name_bytes)))

        # File name
        send_data(file_name_bytes)

        # File content size
        send_data(struct.pack("i", file_size))

        # File last modify time
        send_data(struct.pack("i", int(file_modify_time)))

        # File create time
        send_data(struct.pack("i", int(file_create_time)))

        # Make sure that the client and server are synchronized
        receive_data(BUFFER_SIZE)

    # Sum of file sizes in directory
    send_data(struct.pack("i", total_directory_size))

    # Final check
    receive_data(BUFFER_SIZE)
    print("Successfully sent file listing")


def dwld():
    send_data(b"1")

    # Receive file name length and file name
    file_name_length = struct.unpack("h", receive_data(2))[0]
    base_dir = os.path.join(os.path.dirname(os.getcwd()), "Files")
            # Decode file name from bytes to string
    file_name = os.path.join(base_dir, receive_data(file_name_length).decode("utf-8"))


    if os.path.isfile(file_name):
        # File exists, send file size
        send_data(struct.pack("i", os.path.getsize(file_name)))
    else:
        # File doesn't exist, send error code
        print("File name not valid")
        send_data(struct.pack("i", -1))
        return

    # Wait for confirmation to send file
    receive_data(BUFFER_SIZE)

    # Enter loop to send file
    start_time = time.time()
    print("Sending file...")
    with open(file_name, "rb") as content:
        while True:
            data = content.read(BUFFER_SIZE)
            if not data:
                break
            send_data(data)

    # Get client's go-ahead, then send download details
    receive_data(BUFFER_SIZE)
    send_data(struct.pack("f", time.time() - start_time))


def delf():
    # Send go-ahead
    send_data(b"1")

    # Get file details
    file_name_length = struct.unpack("h", receive_data(2))[0]
    # file_name = receive_data(file_name_length)
    base_dir = os.path.join(os.path.dirname(os.getcwd()), "Files")
            # Decode file name from bytes to string
    file_name = os.path.join(base_dir, receive_data(file_name_length).decode("utf-8"))

    # Check if file exists
    if os.path.isfile(file_name):
        send_data(struct.pack("i", 1))
    else:
        # File doesn't exist
        send_data(struct.pack("i", -1))

    # Wait for deletion confirmation
    confirm_delete = receive_data(BUFFER_SIZE)
    if confirm_delete == b"Y":
        try:
            # Delete file
            os.remove(file_name)
            send_data(struct.pack("i", 1))
        except:
            # Unable to delete file
            print("Failed to delete {}".format(file_name))
            send_data(struct.pack("i", -1))
    else:
        # User abandoned deletion
        # The server probably received "N", but else used as a safety catch-all
        print("Delete abandoned by client!")


def quit_server():
    send_data(b"1")
    # Close the connection and the server
    conn.close()
    s_ssl.close()    
    # Restart the server
    os.execl(sys.executable, sys.executable, *sys.argv)


while True:
    # Enter into a while loop to receive commands from the client
    print("\n\nWaiting for instruction")
    data = receive_data(BUFFER_SIZE)
    print("\nReceived instruction: {}".format(data))

    # Check the command and respond correctly
    if data == b"UPLD":
        upld()
    elif data == b"LIST":
        list_files()
    elif data == b"DWLD":
        dwld()
    elif data == b"DELF":
        delf()
    elif data == b"QUIT":
        quit_server()

    # Reset the data to loop
    data = None
