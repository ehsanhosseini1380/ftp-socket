import socket
import sys
import os
import struct

TCP_IP = "127.0.0.1"
TCP_PORT = 1456
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def conn():
    # Connect to the server
    print("Sending server request...")
    try:
        s.connect((TCP_IP, TCP_PORT))
        print("Connection successful")
        # Send authentication credentials
        username = input("Enter username: ")
        password = input("Enter password: ")
        s.sendall(f"AUTH {username}:{password}".encode())
        auth_response = s.recv(BUFFER_SIZE).decode()
        if auth_response != "OK":
            print("Authentication failed. Disconnecting.")
            s.close()
            sys.exit(1)
    except Exception as e:
        print("Connection unsuccessful. Make sure the server is online.")
        print(f"Error: {str(e)}")

# Rest of the client code...


def upld(file_name):
    # Upload a file
    print("\nUploading file: {}...".format(file_name))
    try:
        # Check if the file exists
        if not os.path.isfile(file_name):
            print("Couldn't open file. Make sure the file name was entered correctly.")
            return
        # Make upload request
        s.sendall(b"UPLD")
    except Exception as e:
        print("Couldn't make server request. Make sure a connection has been established.")
        print(f"Error: {str(e)}")
        return
    try:
        # Wait for server acknowledgement then send file details
        # Wait for server ok
        s.recv(BUFFER_SIZE)
        # Send file name size and file name
        file_name_size = struct.pack("h", len(file_name.encode()))
        s.send(file_name_size)
        s.send(file_name.encode())
        # Wait for server ok then send file size
        s.recv(BUFFER_SIZE)
        file_size = os.path.getsize(file_name)
        s.send(struct.pack("i", file_size))
    except Exception as e:
        print("Error sending file details")
        print(f"Error: {str(e)}")
        return
    try:
        # Send the file in chunks defined by BUFFER_SIZE
        # Doing it this way allows for unlimited potential file sizes to be sent
        with open(file_name, "rb") as content:
            print("\nSending...")
            while True:
                chunk = content.read(BUFFER_SIZE)
                if not chunk:
                    break
                s.send(chunk)
            # Get upload performance details
            upload_time = struct.unpack("f", s.recv(4))[0]
            upload_size = struct.unpack("i", s.recv(4))[0]
            print("\nSent file: {}\nTime elapsed: {}s\nFile size: {}b".format(file_name, upload_time, upload_size))
    except Exception as e:
        print("Error sending file")
        print(f"Error: {str(e)}")
        return

def list_files():
    # List the files available on the file server
    print("Requesting files...\n")
    try:
        # Send list request
        s.sendall(b"LIST")
    except Exception as e:
        print("Couldn't make server request. Make sure a connection has been established.")
        print(f"Error: {str(e)}")
        return
    try:
        # First get the number of files in the directory
        number_of_files = struct.unpack("i", s.recv(4))[0]
        # Then enter into a loop to receive details of each, one by one
        for _ in range(number_of_files):
            # Get the file name size first to slightly lessen the amount transferred over the socket
            file_name_size = struct.unpack("i", s.recv(4))[0]
            file_name = s.recv(file_name_size).decode()
            # Also get the file size for each item on the server
            file_size = struct.unpack("i", s.recv(4))[0]
            print("\t{} - {}b".format(file_name, file_size))
            # Make sure that the client and server are synchronized
            s.sendall(b"1")
        # Get total size of the directory
        total_directory_size = struct.unpack("i", s.recv(4))[0]
        print("Total directory size: {}b".format(total_directory_size))
    except Exception as e:
        print("Couldn't retrieve listing")
        print(f"Error: {str(e)}")
        return
    try:
        # Final check
        s.sendall(b"1")
        return
    except Exception as e:
        print("Couldn't get final server confirmation")
        print(f"Error: {str(e)}")
        return

def dwld(file_name):
    # Download given file
    print("Downloading file: {}".format(file_name))
    try:
        # Send server request
        s.sendall(b"DWLD")
    except Exception as e:
        print("Couldn't make server request. Make sure a connection has been established.")
        print(f"Error: {str(e)}")
        return
    try:
        # Wait for server ok, then make sure file exists
        s.recv(BUFFER_SIZE)
        # Send file name length, then name
        file_name_size = struct.pack("h", len(file_name.encode()))
        s.send(file_name_size)
        s.send(file_name.encode())
        # Get file size (if exists)
        file_size = struct.unpack("i", s.recv(4))[0]
        if file_size == -1:
            # If file size is -1, the file does not exist
            print("File does not exist. Make sure the name was entered correctly.")
            return
    except Exception as e:
        print("Error checking file")
        print(f"Error: {str(e)}")
        return
    try:
        # Send ok to receive file content
        s.sendall(b"1")
        # Enter loop to receive file
        with open(file_name, "wb") as output_file:
            bytes_received = 0
            print("\nDownloading...")
            while bytes_received < file_size:
                # Again, file broken into chunks defined by the BUFFER_SIZE variable
                chunk = s.recv(BUFFER_SIZE)
                output_file.write(chunk)
                bytes_received += len(chunk)
        print("Successfully downloaded {}".format(file_name))
        # Tell the server that the client is ready to receive the download performance details
        s.sendall(b"1")
        # Get performance details
        time_elapsed = struct.unpack("f", s.recv(4))[0]
        print("Time elapsed: {}s\nFile size: {}b".format(time_elapsed, file_size))
    except Exception as e:
        print("Error downloading file")
        print(f"Error: {str(e)}")
        return

def delf(file_name):
    # Delete specified file from the file server
    print("Deleting file: {}...".format(file_name))
    try:
        # Send request, then wait for go-ahead
        s.sendall(b"DELF")
        s.recv(BUFFER_SIZE)
    except Exception as e:
        print("Couldn't connect to server. Make sure a connection has been established.")
        print(f"Error: {str(e)}")
        return
    try:
        # Send file name length, then file name
        file_name_size = struct.pack("h", len(file_name.encode()))
        s.send(file_name_size)
        s.send(file_name.encode())
    except Exception as e:
        print("Couldn't send file details")
        print(f"Error: {str(e)}")
        return
    try:
        # Get confirmation that file does/doesn't exist
        file_exists = struct.unpack("i", s.recv(4))[0]
        if file_exists == -1:
            print("The file does not exist on the server")
            return
    except Exception as e:
        print("Couldn't determine file existence")
        print(f"Error: {str(e)}")
        return
    try:
        # Confirm user wants to delete the file
        confirm_delete = input("Are you sure you want to delete {}? (Y/N)\n".format(file_name)).upper()
        # Make sure input is valid
        # Unfortunately, Python doesn't have a do-while style loop, as that would have been better here
        while confirm_delete != "Y" and confirm_delete != "N" and confirm_delete != "YES" and confirm_delete != "NO":
            # If user input is invalid
            print("Command not recognized, try again")
            confirm_delete = input("Are you sure you want to delete {}? (Y/N)\n".format(file_name)).upper()
    except Exception as e:
        print("Couldn't confirm deletion status")
        print(f"Error: {str(e)}")
        return
    try:
        # Send confirmation
        if confirm_delete == "Y" or confirm_delete == "YES":
            # User wants to delete the file
            s.sendall(b"Y")
            # Wait for confirmation the file has been deleted
            delete_status = struct.unpack("i", s.recv(4))[0]
            if delete_status == 1:
                print("File successfully deleted")
                return
            else:
                # Client will probably send -1 to get here, but an else is used as more of a catch-all
                print("File failed to delete")
                return
        else:
            s.sendall(b"N")
            print("Delete abandoned by user!")
            return
    except Exception as e:
        print("Couldn't delete file")
        print(f"Error: {str(e)}")
        return

def quit_ftp():
    s.sendall(b"QUIT")
    # Wait for server go-ahead
    s.recv(BUFFER_SIZE)
    s.close()
    print("Server connection ended")
    return

print("\n\nWelcome to the FTP client.\n\nCall one of the following functions:\nCONN           : Connect to the server\nUPLD file_path : Upload a file\nLIST           : List files\nDWLD file_path : Download a file\nDELF file_path : Delete a file\nQUIT           : Exit")

while True:
    # Listen for a command
    prompt = input("\nEnter a command: ")
    if prompt[:4].upper() == "CONN":
        conn()
    elif prompt[:4].upper() == "UPLD":
        upld(prompt[5:])
    elif prompt[:4].upper() == "LIST":
        list_files()
    elif prompt[:4].upper() == "DWLD":
        dwld(prompt[5:])
    elif prompt[:4].upper() == "DELF":
        delf(prompt[5:])
    elif prompt[:4].upper() == "QUIT":
        quit_ftp()
        break
    else:
        print("Command not recognized; please try again")