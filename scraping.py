# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

# Define function to initialize browser, create a data dictionary, end the webdriver and return scraped data
def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser('chrome', executable_path = '/Users/kesh/Desktop/Class/Mission-to-Mars/chromedriver', headless = True)

    # Set 2 variables news_title and news_paragraph that the function will return
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "mars_hemispheres": mars_hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Parse the HTML
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        
        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_= 'content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_= 'article_teaser_body').get_text()

    except AttributeError:
        return None, None    
    
    return news_title, news_p

# ### Featured Images
def featured_image(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time = 1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
        
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    return img_url

def mars_facts():
    
    # Add try/except for error handling
    try:
        # read the entire table using pandas
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframe        
    df.columns = ['Description', 'Mars']
    df.set_index('Description', inplace=True)
    
    # convert dataframe back into html, add bootstrap
    return df.to_html(classes = 'table table-striped')

def mars_hemispheres(browser):

    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Parse the data
    html_hemispheres = browser.html
    hemisphere_soup = soup(html_hemispheres, 'html.parser')

    # Scrape the data
    items = hemisphere_soup.find_all('div', class_='item')

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Store the main_ul 
    hemispheres_main_url = 'https://astrogeology.usgs.gov'

    for i in items: 
    
        # Store title
        title = i.find('h3').text
    
        # Store link that leads to full image website
        partial_img_url = i.find('a', class_='itemLink product-item')['href']
    
        # Visit the link that contains the full image website 
        browser.visit(hemispheres_main_url + partial_img_url)
    
        # HTML Object of individual hemisphere information website 
        partial_img_html = browser.html
    
        # Parse HTML with Beautiful Soup for every individual hemisphere information website 
        hemisphere_soup = soup(partial_img_html, 'html.parser')
    
        # Retrieve full image source 
        img_url = hemispheres_main_url + hemisphere_soup.find('img', class_='wide-image')['src']
    
        # Append the retreived information into a list of dictionaries 
        hemisphere_image_urls.append({"title" : title, "img_url" : img_url})

    return hemisphere_image_urls    

if __name__ == '__main__':

    # If running as script, print scraped data
    print(scrape_all())





