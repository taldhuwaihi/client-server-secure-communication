import socket
import hashlib
from cryptography.fernet import Fernet
# symmetric key generaton from server
with open('secret.key', 'rb') as key_file:
 key = key_file.read()
cipher_suite = Fernet(key)
# Socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.8.176', 24)) # parameteres: server IP , port
# Authentication
username = input("Enter username: ")
password = input("Enter password: ")
# password hashing using sha256
hashed_password = hashlib.sha256(password.encode()).hexdigest()
auth_message = f"{username}:{hashed_password}"
2
encrypted_auth_message = cipher_suite.encrypt(auth_message.encode())
client_socket.send(encrypted_auth_message)
# authentication validation
response = cipher_suite.decrypt(client_socket.recv(1024)).decode()
if response == "Authenticated":
 print("Login successful!") # ensuring secret key is same in both server and client
 while True:
 command = input("Enter command ('led 1 on', 'led 1 off', 'led 2 on', 'led 2 off', 'led 3 on', 'led
3 off', 'exit' to quit): ")
 encrypted_command = cipher_suite.encrypt(command.encode())
 client_socket.send(encrypted_command)
 if command == 'exit':
 break
else:
 print("Login failed!")
client_socket.close()