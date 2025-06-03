# Web-Scraping
This is a project in which I will be learning/implementing web-scraping.

# Where?

I am testing this using a website called webscraper.io/test-sites. I believe this website exists to test a separate web scraper — the one the site is actually advertising/selling — but I thought it was perfect for testing my own scraper. It features various levels of difficulty by adding more and more layers of complexity in order to scrape the necessary data (shown below).

<img width="1031" alt="WSS1" src="https://github.com/user-attachments/assets/29b0ab31-69b3-4b85-95d7-bbf2383f0aa7" />
<img width="1033" alt="WSS2" src="https://github.com/user-attachments/assets/e7fa7482-8a00-4a95-b4c9-395ff5879eeb" />
<img width="1032" alt="WSS3" src="https://github.com/user-attachments/assets/f2f28a52-2f0b-4ea2-baa0-603697ce923e" />

# What am I doing?

To start with, I’ve created a web scraping program with a couple of key features (nothing crazy — this is just a test). From there, I’ll adjust the program to work on the next level, gradually making it more robust and resilient in the face of awkward or inconsistent website design.

# Version 1.0

Version 1.0 is designed for the "E-commerce site" and is very basic — just the foundation that later versions will build on. It has a few features to make it relatively user-friendly, including:

- Returning all laptops/tablets/phones

- Sorting each list by name (alphabetically), price, or rating

- Searching for specific items

- Returning detailed information for any searched item

The biggest issue I had in this version was handling the storage and colour buttons. It was nearly impossible to get the value of those buttons using only BeautifulSoup, since only one was pressed by default. So, I had to bring in Chrome WebDriver (more info here: ChromeDriver Docs). This allowed me to simulate the clicking of each button to retrieve its data, including whether or not the option was still available.

The only downside is that it made the program much slower, and if you idle in the search section for too long, terminal messages start appearing. I tried my best to resolve this, but couldn’t find a consistent way to suppress them — so I had to admit defeat on that one. Other than that, it was a very successful first version.

# Version 2.0

Version 2.0 is designed for the "E-commerce site with pagination links." This version was relatively simple to adapt. The big issue was that there are now an unknown number of pages, each with up to 6 items.

My first (and final) solution was to iterate through each page by incrementing the number at the end of the URL (e.g., https://webscraper.io/test-sites/e-commerce/static/computers/laptops?page=5). This didn’t initially work, because if the page number exceeded the actual number of pages, it wouldn’t return an error — the page title wouldn’t even change. In the end, I simply checked whether the current page contained any products; if it didn’t, the loop would stop. Worked like a charm.

I had to do the same thing with the storage and colour option buttons, but since I’d already figured it out in the get_all_details() subroutine, it was much easier this time around. Beyond that, I made some small quality-of-life changes, like updating the main menu logic and removing unnecessary code like the kill() function. I also added more comments for future reference.
