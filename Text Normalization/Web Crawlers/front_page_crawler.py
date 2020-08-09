from bs4 import BeautifulSoup
import urllib.request
from selenium import webdriver
from vnexpress_crawler import Extract_Text, Extract_URLs, concat_dataframe

# Output path
out_path = "/Users/macbook/Desktop/Everything Deep Learning/FPT.AI 2020/Text Normalization/front_page.csv"

# Parse the front page
url =  'https://vnexpress.net'
chrome_path = "/Users/macbook/Desktop/Everything Deep Learning/FPT.AI 2020/Text Normalization/chromedriver"
page = urllib.request.urlopen(url)
soup = BeautifulSoup(page, 'html.parser')

extract_urls = Extract_URLs()
extract_text = Extract_Text()

# Top story
top_url = extract_urls.get_top_story_url(soup)
top_text = extract_text.get_text_from_url(top_url)
# Sub top stories
sub_urls = extract_urls.get_sub_stories_urls(soup)
sub_text = extract_text.get_text_from_url(sub_urls)
# View article
view_url = extract_urls.get_view_url(soup)
view_text = extract_text.get_text_from_view(view_url)
# Left column stories
left_urls = extract_urls.get_col_left_urls(soup)
left_text = extract_text.get_text_from_url(left_urls)
# Right column stories
right_urls = extract_urls.get_col_right_urls(url, chrome_path)
right_text = extract_text.get_text_from_url(right_urls)
# Below articles 
below_urls = extract_urls.get_below_articles_urls(url, chrome_path)
below_text = extract_text.get_text_from_url(below_urls)

# Combine crawl dictionaries
crawls = [top_text, sub_text, view_text, left_text, right_text, below_text]

# # Export crawl
final_crawl = concat_dataframe(crawls)
final_crawl.to_csv(out_path)