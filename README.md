# Web-Scraping
This is a project in which I will be learning/implementing web-scraping.

# Where?

I am testing this using a website called https://webscraper.io/test-sites. I believe this website exists to test a separate web scraper — the one the site is actually advertising/selling — but I thought it was perfect for testing my own scraper. It features various levels of difficulty by adding more and more layers of complexity in order to scrape the necessary data (shown below).

<img width="1031" alt="WSS1" src="https://github.com/user-attachments/assets/29b0ab31-69b3-4b85-95d7-bbf2383f0aa7" />
<img width="1033" alt="WSS2" src="https://github.com/user-attachments/assets/e7fa7482-8a00-4a95-b4c9-395ff5879eeb" />
<img width="1032" alt="WSS3" src="https://github.com/user-attachments/assets/f2f28a52-2f0b-4ea2-baa0-603697ce923e" />

# What am I doing?

Version 1.0 is designed for the "E-commerce site" and is very basic — just the foundation that later versions will build on. It has a few features to make it relatively user-friendly, including:

Returning all laptops/tablets/phones

Sorting each list by name (alphabetically), price, or rating

Searching for specific items

Returning detailed information for any searched item

The biggest issue I had in this version was handling the storage and colour buttons. It was nearly impossible to get the value of those buttons using only BeautifulSoup, since only one was pressed by default. So, I had to bring in Chrome WebDriver (more info here: ChromeDriver Docs). This allowed me to simulate the clicking of each button to retrieve its data, including whether or not the option was still available.

The only downside is that it made the program much slower, and if you idle in the search section for too long, terminal messages start appearing. I tried my best to resolve this, but couldn’t find a consistent way to suppress them — so I had to admit defeat on that one. Other than that, it was a very successful first version.

# Version 2.0

Version 2.0 is designed for the "E-commerce site with pagination links". This version was relatively simple to adapt. The big issue was that there are now an unknown number of pages, each with up to 6 items.

My first (and final) solution was to iterate through each page by incrementing the number at the end of the URL (e.g., https://webscraper.io/test-sites/e-commerce/static/computers/laptops?page=5). This didn’t initially work, because if the page number exceeded the actual number of pages, it wouldn’t return an error — the page title wouldn’t even change. In the end, I simply checked whether the current page contained any products; if it didn’t, the loop would stop. Worked like a charm.

I had to do the same thing with the storage and colour option buttons, but since I’d already figured it out in the get_all_details() subroutine, it was much easier this time around. Beyond that, I made some small quality-of-life changes, like updating the main menu logic and removing unnecessary code like the kill() function. I also added more comments for future reference.

# Version 3.0

Version 3.0 was designed for the "E-commerce site with AJAX pagination links". This version was much more complicated to adapt than the last. When I actually looked at the HTML, I discovered that there was a list of information on all of the products on each laptops/tablets/phones page. I thought that the easy answer was in front of me — when I came to the soul-crushing realisation that the rating wasn't included in that list.

Undeterred, I decided to instead use WebDriver to simulate the clicking of each "page" button and get the data from each product. However, I made the doubly soul-crushing discovery that, for some unknown reason, every single rating on this site (on the homepage) displayed 5 stars for every product — when in reality, none of the products are 5 stars.

This finally forced me to do a much more complicated method of getting IDs from the information list previously mentioned and using the product URLs (example: https://webscraper.io/test-sites/e-commerce/ajax/product/124) to get the information for any product.

In the end, I only really had to change the get_details, get_all_info, search_for_items, and get_specifics subroutines, but it was just a lot of back and forth before finding the final answer. On the bright side, I came out of it with a deeper understanding of HTML escaping, JSON parsing, and scraping dynamically loaded data. Not a bad trade.

# Version 4.0

Version 4.0 was designed for the "E-commerce site with "Load more" buttons". I literally just changed every instance of "ajax" to "more". Thats it. And everything worked. After the calamity of v3.0, this was a lovely breath of fresh air.

# Version 5.0

Version 4.0 was designed for the "E-commerce site that loads items while scrolling". Similar to before, I just changed every instance of "more" (in URLs and HTML) to "scroll". I really struck gold with this structure. I have a feeling it won't work for the final version, but for now I am very satisfied.

# Version 6.0

Version 6.0 was designed for the "Table Playground". This site was completely different from the previous ones, sporting different data and a much different structure, so I completely rewrote the code.

The first two sections weren't too difficult, with the most problems coming from tweaking the sorting code (copied from the previous iterations) to check all fields, as opposed to just the first field (previously name/title).

The third section was a good bit more difficult — partially because it couldn’t use the same code as section 1 (which was a nice surprise for section 2), but also because it has an extra layer of headers, one of which spanned two columns. My final solution to this is quite rigid; it just pastes it on top of the existing table. This works for now and will continue to work until one of the fields exceeds a silly length.

While the whole code is not robust enough to handle large-scale changes in the website’s structure, for the website I was given, it works perfectly.

# Conclusion

This was an interesting little experiment, and I learned quite a bit. I of course learned how to use BeautifulSoup and requests to get data from URLs, and I am now quite efficient at it. But the biggest thing that changed was my mindset.

By this, I mean that the biggest thing I had to overcome in each section (bar v4.0 and v5.0) was finding a creative but realistic way to overcome the nuisances that had thwarted my previous method. I believe I have now improved my ability to find those solutions.
