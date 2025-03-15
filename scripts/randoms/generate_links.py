import requests
from bs4 import BeautifulSoup


html_text = open("/home/hbina085/git/iex-tools/scripts/randoms/page.html","r").read()

# Parse the page content with BeautifulSoup
soup = BeautifulSoup(html_text, "html.parser")

# Select all rows within the table body identified by #hist-rows
rows = soup.select("#hist-rows > tr")


output_file = open("/home/hbina085/git/iex-tools/scripts/randoms/links.csv","w")

for i, row in enumerate(rows, start=1):
    links = row.select("td > a")
    for link in links:
        href = link.get("href")
        if href:
            filename = href[81:81+31]
            output_file.write(f"{filename},{href}\n")
