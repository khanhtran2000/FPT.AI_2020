# -*- coding: utf-8 -*-
from selenium import webdriver
import re
import pandas as pd
import numpy as np


def drop_duplicates(x):
    """Drop duplicates from a list"""
    return list(dict.fromkeys(x))


def concat_dataframe(crawl_list):
    """Merge a list of dictionaries with same keys into a dataframe"""
    crawl_dfs = [pd.DataFrame(crawl) for crawl in crawl_list]
    final_crawl = pd.concat(crawl_dfs, axis=0)
    final_crawl.reset_index(inplace=True, drop=True)
    return final_crawl


class Extract_URLs:
    def __init__(self):
        self.top_story_url = []
        self.sub_stories_urls = []
        self.view_url = []
        self.col_left_urls = []
        self.col_right_urls = []
        self.below_urls = []
        self.category_urls = []

    def get_top_story_url(self, soup):
        """Extract the website url of the top story"""
        top_html = soup.find("section", class_="section section_topstory")
        top_story_html = top_html.find("article", class_="item-news full-thumb article-topstory").find_all("a")
        top_story_url = drop_duplicates([news.get("href") for news in top_story_html if news.get("title") is not None])
        self.top_story_url = top_story_url
        return top_story_url

    def get_sub_stories_urls(self, soup):
        """Extract the website urls of the sub top stories"""
        sub_stories_html = soup.find("div", class_="sub-news-top").find_all("h3", class_="title_news")
        sub_html = [sub_story_html.find("a") for sub_story_html in sub_stories_html]
        sub_stories_urls = drop_duplicates([news.get("href") for news in sub_html if news.get("title") is not None])
        self.sub_stories_urls = sub_stories_urls
        return sub_stories_urls

    def get_view_url(self, soup):
        """Extract the website url of the view article"""
        sub_top_html = soup.find("div", class_="sub-news-top")
        view_html = sub_top_html.find("h3", class_="title-news").find("a")
        view_url = view_html.get("href")
        self.view_url = view_url
        return view_url

    def get_col_left_urls(self, soup):
        """Extract the website urls of the below articles in left column"""
        col_left = soup.find("div", class_="col-left col-small")
        col_left_html = col_left.find_all("article", class_="item-news item-news-common")

        col_left_title_news = []
        for article in col_left_html:
            col_left_title_news.append(article.find("h3", class_="title-news"))

        left_articles_html = [article.find("a") for article in col_left_title_news]
        col_left_urls = drop_duplicates([news.get("href") for news in left_articles_html if news.get("title") is not None])
        self.col_left_urls = col_left_urls
        return col_left_urls

    def get_col_right_urls(self, url, chrome_path):
        """Extract the website urls of the below articles in right column (Kinh doanh, Thể thao, Giải trí, Sức khoẻ,...)"""
        # Use Selenium here. BeautifulSoup alone can't crawl the html of the right column
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=options)
        driver.get(url)

        html = driver.page_source
        soup = BeautifulSoup(html,'lxml')

        col_right = soup.find('div', class_="col-right col-medium")
        content_boxes = col_right.find_all("div", class_="width_common content-box-category flexbox")

        # First layer of boxes
        boxes_a = []
        for content_box in content_boxes:
            box_a = content_box.find_all("a")
            boxes_a.append(box_a)

        # Second layer of boxes. Extract urls here.
        col_right_hrefs =  []
        for box_a in boxes_a:
            for box in box_a:
                col_right_hrefs.append(box.get("href"))

        col_right_hrefs = drop_duplicates(col_right_hrefs)

        # Regex to drop the urls of comment boxes
        p = re.compile('.*\.html$')
        col_right_urls = [href for href in col_right_hrefs if p.match(href)]
        self.col_right_urls = col_right_urls
        return col_right_urls

    def get_below_articles_urls(self, url, chrome_path):
        """Extract website urls from articles in the below sections (Thời sự, Pháp luật, Du lịch, Số hoá,...)"""
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=options)
        driver.get(url)

        html = driver.page_source
        soup = BeautifulSoup(html,'lxml')
        
        section_containers = soup.find_all("section", class_="section section_container")
        h3_tags = [cont.find_all("h3", class_="title-news") for cont in section_containers]

        a_tags = []
        for h3 in h3_tags:
            for a in h3:
                a_tags.append(a.find("a"))

        below_hrefs = []
        for a_tag in a_tags:
            below_hrefs.append(a_tag.get("href"))

        # Regex to drop video urls (e.g. https://video.vnexpress.net/)
        p = re.compile('.*\/\/vnexpress\.')
        below_urls = [href for href in below_hrefs if p.match(href)]
        self.below_urls = below_urls
        return below_urls

    def get_category_page_urls(self, soup):
        """Extract website urls of articles in specific category page (starting from page 2)"""
        a_tags = soup.find("section", class_="section section_container mt15").find_all("a")
        hrefs = [a_tag.get("href") for a_tag in a_tags]
        category_urls = drop_duplicates(hrefs)

        p = re.compile('.*\.html$')
        category_urls = [url for url in category_urls if p.match(url)]
        self.category_urls = category_urls
        return category_urls


class Extract_Text:
    def get_text_from_url(self, url_list):
        """Crawl raw text from normal articles"""
        crawl = {"Title":[], "Descr":[], "Content":[], "URL":[]}
        for url in url_list:
            page = urllib.request.urlopen(url)
            soup = BeautifulSoup(page, 'html.parser')

            # Extract title, decription box, and the paragraphs.
            try:
                article = soup.find('section', class_='section page-detail top-detail').find("div", class_="sidebar-1")
            except AttributeError:
                continue
            title = article.find("h1", class_="title-detail").text
            descr = article.find("p", class_="description").text
            paragraphs = article.find_all("p", class_="Normal")
            
            # Populate the crawl dictionary
            crawl["URL"].append(url)
            crawl["Title"].append(title)
            crawl["Descr"].append(descr)

            content = [para.text for para in paragraphs]
            crawl["Content"].append("\n".join(content))
        return crawl

    def get_text_from_view(self, view_url):
        """Crawl text from view articles"""
        crawl = {"Title":[], "Descr":[np.nan], "Content":[], "URL":[]}
        page = urllib.request.urlopen(view_url)
        soup = BeautifulSoup(page, 'html.parser')

        # Extract the title and the paragraphs. No description boxes in view articles.
        article = soup.find("section", class_="sidebar_2")
        title = article.find("h1", class_="title_gn_detail").text
        paragraphs = article.find_all("p", class_="Normal")

        # Populate the crawl dictionary
        crawl["Title"].append(title)
        crawl["URL"].append(view_url)

        content = [paragraph.text for paragraph in paragraphs]
        crawl["Content"].append("\n".join(content))
        return crawl
