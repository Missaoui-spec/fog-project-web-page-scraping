
import socket
import requests
from bs4 import BeautifulSoup
import threading

def parse(url_new):
    print(f"Scraping data from link: {url_new}")
    r = requests.get(url_new)
    soup = BeautifulSoup(r.content, 'html.parser')

    quotes = []
    authors = []
    themes = []

    quotes_list = soup.find_all('span', attrs={'class': 'text'})
    for each_quote in quotes_list:
        quotes.append(each_quote.string)

    authors_list = soup.find_all('small', attrs={'class': 'author'})
    for each_author in authors_list:
        authors.append(each_author.string)

    titles_list = soup.find_all("meta", class_="keywords")
    for title in titles_list:
        themes.append(title["content"])

    data = []
    for i in range(len(quotes)):
        data.append([quotes[i], authors[i], themes[i]])
    
    return data

def handle_url(client_socket, url):
    if not url.strip():  
        print("Received an empty URL, skipping...")
        return

    data = parse(url)
    client_socket.send(str(data).encode())

def run():
    server_ip = input("Enter the server IP address: ")
    server_port = 5008

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    threads = []
    while True:
        url = client_socket.recv(1024).decode()  
        if url == "END":
            break  

        # Create a new thread to handle the scraping of each URL
        thread = threading.Thread(target=handle_url, args=(client_socket, url))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    client_socket.close()

if __name__ == "__main__":
    run()
