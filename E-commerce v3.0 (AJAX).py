import requests
from bs4 import BeautifulSoup
import os
from difflib import get_close_matches
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import contextlib
import sys
import html
import json


# Basically just tells chromedriver to shut up
os.environ['WDM_LOG_LEVEL'] = '0'
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ["DISPLAY"] = ":99"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress all logs from TensorFlow

# Same as above
@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr


def get_soup(url):
    # Making a GET request
    r = requests.get(url)

    # Parsing the HTML
    soup = BeautifulSoup(r.content, 'html.parser')

    return soup


def add_a_zero(price):
    if price[-2] == "." and ("." in price):
        return (price + "0")
    return price


def get_details(url):
    os.system("cls")
    print("Please wait...")

    soup = get_soup(url)

    # Just gets the data blob, unescapes it (makes it non html-friendly), and parses it into a python dictionary
    data = soup.find('div', class_='row ecomerce-items ecomerce-items-ajax').get('data-items', '')
    info_list = json.loads(html.unescape(data))

    base_url = "https://webscraper.io/test-sites/e-commerce/ajax/product/"
    final_info = []

    for info in info_list:
        product_url = base_url + str(info["id"])

        # Get all of the info
        final_info.append(get_all_info(product_url)) 

    os.system("cls")

    count = 1
    
    os.system("cls")

    # Print all items
    for item in final_info:
        print(str(count) + ".", (" " * (3 - len(str(count)))), item[0], (" " * (65 - len(item[0]))), item[1], " ", (" " * (10 - len(str(item[1])))) + ("*" * int(item[2])))
        count += 1

    # Next steps
    print("\n\nWhat would you like to do next?\n")
    print("1. Sort items by name")
    print("2. Sort items by price")
    print("3. Sort items by rating")
    print("4. Go back to main menu\n")

    choice = "a"

    # Loops until the user enters a valid number
    while not choice in ["1", "2", "3", "4"]:
        choice = input("What would you like to do?   ")

    # Calls whatever subroutine is needed
    os.system('cls')

    if not choice == "4":
        print_sorted(Merge(final_info, int(choice)-1))
    else:
        pass


def print_sorted(sorted_list):
    count = 1
    for item in sorted_list[0]:
        print(str(count) + ".", (" " * (3 - len(str(count)))), item[0], (" " * (65 - len(item[0]))), item[1], " ", (" " * (10 - len(str(item[1]))) + ("*" * int(item[2]))))
        count += 1

    smth = input("\n\nPress any key to continue...")


def safe_price(text):
    try:
        return float(text.strip().replace("$", "").replace(",", ""))
    except:
        # If something goes wrong, just call it infinite
        return float('inf')


def Insertion(sequence, place):
    for i in range(1, len(sequence)):
        count = 0
        while (i - 1 - count) >= 0:
            focus = sequence[i - count]
            left = sequence[i - 1 - count]
            
            # If going by name
            if place == 0:
                left_name = left[0].strip().lower()
                focus_name = focus[0].strip().lower()

                if left_name > focus_name:
                    sequence[i - 1 - count] = focus
                    sequence[i - count] = left
                    count += 1
                else:
                    break

            # If going by price
            elif place == 1:
                if safe_price(left[1]) > safe_price(focus[1]):
                    sequence[i - 1 - count] = focus
                    sequence[i - count] = left
                    count += 1
                else:
                    break


            # If going by rating
            elif place == 2:
                if left[2] < focus[2]:
                    sequence[i - 1 - count] = focus
                    sequence[i - count] = left
                    count += 1
                else:
                    break

    return sequence


def Merge(sequence, place):
    # Basically skips the unmerging process as this doesnt change the order of the items
    if len(sequence) > 1:
        count = 0
        done = False
        new = []
        while not done:
            # While we havent reached the end of each pass
            if count < len(sequence) - 1:
                left = sequence[count]
                right = sequence[count + 1]
                # Combining
                if type(left) != list:
                    left = [left]
                if type(right) != list:
                    right = [right]
                for item in right:
                    left.append(item)
                # Sorts two merged lists using the insertion sort as this is more efficient than the bubble sort
                new.append(Insertion(left, place))
                count += 2
            else:
                # Once we are done with a pass, we add any remaining items from 
                # odd numbered lists before recursively calling the subroutine again
                if (len(sequence) % 2) != 0:
                    new.append(sequence[len(sequence)-1])
                done = True
        # Recursive call
        sequence = Merge(new, place)
    return sequence


def get_all_info(url):
    soup = get_soup(url)

    name = soup.find('h4', itemprop = 'name').text
    price = soup.find('span', itemprop = 'price').text
    stars = soup.find_all('span', class_ = 'ws-icon ws-icon-star')

    return (name, add_a_zero(price), str(len(stars)))


def fuzzy_search(items, search_term, threshold=0.6, limit=10):
    """
    Fuzzy search through product names
    :param items: List of (name, price, rating) tuples
    :param search_term: User's search input
    :param threshold: Similarity threshold (0-1)
    :param limit: Max number of results to return
    :return: List of matching items
    """
    # Get all product names
    product_names = [item[0] for item in items]
    
    # Find closest matches using fuzzy matching
    matches = get_close_matches(
        search_term.lower(),
        [name.lower() for name in product_names],
        n=limit,
        cutoff=threshold
    )
    
    # Return full product info for matches
    return [item for item in items if item[0].lower() in matches]


def enhanced_search(items, search_term):
    """Search with multiple matching techniques"""
    
    # 1. Exact match (case insensitive)
    exact_matches = [
        item for item in items 
        if search_term in item[0].lower()
    ]
    
    # 2. Partial word matches
    partial_matches = [
        item for item in items
        if any(search_term in word.lower() 
              for word in item[0].split())
    ]
    
    # 3. Fuzzy matches
    fuzzy_matches = fuzzy_search(items, search_term)
    
    # Combine and deduplicate results
    all_matches = exact_matches + partial_matches + fuzzy_matches
    unique_matches = []
    seen = set()
    
    for item in all_matches:
        if item[0] not in seen:
            seen.add(item[0])
            unique_matches.append(item)
    
    return unique_matches


def get_specifics(item):
    os.system("cls")
    print("Please wait...")

    with suppress_stderr():
        # Starting up the chrome webdriver
        options = Options()
        options.add_argument('--log-level=1')
        options.add_argument("--headless")
        chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)

        product_found = False

        try:
            base_url = "https://webscraper.io"
            urls = [
                f"{base_url}/test-sites/e-commerce/ajax/computers/laptops",
                f"{base_url}/test-sites/e-commerce/ajax/computers/tablets",
                f"{base_url}/test-sites/e-commerce/ajax/phones/touch"
            ]

            for url in urls:
                soup = get_soup(url)

                # Just gets the data blob, unescapes it (makes it non html-friendly), and parses it into a python dictionary
                data = soup.find('div', class_='row ecomerce-items ecomerce-items-ajax').get('data-items', '')
                info_list = json.loads(html.unescape(data))

                for info in info_list:
                    # If match
                    if item[0] == info["title"]:
                        id = info["id"]
                        product_url = "https://webscraper.io/test-sites/e-commerce/ajax/product/" + str(id)

                        product_soup = get_soup(product_url)

                        description = product_soup.find('p', itemprop = 'description').text

                        reviews = product_soup.find('span', itemprop = 'reviewCount').text

                        driver.get(product_url)

                        # These next few lines basically just get the different storage options
                        option_buttons = driver.find_elements(By.CSS_SELECTOR, "button.btn.swatch")
                        storage_prices = {}

                        for btn in option_buttons:
                            storage = btn.get_attribute("value").strip()
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(1)

                            if "disabled" not in btn.get_attribute("class"):
                                price = driver.find_element(By.CLASS_NAME, "price").text.strip()
                                storage_prices[storage] = price

                        # Same as above but for colours this time
                        colours = []
                        for option in driver.find_elements(By.CSS_SELECTOR, "option.dropdown-item"):
                            if option.text != "Select color":
                                colours.append(option.text)

                        os.system("cls")

                        # Printing details
                        print("Name:  ", item[0])
                        print("\nDescription:  ", description)

                        if storage_prices:
                            print("\nAvailable HDD Options & Prices:")
                            for storage, price in storage_prices.items():
                                        print(f" • {storage} GB: {price}")
                        else:
                            print("\nStorage options not found. Base Price: ", item[1])

                        if colours:
                            print("\nAvailable colours:")
                            for colour in colours:
                                print(" • " + colour)

                        print("\nRating:  ", ("*" * int(item[2])))
                        print("\nReviews:  ", reviews, "reviews")

                        input("\n\nPress any key to continue...")
                        product_found = True
                        break

        # Gotta remember to close this
        finally:
            driver.quit()

        if not product_found:
            print(f"Product '{item[0]}' not found in any category.")
            input("\n\nPress any key to continue...")

        os.system("cls")
        print("Please wait...")


def search_for_items():
    done = False

    while not done:
        os.system("cls")
        print("Please wait...")

        urls = [
            "https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops",
            "https://webscraper.io/test-sites/e-commerce/ajax/computers/tablets",
            "https://webscraper.io/test-sites/e-commerce/ajax/phones/touch"
        ]

        # Get all item name + price pairs quickly
        fast_items = []
        id_lookup = {}

        for url in urls:
            soup = get_soup(url)

            # Just gets the data blob, unescapes it (makes it non html-friendly), and parses it into a python dictionary
            data = soup.find('div', class_='row ecomerce-items ecomerce-items-ajax').get('data-items', '')
            info_list = json.loads(html.unescape(data))

            for info in info_list:
                name = info["title"]
                price = f"${info['price']:.2f}"
                fast_items.append((name, price))

                # For the url later
                id_ = info["id"]       
                id_lookup[name] = id_

        os.system("cls")
        search_term = input("What would you like to search for?    ")
        os.system('cls')
        print("Please wait...")

        # Do fast search first, as it only needs the name
        fast_results = enhanced_search([(name, price, "?") for name, price in fast_items], search_term)

        if not fast_results:
            print("\nSorry, no items found.\n")
            input("\nPress any key to continue...")
            return

        # Now get actual ratings for matching results only
        output = []
        for name, price, _ in fast_results:
            # Gets the id from the id_lookup dictionary
            product_url = f"https://webscraper.io/test-sites/e-commerce/ajax/product/{id_lookup[name]}"
            name, price, rating = get_all_info(product_url)
            output.append((name, price, rating))

        # Display results
        count = 1
        for item in output:
            print(str(count) + ".", (" " * (2-len(str(count)))), item[0], (" " * (65 - len(str(count)) - len(item[0]))), item[1], (" " * (10 - len(str(item[1])))) + ("*" * int(item[2])))
            count += 1

        continyu = input("""\nPress s to search again, enter the number of the item you wish to learn more about, 
or anything else to continue.   """)

        if continyu.isnumeric():
            if int(continyu) <= len(output):
                get_specifics(output[int(continyu) - 1])
                done = True
        elif continyu.lower() != "s":
            done = True


def main_menu():
    over = False

    urls = ["https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops?page=1", 
            "https://webscraper.io/test-sites/e-commerce/ajax/computers/tablets?page=1", 
            "https://webscraper.io/test-sites/e-commerce/ajax/phones/touch?page=1"]

    # Loop for use
    while not over:
        os.system("cls")

        print("Welcome to the unnamed E-commerce site web scraping tool!\n")
        print("1. Get all laptops")
        print("2. Get all tablets")
        print("3. Get all phones")
        print("4. Search for items")
        print("5. Quit\n")

        choice = "a"

        # Loops until the user enters a valid number
        while not (choice in ["1", "2", "3", "4", "5"]):
            choice = input("What would you like to do?   ")

        # Calls whatever subroutine is needed
        if int(choice) <= 3:
            get_details(urls[int(choice)-1])
        elif choice == "4":
            search_for_items()
        else:
            over = True


if __name__ == "__main__":
    main_menu()
