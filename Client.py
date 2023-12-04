import socket

# Adresa dhe porti i serverit
server_address = '127.0.0.1'  # Ndryshoni këtë sipas nevojës
server_port = 9999  # Ndryshoni këtë sipas nevojës

# Krijimi i soketit të klientit
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Lidhja me serverin
try:
    client_socket.connect((server_address, server_port))
    print(f'Lidhja me serverin {server_address}:{server_port} u krye me sukses.')
except Exception as e:
    print(f'Gabim gjatë lidhjes me serverin: {str(e)}')
    exit()

# Definimi i funksionit për dërgimin e kerkesave dhe marrjen e përgjigjeve
def dergo_kerkesen(kerkesa):
    try:
        client_socket.sendall(kerkesa.encode("utf-8"))
        pergjigja = client_socket.recv(4096).decode("utf-8")
        return pergjigja
    except Exception as e:
        print(f'Gabim gjatë dërgimit të kerkesës: {str(e)}')
        return None

# Lidhja e një pajisjeje me privilegji të plotë
kerkesa_privilegje_te_plote = "PRIVILEGE FULL_ACCESS_DEVICE\r\n"
pergjigja_privilegje_te_plote = dergo_kerkesen(kerkesa_privilegje_te_plote)
print("Përgjigja për PRIVILEGE FULL_ACCESS_DEVICE:\n", pergjigja_privilegje_te_plote)

# Lidhja e një pajisjeje me read() permission
kerkesa_privilegje_read = "PRIVILEGE READ_ONLY_DEVICE\r\n"
pergjigja_privilegje_read = dergo_kerkesen(kerkesa_privilegje_read)
print("\nPërgjigja për PRIVILEGE READ_ONLY_DEVICE:\n", pergjigja_privilegje_read)

# Dërgimi i një mesazhi tek serveri
mesazhi = "SEND_MESSAGE Hello from the client!\r\n"
pergjigja_mesazhi = dergo_kerkesen(mesazhi)
print("\nPërgjigja për SEND_MESSAGE:\n", pergjigja_mesazhi)

# Qasja në folderat/përmbajtjen në server (p.sh., leximi i një file)
kerkesa_lexo_file = "READ /index.html\r\n"
pergjigja_lexo_file = dergo_kerkesen(kerkesa_lexo_file)
print("\nPërgjigja për READ /index.html:\n", pergjigja_lexo_file)

# Mbyllja e lidhjes me serverin
client_socket.close()
