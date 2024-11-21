
import socket
import threading
import csv
import math

class CentralServer:
    def __init__(self, host='192.168.100.140', port=5008):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Central Server listening on {self.host}:{self.port}")

        self.urls = self.generatelinks()  # Generate URLs to scrape

        # Open the CSV file in write mode
        self.csv_file = open('dn.csv', 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Quote', 'Author', 'Theme'])  # Write header

    def generatelinks(self):
        url = "http://quotes.toscrape.com/"
        url_list = [url]
        for i in range(2, 11):
            url_new = url + 'page/' + str(i)
            url_list.append(url_new)
        return url_list

    def handle_client(self, client_socket, urls_subset):
        # Send a subset of URLs to the client
        for url in urls_subset:
            client_socket.send(url.encode())
            response = client_socket.recv(4096).decode()  # Receive response
            if response == "END":
                break  # If the worker sends "END", stop receiving data

            # Convert the string representation of the list back to a list
            data = eval(response)  # Be cautious with eval; ensure it's safe in your context
            self.csv_writer.writerows(data)  # Write all rows to CSV

        client_socket.send("END".encode())
        client_socket.close()

    def start(self):
        print("Waiting for connections...")
        client_count = 0

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}")

            # Distribute URLs evenly across clients
            num_clients = 5  # Assume a max of 5 clients for now
            chunk_size = math.ceil(len(self.urls) / num_clients)
            urls_subset = self.urls[client_count * chunk_size:(client_count + 1) * chunk_size]

            # Start a new thread to handle each client
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, urls_subset))
            client_handler.start()
            client_count += 1

if __name__ == "__main__":
    server = CentralServer()
    server.start()
