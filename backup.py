import os
import shutil
import datetime
import time
import socket
import select

# Preset global variables
interval = 60
src_dir = r"C:\Users\hamme\Desktop\Software Enginnering 1\Idea Board Project\Backups\ideaboard_backup.json"
dest_dir = "./backup_file/"

def print_title():
    print(
        f'''
    ________________________________________________________________

                        A U T O - B A C K - U P 

                        M I C R O - S E R V I C E        
    ________________________________________________________________
    '''
    )

def backup():
    global last_backup
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    current_time = datetime.datetime.now().strftime("%Y%b%d_%H%M%S")
    dest_file_name = f'backup_{current_time}.json'
    shutil.copy2(src_dir, os.path.join(dest_dir, dest_file_name))
    print(f'Backup "{dest_file_name}" saved successfully.')
    last_backup = os.path.join(dest_dir, dest_file_name)


def main():
    print_title()

    # Initialize Socket
    server = socket.socket()
    print("Socket successfully created")
    port = 12345
    server.bind(('', port))
    print(f"Socket binded to {port}")
    server.listen(5)
    print("socket is listening... waiting for client program to start")


    client, addr = server.accept()
    print(f'Got connection from {addr} \n')

    while True:
        try:
            ready, _, _ = select.select([client], [], [], interval)

            if client in ready:
                req = client.recv(1024).decode()
                print("A REQUEST received from client")

                # check the content of the request
                if req == "Backup" or req == "backup":
                    backup()
                    client.send("Backup completed".encode())
                elif req == "Revert" or req == "revert":
                    if last_backup:
                        abs_path = os.path.abspath(last_backup)
                        client.send(abs_path.encode())
                        print("Latest back up sent to the client.")
                    else:
                        client.send("No backup found.".encode())
                elif req == "Exit" or req == "exit":
                    print("Client requested to end connection")
                    break
                else:
                    client.send(f"Invalid request command '{req}' sent.".encode())
                    print("Invalid request received")

        except ConnectionResetError:
            print("\n       ** ALERT **: Connection ended by the client, ending the program.\n")
        except ConnectionAbortedError:
            print("\n       ** ALERT **: Connection aborted by the client, ending the program.\n")
        except Exception as e:
            print("\n       ** ALERT **: Something went wrong", e)
        finally:
            server.close()


if __name__ == "__main__":
    main()
