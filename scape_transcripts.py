# file to scrape podcast transcripts from https://zoe.com/learn/category/podcasts

import logging

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from typing import Optional
from pathlib import Path
import json


class PodcastTranscript:
    def __init__(self, title: str, transcript: str):
        self.title = title
        self.transcript = transcript

    def transcript_to_dict(self) -> dict:
        return {"title": self.title, "transcript": self.transcript}


class TranscriptScraper:

    long_podcast_base_url = (
        "https://zoe.com/learn/category/podcasts/zoe-podcast-long-episodes"
    )
    short_podcast_base_url = (
        "https://zoe.com/learn/category/podcasts/zoe-podcast-shorts"
    )

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
                if (
                    candidate
                    and candidate.startswith("/learn")
                    and not (
                        candidate.startswith("/learn/category") or candidate == "/learn"
                    )
                ):
                    podcast_urls.append(candidate)
                    self.logger.debug(f"Found long podcast url: {candidate}")

        return [base_url_for_article + url for url in podcast_urls]

    def _get_transcript(self, url: str) -> PodcastTranscript:
        """
        Get the transcript of the podcast from the given url
        """
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        # all transcripts start at a point in the page where it says "Transcript" as a header
        # and end at the next header
        transcript = ""
        for header in soup.find_all("h2"):
            if header.text.lower() == "transcript":
                for sibling in header.next_siblings:
                    if sibling.name == "h2":
                        break
                    if sibling.name == "p":
                        transcript += sibling.text + " "
        return PodcastTranscript(soup.title.text, transcript)

    def run(self):
        """
        Run the scraper to get all the transcripts
        and write to LFS
        """
        self.logger.info("Starting scraping of transcript URLS")
        long_podcast_urls = self._get_url_of_podcasts("long")
        short_podcast_urls = self._get_url_of_podcasts("short")
        all_podcast_urls = long_podcast_urls + short_podcast_urls
        transcripts = []
        self.logger.info("Starting scraping of transcripts")
        for url in tqdm(all_podcast_urls):
            transcripts.append(self._get_transcript(url))

        self.logger.info("Writing transcripts to LFS")
        folder_path = Path("transcripts")  # create folder if it doesn't exist
        folder_path.mkdir(parents=True, exist_ok=True)
        for transcript in transcripts:
            with open(folder_path / f"{transcript.title}.txt", "w") as f:
                json.dump(transcript.transcript_to_dict(), f)


if __name__ == "__main__":
    TranscriptScraper().run()
