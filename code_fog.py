import socket
import requests
from bs4 import BeautifulSoup

def parse(url_new):
    print(f"Scraping data from link: {url_new}")
    r = requests.get(url_new)
    soup = BeautifulSoup(r.content, 'html.parser')

    quotes = []
    authors = []
    themes = []

    # Storing the Quotes
    quotes_list = soup.find_all('span', attrs={'class': 'text'})
    for each_quote in quotes_list:
        quotes.append(each_quote.string)

    # Storing the authors of the quotes
    authors_list = soup.find_all('small', attrs={'class': 'author'})
    for each_author in authors_list:
        authors.append(each_author.string)

    titles_list = soup.find_all("meta", class_="keywords")
    for title in titles_list:
        themes.append(title["content"])

    # Prepare the data for sending back to the server
    data = []
    for i in range(len(quotes)):
        data.append([quotes[i], authors[i], themes[i]])
    
    return data

def run():
    server_ip = input("Enter the server IP address: ")
    server_port = 5100


    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    empty_count = 0
    empty_limit = 2  # Stop after receiving 2 consecutive empty URLs

    while True:
        url = client_socket.recv(1024).decode()  # Receive URL
        if url == "END":
            break  # End of task
        if not url.strip():  # Check if the URL is empty or only contains whitespace
            print("Received an empty URL, skipping...")
            empty_count += 1
            if empty_count >= empty_limit:
                print("Too many empty URLs received, stopping the loop.")
                client_socket.send("END".encode())  # Notify server of completion
                break
            continue
        else:
            empty_count = 0  # Reset the counter when a valid URL is received

        data = parse(url)  # Get scraped data
        client_socket.send(str(data).encode())  # Send data to server

    client_socket.close()

if __name__ == "__main__":
    run()