import requests
from bs4 import BeautifulSoup
import csv
import re

# Set the base URL and search parameters

base_url = 'https://www.amazon.in'
search_query = '/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}'

# Set the headers to mimic a browser visit
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Set the number of pages to scrape
num_pages =  300
# Create a list to hold the product details
product_list = []

# Loop through each page of search results
for i in range(1, num_pages + 1):
    # Add the page number to the search parameters
    url = base_url + search_query.format(i)

    # Make a request to the website and get the response
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all the product containers on the page
    products = soup.find_all('div', {'data-component-type': 's-search-result'})

    # Loop through each product container and extract the details
    for product in products:
        # Get the product URL
        url = product.find('a', {'class': 'a-link-normal s-no-outline'})['href']
        url = 'https://www.amazon.in' + url

        # Get the product name
        name = product.find('h2', {'class': 'a-size-mini a-spacing-none a-color-base s-line-clamp-2'}).text.strip()

        # Get the product price
        price = product.find('span', {'class': 'a-price-whole'}).text.strip()

        # Get the product rating
        rating_elem = product.find('span', {'class': 'a-icon-alt'})
        rating = rating_elem.text.strip() if rating_elem else ""


        # Add the product details to the list
        product_list.append([url, name, price, rating])

# Loop through each product URL and fetch additional details
for product in product_list:
    # Make a request to the product page and get the response
    response = requests.get(product[0], headers=headers)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the ASIN
    url = product[0]
    asin = url.split("/")[-1]

    # Get the product description

    description_element_tag = soup.find("div", {"id": "feature-bullets"})
    description_element = str(description_element_tag)
    clean = re.compile('<.*?>')
    description = re.sub(clean, '', description_element)

    # Get the manufacturer
    manufacturer_elem = soup.find('a', {'id': 'bylineInfo'})
    manufacturer = manufacturer_elem.text.strip() if manufacturer_elem else ""

    reviews_elem_tag = soup.findAll('div',{'class':'a-row a-spacing-small review-data'})
    #print(reviews_elem_tag)
    reviews_elem = str(reviews_elem_tag)
    clean = re.compile('<.*?>')
    reviews = re.sub(clean, '', reviews_elem)
    #print(type(reviews))
    reviews = reviews.replace('Read more','').replace('[', '').replace(']', '').strip()


    # Update the product list with the additional details
    product.extend([reviews,description, asin, manufacturer])

# Write the product details to a CSV file
with open('products.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['URL', 'Name', 'Price', 'Rating', 'Reviews', 'Description', 'ASIN', 'Manufacturer'])
    writer.writerows(product_list)
