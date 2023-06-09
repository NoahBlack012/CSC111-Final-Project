"""
CSC111 Final Project: Simplifying the UofT Course Selection Process

Description
===============================
This file was autogenerated by the scrapy library to set up a web-scraping framework
Note: This file is never run directly (During the running of main.py or during the web scraping process). A scrapy shell
command is used to run the entire web scraping process at once
"""
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


if __name__ == '__main__':
    import python_ta
    import doctest
    doctest.testmod()
    python_ta.check_all(config={
        'extra-imports': ['scrapy'],
        'allowed-io': [],
        'max-line-length': 120
    })
