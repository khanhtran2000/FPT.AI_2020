from bs4 import BeautifulSoup
import urllib.request
from vnexpress_crawler import Extract_Text, Extract_URLs, concat_dataframe

out_path = "/Users/macbook/Desktop/Everything Deep Learning/FPT.AI 2020/Text Normalization/raw_text/thegioi_p2to12.csv"

category_url = "https://vnexpress.net/the-gioi-p"
extract_urls = Extract_URLs()
extract_text = Extract_Text()

urls = []
for i in range(2,12):
    page = urllib.request.urlopen(category_url+str(i))
    soup = BeautifulSoup(page, 'html.parser')

    for url in extract_urls.get_category_page_urls(soup):
        urls.append(url)

crawl = extract_text.get_text_from_url(urls)

final_crawl = concat_dataframe([crawl])
final_crawl.to_csv(out_path)