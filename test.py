import time

import requests


def getURL(url):
    try:
        print(f"Fetching data from {url}")
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        with open('response.json', 'w') as file:
            file.write(response.text)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def sendAllReceipts(urls):
    host = "http://127.0.0.1:5000/api/fetchReceipt"
    for url in urls:
        headers = {"Content-Type": "application/json"}
        res = requests.post(
            headers=headers,
            url=host,
            json={
                "url": url
            }

        )
        if res.status_code == 200:
            print(f"Successfully sent receipt for {url}")
            time.sleep(1)

        else:
            print(f"Failed to send receipt for {url}: {res.status_code}, {res.text}")
            time.sleep(1)


# url = 'https://osher.pairzon.com/v1.0/documents/fe4f9bcf-050e-48f5-af2b-bb5a7b81f001?p=1247'

# res = getURL(url)
# if res:
#     print(f"Data fetched successfully.\n {res}")


if __name__ == "__main__":
    urls = ["https://osher.pairzon.com/1247/7JSqNKZ3oh6ElhadNvz8c1",
            "https://osher.pairzon.com/1247/EwixCSvwvyTs77wXbJgb2",
            "https://osher.pairzon.com/1247/3FHOeMrlydVwpnMNvFzYXa",
            "https://osher.pairzon.com/1247/n8eR2xy3oU2Ud5cWbxy75]"]

    sendAllReceipts(urls)
