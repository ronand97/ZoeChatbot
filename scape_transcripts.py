# file to scrape podcast transcripts from https://zoe.com/learn/category/podcasts


import logging

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import Optional

class TranscriptScraper:

    long_podcast_base_url = "https://zoe.com/learn/category/podcasts/zoe-podcast-long-episodes"
    short_podcast_base_url = "https://zoe.com/learn/category/podcasts/zoe-podcast-shorts"

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger if logger else logging.getLogger(__name__)

    def _get_url_of_podcasts(self, long_or_short: str) -> list[str]:
        """
        Get all the urls of the long podcasts to be appended on
        to the base long podcast url
        """
        # the long podcast urls are in the form of /learn/category/podcasts/zoe-podcast-long-episodes/p/1
        # apart from the base url which has no page number
        if long_or_short == "long":
            base_url = self.long_podcast_base_url
            n_pages = 13
            base_url_for_article = "https://zoe.com"
        elif long_or_short == "short":
            base_url = self.short_podcast_base_url
            n_pages = 6
            base_url_for_article = "https://zoe.com"
        else:
            raise ValueError("long_or_short must be either 'long' or 'short'")


        podcast_urls = []

        # define the base url and subsequent pages to scrape
        urls_to_query = []
        urls_to_query.append(base_url)
        for i in range(1, n_pages + 1):
            urls_to_query.append(f"{base_url}/p/{i}")

        # parsing logic
        for url in urls_to_query:
            self.logger.debug(f"Scraping {url}")
            soup = BeautifulSoup(requests.get(url).content, "html.parser")
            for link in soup.find_all("a"):
                candidate = link.get("href")
                if candidate and candidate.startswith("/learn") and not (candidate.startswith("/learn/category") or candidate == "/learn"):
                    podcast_urls.append(candidate)
                    self.logger.debug(f"Found long podcast url: {candidate}")

        return [base_url_for_article + url for url in podcast_urls]
    



if __name__ == "__main__":
    test = TranscriptScraper()
    print(test._get_url_of_podcasts("long"))
