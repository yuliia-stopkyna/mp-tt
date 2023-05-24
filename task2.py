import os
import time

import httpx
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

ARTICLES_URLS = [
    "https://startupily.com/how-to-create-a-professional-website-for-your-small-business/",
    "https://www.mailbutler.io/blog/email/email-inbox-management/",
    "https://www.selfcad.com/blog/common-3d-modeling-mistakes-and-how-to-avoid-them",
    "https://globalowls.com/increase-efficiency-recruiting-processes/",
    "https://www.jeuxvideo.com/forums/42-51-68599132-2-0-1-0-macbook-pro-vs-macbook-air.htm",
    "https://forum.basercms.net/t/topic/825/3",
    "https://gadgetgets.com/5-pros-and-cons-of-purchasing-a-macbook/",
    "https://blockcrux.com/how-to-remove-search-pulse-browser-hijacker-from-mac/",
    "https://gamecravings.com/modder-claims-this-16-half-will-cease-your-m2-macbook-air-from-overheating/",
    "https://hammburg.com/how-to-get-rid-of-malware-on-mac/",
    "https://career-women.org/wenn-der-mac-abstuerzt-so-beheben-sie-das-problem.html",
    "https://ireviewlot.com/tips-on-managing-digital-clutter/",
    "https://www.zenbusiness.com/blog/how-to-improve-graphic-designer-performance/",
    "https://agilitycms.com/resources/posts/how-customer-experiences-are-evolving-in-the-digital-space",
    "https://dzieckowwarszawie.pl/artykul/jak-przyspieszyc-dzialanie-laptopa-mac/",
    "https://engageforsuccess.org/productivity/top-7-strategies-to-help-boost-hybrid-work-productivity/",
    "https://www3.yggtorrent.do/forum/index.php?threads/macos-parallels-desktop-17-m1.62694/page-2",
    "https://www.technik-smartphone-news.de/5-gute-tipps-wie-du-deinen-mac-aufraeumen-kannst/",
    "https://clipchamp.com/en/blog/how-to-send-large-videos-signal-app-video-compressor/",
    "https://lattelindsay.com/random-ramblings/5-tips-to-overcome-writers-blocks-as-a-blogger/",
]

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL_MESSAGE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def get_links_report(articles_urls: list[str]) -> list[dict]:
    report = []
    options = Options()
    options.page_load_strategy = "none"
    with webdriver.Chrome(options=options) as driver:
        for url in articles_urls:
            driver.get(url)
            time.sleep(6)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            if soup.select_one("h1.post-title span") is not None:
                title = soup.select_one("h1.post-title span").text
            else:
                title = soup.title.text

            page_links = soup.select("a")
            article_report = {
                "article_url": url,
                "title": title,
                "publication_date": get_publication_date(soup=soup),
            }
            macpaw_links = 0
            for link in page_links:
                if link.has_attr("href"):
                    if "macpaw" in link["href"] or "cleanmymac" in link["href"]:
                        if link.has_attr("rel"):
                            nofollow = "nofollow" in link["rel"]
                        else:
                            nofollow = False
                        macpaw_link = {
                            "macpaw_link": link["href"],
                            "nofollow": nofollow,
                            "anchor_text": link.text,
                        }
                        macpaw_links += 1
                        report.append({**article_report, **macpaw_link})

            if not macpaw_links:
                report.append(
                    {
                        **article_report,
                        "macpaw_link": None,
                        "nofollow": None,
                        "anchor_text": None,
                    }
                )

    return report


def get_publication_date(soup: BeautifulSoup) -> str | None:
    publication_date = None

    selector_variants = (
        soup.select_one("span.updated"),
        soup.select_one("p.post-meta span.tie-date"),
        soup.select_one("div.date"),
        soup.select_one("div.jeg_meta_date a"),
        soup.select_one("article#js-post-420640 dd"),
        soup.select_one("span.posts-date"),
    )

    if soup.select("div.mob\:pl-5.mob\:mb-10 > p"):
        publication_date = soup.select("div.mob\:pl-5.mob\:mb-10 > p")[1].text

    if soup.time:
        publication_date = soup.time["datetime"]

    if soup.select_one("span.tophead"):
        publication_date = (
            soup.select_one("span.tophead").text.replace("On:", "").strip()
        )

    for variant in selector_variants:
        if variant is not None:
            publication_date = variant.text.strip()

    return publication_date


def write_report_to_csv(report: list[dict]) -> None:
    df = pd.DataFrame.from_records(report)
    df.to_csv("task2_report.csv", index=False)


def check_report_changes(
    previous_report: pd.DataFrame, current_report: list[dict]
) -> list[dict]:
    changes = []

    for row in current_report:
        prev = previous_report[previous_report["article_url"] == row["article_url"]]

        if row["macpaw_link"] is None and not prev.iloc[0, 3] != prev.iloc[0, 3]:
            change = {
                "article_url": row["article_url"],
                "change": "MacPaw link is absent",
            }
            changes.append(change)
            continue

        if row["macpaw_link"] is not None:
            prev = prev[prev["macpaw_link"] == row["macpaw_link"]]
            if prev.shape[0]:
                if row["nofollow"] != prev.iloc[0, 4]:
                    change = {
                        "article_url": row["article_url"],
                        "change": f"For link {row['macpaw_link']} nofollow "
                        f"attribute was changed to {row['nofollow']}",
                    }
                    changes.append(change)

            else:
                change = {
                    "article_url": row["article_url"],
                    "change": f"MacPaw link {row['macpaw_link']} appeared on the website",
                }
                changes.append(change)

    return changes


def send_notification(changes: list[dict] = None, message: str = None) -> None:
    if changes is not None:
        message = ""
        for change in changes:
            message += (
                f"Change for website: {change['article_url']}. {change['change']}.\n"
            )

    httpx.post(URL_MESSAGE, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})


def main() -> None:
    current_report = get_links_report(ARTICLES_URLS)
    if os.path.exists("task2_report.csv"):
        previous_report = pd.read_csv("task2_report.csv")
        changes = check_report_changes(
            previous_report=previous_report, current_report=current_report
        )
        if changes:
            send_notification(changes=changes)
        else:
            send_notification(message="No changes detected.")
        write_report_to_csv(current_report)
    else:
        write_report_to_csv(current_report)
        send_notification(message="First report was created.")


if __name__ == "__main__":
    main()
