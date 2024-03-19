# backup_client.py
import socket
import subprocess
import threading
from PyQt5.QtWidgets import QApplication


class BackupClient:
    def __init__(self, src_dir, interval=60):
        self.src_dir = src_dir
        self.interval = interval
        self.process = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_microservice(self):

        self.process = subprocess.Popen(['python', 'backup.py'], start_new_session=True)

        QApplication.processEvents()
        try:
            self.socket.connect(('localhost', 12345))
            print("Connected to the backup service.")
        except ConnectionRefusedError:
            print("Failed to connect to the backup service. Make sure it's running.")

    def send_command(self, command):
        try:
            self.socket.sendall(command.encode())
        except Exception as e:
            print(f"Failed to send command: {e}")

    def receive_response(self):
        try:
            return self.socket.recv(1024).decode()
        except Exception as e:
            print(f"Failed to receive response: {e}")
            return None

    def stop_microservice(self):
        try:
            self.send_command("Exit")
            self.socket.close()
            if self.process:
                self.process.kill()
                print("Backup service stopped.")
        except Exception as e:
            print(f"Error stopping the backup service: {e}")
