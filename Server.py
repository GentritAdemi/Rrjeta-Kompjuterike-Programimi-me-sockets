import socket
import os
import codecs

# 1. Vendos variablat për IP adresën dhe numrin e portit
serverName = '127.0.0.1'  # Mund të ndryshohet sipas nevojës
serverPort = 9999  # Mund të ndryshohet sipas nevojës

# 2. Dëgjo listën e anëtarëve të grupit
members = []

# 3. Krijimi i një fjalor për të ruajtur privilegjet e klientëve
privilegjet = {}

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSocket.bind((serverName, serverPort))
serverSocket.listen(10)
print(f'Serveri eshte startuar ne portin {serverPort}')

def handle_client(clientSocket):
    pranimi = clientSocket.recv(1024)
    kerkesa = pranimi.decode("utf-8")

    get = kerkesa[0:3]
    if get != 'GET':
        return

    index = int(kerkesa.index('HTTP/1.'))
    pathi = kerkesa[4:index]
    folderCheck = pathi.count('/')
    folder = ''
    file = ''

    if folderCheck > 1:
        folder = pathi[pathi.find('/'):pathi.rfind('/') + 1]
        file = pathi[pathi.rfind('/') + 1:]
    else:
        file = pathi[1:]

    # 4. Verifikimi i privilegjeve të klientit
    klienti_address = clientSocket.getpeername()[0]
    if klienti_address in privilegjet:
        privilegji = privilegjet[klienti_address]
    else:
        privilegji = "read"  # Në rast se klienti nuk ka privilegje të ndryshme, atëherë i jepet privilegji "read"

    if file.strip() == 'index.html':
        f = codecs.open(file, 'r', 'utf-8-sig')
        fajlliFizik = f.read()
        pergjigjja = (f"HTTP/1.1 200 OK\r\n"
                      f"Content-Type: text/html\r\n\r\n"
                      f"{fajlliFizik}").encode("utf-8")

    elif file.strip() == 'members.txt':
        # 5. Kontrollo për privilegjet për members.txt
        if privilegji == "full":
            # Në rast se klienti ka privilegjin "full", atëherë mund të lexojë members.txt
            members_str = "\n".join(members)
            pergjigjja = (f"HTTP/1.1 200 OK\r\n"
                          f"Content-Type: text/plain\r\n\r\n"
                          f"Anetaret e grupit:\n{members_str}").encode("utf-8")
        else:
            pergjigjja = (f"HTTP/1.1 403 Forbidden\r\n"
                          f"Content-Type: text/plain\r\n\r\n"
                          f"Ju nuk keni leje për të lexuar këtë resurs.").encode("utf-8")


    elif file.strip().startswith('execute/'):
        # 6. Kontrollo për privilegjet për ekzekutimin e komandës
        if privilegji == "full":
            # Në rast se klienti ka privilegjin "full", atëherë mund të ekzekutojë komandën
            command = file[len('execute/'):]
            try:
                output = os.popen(command).read()
                pergjigjja = (f"HTTP/1.1 200 OK\r\n"
                              f"Content-Type: text/plain\r\n\r\n"
                              f"{output}").encode("utf-8")
            except Exception as e:
                pergjigjja = (f"HTTP/1.1 500 Internal Server Error\r\n"
                              f"Content-Type: text/plain\r\n\r\n"
                              f"Gabim gjatë ekzekutimit të komandës: {str(e)}").encode("utf-8")
        else:
            pergjigjja = (f"HTTP/1.1 403 Forbidden\r\n"
                          f"Content-Type: text/plain\r\n\r\n"
                          f"Ju nuk keni leje për të ekzekutuar këtë komandë.").encode("utf-8")

    elif file.strip().startswith('access/'):
        # 7. Kontrollo për privilegjet për qasjen në foldera dhe file-t
        if privilegji == "full":
            # Në rast se klienti ka privilegjin "full", atëherë mund të qaset në foldera dhe file-t
            path = file[len('access/'):]
            try:
                with open(path, 'rb') as f:
                    file_content = f.read()
                    pergjigjja = (f"HTTP/1.1 200 OK\r\n"
                                  f"Content-Type: application/octet-stream\r\n\r\n"
                                  f"{file_content}").encode("utf-8")
            except FileNotFoundError:
                pergjigjja = (f"HTTP/1.1 404 Not Found\r\n"
                              f"Content-Type: text/html\r\n\r\n"
                              f"Ky fajll nuk ekziston").encode("utf-8")
        else:
            pergjigjja = (f"HTTP/1.1 403 Forbidden\r\n"
                          f"Content-Type: text/plain\r\n\r\n"
                          f"Ju nuk keni leje për të qasur këtë resurs.").encode("utf-8")

    elif file.strip().startswith('permissions/'):
        # 8. Kontrollo për kërkesat e ndryshimit të privilegjeve
        if privilegji == "full":
            path = file[len('permissions/'):]
            try:
                with open(path, 'r') as f:
                    permissions = f.read().strip().lower()
                    pergjigjja = (f"HTTP/1.1 200 OK\r\n"
                                  f"Content-Type: text/plain\r\n\r\n"
                                  f"Privilegjet aktuale: {permissions}").encode("utf-8")
            except FileNotFoundError:
                pergjigjja = (f"HTTP/1.1 404 Not Found\r\n"
                              f"Content-Type: text/html\r\n\r\n"
                              f"Ky fajll nuk ekziston").encode("utf-8")
        else:
            pergjigjja = (f"HTTP/1.1 403 Forbidden\r\n"
                          f"Content-Type: text/plain\r\n\r\n"
                          f"Ju nuk keni leje për të qasur këtë resurs.").encode("utf-8")

    else:
        pergjigjja = (f"HTTP/1.1 404 Not Found\r\n"
                      f"Content-Type: text/html\r\n\r\n"
                      f"Ky fajll nuk ekziston").encode("utf-8")

    clientSocket.sendall(pergjigjja)
    clientSocket.close()

while True:
    clientSocket, address = serverSocket.accept()
    members.append(address[0])  # 9. Lexo mesazhet nga klientët

    # 10. Kërko dhe ruaj privilegjet e klientit në fjalor
    kerkesa_privilegji = clientSocket.recv(1024).decode("utf-8")
    if kerkesa_privilegji.startswith("PRIVILEGE"):
        _, klienti_address, privilegji = kerkesa_privilegji.split()
        privilegjet[klienti_address] = privilegji

        # 11. Përgjigja për kërkesën e privilegjeve
        pergjigjja_privilegji = f"PRIVILEGE_GRANTED {privilegji}\r\n"
        clientSocket.sendall(pergjigjja_privilegji.encode("utf-8"))
        continue

    handle_client(clientSocket)
