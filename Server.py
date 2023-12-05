import socket
import os

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_port = 12345
server_ip = '127.0.0.2'

server_socket.bind((server_ip, server_port))

server_socket.listen(4)

print(f"Serveri është në pritje për lidhje në {server_ip}:{server_port}")

# Numri maksimal i klientëve
max_clients = 4
num_clients = 0

# Përcakto një flag për të parë nëse klienti i parë ka privilegjet për 'WRITE' dhe 'EXECUTE'
first_client = True

while True:
    # Prisni për një lidhje nga një klient
    client_socket, client_address = server_socket.accept()
    print(f"Lidhur me klientin {client_address}")

    # Nëse numri i klientëve aktive është më i vogël se 4
    if num_clients < max_clients:
        num_clients += 1  # Rrit numrin e klientëve aktive

        # Nëse është klienti i parë dhe ka privilegjet e duhura
        if first_client:
            while True:
                try:
                    # Pranojë kërkesat nga klienti
                    request = client_socket.recv(1024).decode()

                    # Përpunimi i kërkesës së klientit
                    if not request:
                        # Nëse nuk ka të dhëna, ndërprer ciklin
                        break

                    if request == 'LIST':
                        files = os.listdir('.')
                        file_list = '\n'.join(files)
                        client_socket.send(file_list.encode())
                    elif request == 'READ':
                        # Këtu mund të lexoni përmbajtjen e file-it (p.sh., index.html)
                        file_name = 'index.html'
                        try:
                            with open(file_name, 'r') as file:
                                content = file.read()
                                client_socket.send(content.encode())
                        except FileNotFoundError:
                            client_socket.send("File-i nuk ekziston.".encode())
                    elif request == 'WRITE':
                        # Pranojë përmbajtjen e re nga klienti dhe shkruajë në file
                        file_name = 'index.html'
                        data = client_socket.recv(1024).decode()
                        with open(file_name, 'w') as file:
                            file.write(data)
                        client_socket.send("File-i u shkrua me sukses.".encode())
                        # Ndrysho flagun për të ndaluar klientët e tjerë nga të drejtat për 'WRITE' dhe 'EXECUTE'
                        first_client = False
                    elif request.startswith('EXECUTE:'):
                        # Merr komandën nga kërkesa e klientit
                        command = request[len('EXECUTE:'):].strip()
                        try:
                            result = os.popen(command).read()
                            client_socket.send(result.encode())
                        except Exception as e:
                            client_socket.send(f"Gabim gjatë ekzekutimit: {str(e)}".encode())
                except ConnectionAbortedError:
                    print(f"Lidhja me klientin {client_address} është ndërprerë nga klienti.")
                    break

            # Përsërit ciklin e brendshëm pasi ka përfunduar një kërkesë nga klienti
            first_client = True
        else:
            # Refuzo kërkesat e klientëve të tjerë për 'WRITE' dhe 'EXECUTE'
            client_socket.send("Ju nuk keni privilegjet për këtë kërkesë.".encode())
    else:
        # Refuzo lidhjen nëse numri i klientëve aktive është 4
        client_socket.send("Numri maksimal i klientëve është arritur. Lidhja mbyllet.".encode())

    # Zvoglo numrin e klientëve aktive dhe mbyll lidhjen me klientin
    num_clients -= 1
    client_socket.close()
