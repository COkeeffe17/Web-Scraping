import requests
from bs4 import BeautifulSoup
import os
from difflib import get_close_matches


def get_soup(url):
    # Making a GET request
    r = requests.get(url)

    # Parsing the HTML
    soup = BeautifulSoup(r.content, 'html.parser')

    return soup


def print_table(headers, data):
    # Just prints everything very nicely
    print("-" * 106)
    print("|", headers[0] + (" " * (20 - len(headers[0]))) + "|", headers[1] + (" " * (20 - len(headers[0]))) + "|", 
            headers[2] + (" " * (20 - len(headers[0]))) + "|", headers[3] + (" " * (20 - len(headers[3]))) + "|")
    print("-" * 106)

    for info in data:
        print("|", info[0] + (" " * (20 - len(info[0]))) + "|", info[1] + (" " * (29 - len(info[1]))) + "|", 
            info[2] + (" " * (28 - len(info[2]))) + "|", info[3] + (" " * (20 - len(info[3]))) + "|")
        print("-" * 106)


def fuzzy_search(items, search_term, threshold=0.6, limit=3):
    """
    Fuzzy search through product names
    :param items: List of (name, price, rating) tuples
    :param search_term: User's search input
    :param threshold: Similarity threshold (0-1)
    :param limit: Max number of results to return
    :return: List of matching items
    """

    to_return = []

    for category in items:
    
        # Find closest matches using fuzzy matching
        matches = get_close_matches(
            search_term.lower(),
            [item.lower() for item in category],
            n=limit,
            cutoff=threshold
        )

        to_return += matches
    
    # Return full product info for matches
    return [item for item in items if ((item[0].lower() in to_return) or (item[1].lower() in to_return) 
                                       or (item[2].lower() in to_return) or (item[3].lower() in to_return))]


def enhanced_search(items, search_term):
    """Search with multiple matching techniques"""
    
    # 1. Exact match (case insensitive)
    exact_matches = [
        item for item in items 
        if any(search_term.lower() == str(field).lower() for field in item)
    ]

    # 2. Partial matches    
    partial_matches = [
        item for item in items
        if any(search_term in str(section).lower() 
               for section in item)
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


def search(headers, to_search, top_headers):
    os.system('cls')

    search_term = input("What would you like to search for?   ")

    print("")

    # Searching time
    matches = enhanced_search(to_search, search_term)

    # If matches were found
    if matches:
        # If those stupid extra headers are here
        if top_headers:
            print("-" * 106)
            print("|", top_headers[0] + (" " * 20) + "|", top_headers[1] + (" " * (59 - len(top_headers[1]))) + "|", top_headers[2] + (" " * (20 - len(top_headers[2]))) + "|")
        print_table(headers, matches)

    # If not
    else:
        print("Sorry, no matches found.")

    continyu = input("\n\nEnter any key to continue...")


def first_two(url):
    os.system('cls')

    soup = get_soup(url)

    # Find the tables
    tables = soup.find_all('table')

    all_headers = []
    all_info = []

    for table in tables:
        # Headers
        headers = table.find_all('th')
        headers = [header.text for header in headers]

        all_headers += headers

        # Rows
        rows = table.find_all('tr')
        
        info_list = []

        for row in rows:
            # Extracting and cleaning the data
            data = row.find_all('td')
            info_list.append([item.text for item in data])

        info_list = info_list[1:]

        all_info += info_list

    # Output the information
    print_table(all_headers, all_info)

    print("\n\n")

    continyu = input("What would you like to do now? Enter 's' to search for an item, or anything else to continue.   ")

    if continyu.lower() == "s":
        search(all_headers, all_info, [])


def multiple_headers(url):
    os.system('cls')

    soup = get_soup(url)

    # Find the tables
    rows = soup.find_all('tr')

    # Weird extra headers
    top_headers = rows[0].find_all('th')
    top_headers = [header.text for header in top_headers]

    # Headers
    headers = [header.text for header in rows[1].find_all('th')]

    # Data/fields
    data = []
    for row in rows[2:]:
        data.append([item.text for item in row.find_all()])

    # Output information
    print("-" * 106)
    print("|", top_headers[0] + (" " * 20) + "|", top_headers[1] + (" " * (59 - len(top_headers[1]))) + "|", top_headers[2] + (" " * (20 - len(top_headers[2]))) + "|")
    print_table(headers, data)
    

    continyu = input("\n\nWhat would you like to do now? Enter 's' to search for an item, or anything else to continue.   ")

    if continyu.lower() == "s":
        search(headers, data, top_headers)


def main_menu():
    over = False

    functions = {
        "1": first_two,
        "2": first_two,
        "3": multiple_headers,
        "4": None
    }

    urls = ["https://webscraper.io/test-sites/tables/tables-semantically-correct",
            "https://webscraper.io/test-sites/tables/tables-without-thead",
            "https://webscraper.io/test-sites/tables/tables-multiple-header-rows"]

    while not over:
        os.system('cls')
        print("Welcome to the table web scraper!\n")
        print("1. Semantically correct tables")
        print("2. Tables without the thead tag")
        print("3. Tables with multiple header rows")
        print("4. Quit\n")

        choice = "a"

        # Loops until the user enters a valid number
        while not (choice in functions):
            choice = input("What would you like to do?   ")

        if choice != "4":
            functions[choice](urls[int(choice)-1])

        else:
            over = True


if __name__ == "__main__":
    main_menu()
