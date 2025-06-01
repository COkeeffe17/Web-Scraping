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


def get_names(soup):
    products = soup.find_all('a', class_ = 'title') 

    # Lists all products and their prices
    full_names = []
    for product in products:
        full_name = product.get('title', product.text).strip()
        full_names.append(full_name)

    return full_names


def get_prices(soup):
    return [price.text for price in soup.find_all('span', itemprop="price")]


def get_ratings(soup):
    # Find all rating divs
    rating_divs = soup.find_all('div', class_='ratings')  
    ratings = []

    for rating_div in rating_divs:
        # Find the <p> tag with the 'data-rating' attribute
        rating_p = rating_div.find('p', attrs={"data-rating": True})
        
        # Check if the rating exists
        if rating_p:  
            # Get the 'data-rating' value
            ratings.append(rating_p['data-rating'])

    return ratings


def get_details(soup):
    os.system("cls")
    
    info_list = get_all_info(soup)

    count = 1

    # Print all items
    for item in info_list:
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

    products = soup.find_all('div', class_='thumbnail')  # Each product is a "block"
    items = []
    # Get all details, making sure that all sections are present
    for product in products:
        try:
            name = product.find('a', class_='title').get('title', product.text).strip()
            price = product.find('span', itemprop="price").text.strip()
            rating = product.find('p', {'data-rating': True})['data-rating']
            items.append((name, price, rating))

        except:
            pass # Just means an item came in missing some data, this shouldn happen bu just in case it is safest to eliminate it.


    if not choice == "4":
        print_sorted(Merge(items, int(choice)-1))
    else:
        pass


def print_sorted(sorted_list):
    count = 1
    for item in sorted_list[0]:
        print(str(count) + ".", (" " * (3 - len(str(count)))), item[0], (" " * (65 - len(item[0]))), item[1], " ", (" " * (10 - len(str(item[1]))) + ("*" * int(item[2]))))
        count += 1

    smth = input("\n\nPress any key to continue...")


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
                if float(left[1][1:]) > float(focus[1][1:]) and (i - 1 - count) >= 0:
                    storage = left
                    sequence[i - 1 - count] = focus
                    sequence[i - count] = storage
                else:
                    count += 1

            # If going by rating
            elif place == 2:
                if left[2] < focus[2] and (i - 1 - count) >= 0:
                    storage = left
                    sequence[i - 1 - count] = focus
                    sequence[i - count] = storage
                else:
                    count += 1
    return sequence


def Merge(sequence, place):
    # Basically skips the unmerging process as this doesnt change the order of the items
    if len(sequence) > 1:
        count = 0
        done = False
        new = []
        while not done:
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
                if (len(sequence) % 2) != 0:
                    new.append(sequence[len(sequence)-1])
                done = True
        # Recursive call
        sequence = Merge(new, place)
    return sequence


def kill():
    return True


def get_all_info(soup):
    items = []

    names, prices, ratings = list(get_names(soup)), list(get_prices(soup)), list(get_ratings(soup))
    for i in range(0, len(names)):
        items.append((names[i], prices[i], ratings[i]))

    return items


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

        # Set up headless Chrome driver (can remove headless if you want to see it)
        options = Options()
        options.add_argument('--log-level=1')
        options.add_argument("--headless")  # REMOVE this line to see the browser
        chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        

        base_url = "https://webscraper.io"

        # Original list of category URLs
        urls = [
            f"{base_url}/test-sites/e-commerce/allinone/computers/laptops",
            f"{base_url}/test-sites/e-commerce/allinone/computers/tablets",
            f"{base_url}/test-sites/e-commerce/allinone/phones/touch"
        ]

        for url in urls:
            soup = get_soup(url)
            products = soup.find_all('div', class_='thumbnail')

            for product in products:
                name = product.find('a', class_='title').get('title', '').strip()

                if item[0].lower() == name.lower():
                    try:
                        # Get product page URL
                        product_path = product.find('a', class_='title')['href']
                        full_url = base_url + product_path

                        # Open the product page in Selenium browser
                        driver.get(full_url)
                        wait = WebDriverWait(driver, 10)

                        # Grab description and reviews using Selenium
                        description = driver.find_element(By.CLASS_NAME, "description").text.strip()
                        reviews = driver.find_element(By.CSS_SELECTOR, 'span[itemprop="reviewCount"]').text

                        # Loop through each storage button and grab the updated price
                        option_buttons = driver.find_elements(By.CSS_SELECTOR, "button.btn.swatch")
                        storage_prices = {}

                        for btn in option_buttons:
                            storage = btn.get_attribute("value").strip()

                            # Click the button to trigger JS update
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(1)  # Wait for price to update
                            
                            # Gets the actual class of the button
                            btn_class = btn.get_attribute("class")
                            
                            # Is the storage option available?
                            if btn_class != "btn swatch disabled active btn-primary":
                                #  Extract price after click
                                price = driver.find_element(By.CLASS_NAME, "price").text.strip()
                                storage_prices[storage] = price

                            else:
                                option_buttons.remove(btn)

                        # Colours                       
                        colour_options = driver.find_elements(By.CSS_SELECTOR, "option.dropdown-item")
                        colours = []
                        for option in colour_options:
                            if option.text != "Select color":
                                colours.append(option.text)

                        driver.quit()  # Close Selenium browser

                        os.system("cls")
                        print("Name:  ", name)
                        print("\nDescription:  ", description)

                        # Display storage-price pairs if found
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

                        return

                    except Exception as e:
                        print(f"⚠️ Error while fetching product details: {e}")
                        continue

        driver.quit()  # Always close browser at the end
        print(f"Product '{item[0]}' not found in any category")
        input("\n\nPress any key to continue...")
        os.system("cls")
        print("Please wait...")


def search_for_items():
    done = False

    while not done:
        os.system("cls")

        # Getting laptop information
        laptops = get_all_info(get_soup("https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"))

        # Getting tablet information
        tablets = get_all_info(get_soup("https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets"))

        # Getting phone information
        phones = get_all_info(get_soup("https://webscraper.io/test-sites/e-commerce/allinone/phones/touch"))

        item_list = laptops + tablets + phones

        search_term = input("What would you like to search for?    ")

        output = enhanced_search(item_list, search_term)
        print("\n")

        if len(output) == 0:
            print("Sorry, no items found.\n")

        else:
            count = 1
            for item in output:
                # Output all items
                print(str(count) + ".", (" " * (2-len(str(count)))), item[0], (" " * (65 - len(str(count)) - len(item[0]))), item[1], (" " * (10 - len(str(item[1])))) + ("*" * int(item[2])))
                count += 1

        continyu = input("""\nPress s to search again, enter the number of the item you wish to learn more about, 
or anything else to continue.   """)

        if continyu.isnumeric():
            if int(continyu) <= len(output):
                get_specifics(output[int(continyu)-1])
                done = True

        elif continyu.lower() != "s":
            done = True


def main_menu():
    over = False

    # What input means what subroutine
    subroutines = {
        "1": "nothing",
        "2": "placeholder",
        "3": "empty",
        "4": search_for_items,
        "5": kill
    }

    urls = ["https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops", "https://webscraper.io/test-sites/e-commerce/allinone/computers/tablets", "https://webscraper.io/test-sites/e-commerce/allinone/phones/touch", "", ""]

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
        while not (choice in subroutines):
            choice = input("What would you like to do?   ")

        # Calls whatever subroutine is needed
        if int(choice) <= 3:
            over = get_details(get_soup(urls[int(choice)-1]))
        else:
            over = subroutines[choice]()


if __name__ == "__main__":
    main_menu()
