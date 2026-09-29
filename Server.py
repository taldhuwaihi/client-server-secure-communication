import socket
import hashlib
from cryptography.fernet import Fernet
import RPi.GPIO as GPIO
# using GPIO to set up LEDs (GREEN, BLUE, RED)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT) # LED 1 (GREEN)
GPIO.setup(23, GPIO.OUT) # LED 2 (BLUE)
GPIO.setup(24, GPIO.OUT) # LED 3 (RED)
# Key generation (AES)
key = Fernet.generate_key()
cipher_suite = Fernet(key)
3
# Client side key file
with open('secret.key', 'wb') as key_file:
 key_file.write(key)
# Hashed password (SHA-256)
user_passwords = {
 "mounib": hashlib.sha256("khanafer".encode()).hexdigest()
}
# Socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 24))
server_socket.listen(1)
print("Server listening...")
client, addr = server_socket.accept()
print("Client connected:", addr)
# Authentication
data = client.recv(1024) # encrypted message
decrypted_message = cipher_suite.decrypt(data).decode()
username, received_hash = decrypted_message.split(':')
# Authentication validation
if username in user_passwords and user_passwords[username] == received_hash:
 client.send(cipher_suite.encrypt("Authenticated".encode()))
 print("Login successful. Waiting for commands.") # ensuring secret key is same in both
server and client
 while True:
 command = cipher_suite.decrypt(client.recv(1024)).decode()
 if command == "led 1 on": # Turning on led 1 (GREEN)
 GPIO.output(18, GPIO.HIGH)
 print("LED 1 turned ON")
 elif command == "led 1 off": # Turning off led 1 (GREEN)
 GPIO.output(18, GPIO.LOW)
 print("LED 1 turned OFF")
 elif command == "led 2 on": # Turning on led 2 (BLUE)
 GPIO.output(23, GPIO.HIGH)
 print("LED 2 turned ON")
 elif command == "led 2 off": # Turning off led 2 (BLUE)
 GPIO.output(23, GPIO.LOW)
 print("LED 2 turned OFF")
4
 elif command == "led 3 on": # Turning on led 3 (RED)
 GPIO.output(24, GPIO.HIGH)
 print("LED 3 turned ON")
 elif command == "led 3 off": # Turning off led 3 (RED)
 GPIO.output(24, GPIO.LOW)
 print("LED 3 turned OFF")
 elif command == "exit":
 break
else:
 client.send(cipher_suite.encrypt("Authentication Failed".encode()))
 print("Login failed!")
client.close()
server_socket.close()
GPIO.cleanup()