import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_port = 12345
server_ip = '127.0.0.2'

client_socket.connect((server_ip, server_port))
print(f"Lidhur me serverin {server_ip}:{server_port}")

action = input("Zgjedhni veprimin (READ, WRITE, EXECUTE): ").upper()

# Dërgo kërkesën tek serveri
client_socket.send(action.encode())

# Për kërkesën 'WRITE', kërko përdoruesin të shkruajë përmbajtjen
if action == 'WRITE':
    content = input("Shkruaj përmbajtjen për file-in: ")
    client_socket.send(content.encode())

# Pranojë përgjigjen nga serveri
response = client_socket.recv(1024).decode()
print(f"Përgjigja nga serveri: {response}")

# Kontrollo nese përdoruesi dëshiron të vazhdojë
pergjigja_e_përdoruesit = input("Dëshironi të vazhdoni (po/jo)? ").lower()
if pergjigja_e_përdoruesit != 'po' :
    client_socket.close()

# Mbyll lidhjen me serverin

