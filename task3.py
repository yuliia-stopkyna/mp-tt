import json
import os

import pandas as pd
import httpx
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("PRODUCTHUNT_TOKEN")
BEFORE_DATE = "2023-03-30"
AFTER_DATE = "2023-03-14"
TOPICS = (
    "apple",
    "mac",
    "ios",
    "apple-watch",
    "imessage-apps",
    "remote-work",
    "productivity",
    "time-tracking",
    "meetings",
)
URL = "https://api.producthunt.com/v2/api/graphql"
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}",
    "Host": "api.producthunt.com",
}
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL_MESSAGE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def get_producthunt_data(
    before_date: str, after_date: str, topics: tuple, url: str, headers: dict
) -> list[dict]:
    posts_data = []
    post_names = []

    for topic in topics:
        query = f"""
        {{
          posts(topic: {json.dumps(topic)}, 
                postedAfter: {json.dumps(after_date)}, 
                postedBefore: {json.dumps(before_date)}) {{
            nodes {{
              name
              description
              votesCount
              tagline
              productLinks {{
                url
              }}
            }}
          }}
        }}
        """
        response = httpx.post(URL, json={"query": query}, headers=headers).json()
        posts = response["data"]["posts"]["nodes"]

        for post in posts:
            if post["name"] not in post_names:
                post_data = {
                    "name": post["name"],
                    "description": post["description"],
                    "num_votes": post["votesCount"],
                    "tagline": post["tagline"],
                    "product_link": post["productLinks"][0]["url"],
                    "topic": topic,
                }
                post_names.append(post["name"])
                posts_data.append(post_data)

    return posts_data


def summarize_data(
    posts_data: list[dict], before_date: str, after_date: str
) -> list[str]:
    df = pd.DataFrame.from_records(posts_data)
    num_products = df.shape[0]
    num_products_by_topics = (
        df.groupby("topic")[["name"]]
        .count()
        .sort_values("name", ascending=False)
        .rename(columns={"name": "num_products"})
    )
    df["max_votes"] = df.groupby(["topic"])["num_votes"].transform(max)
    max_votes = df[df["num_votes"] == df["max_votes"]]
    max_votes_dict = max_votes.to_dict("records")

    return make_message(
        num_products=num_products,
        num_products_by_topics=num_products_by_topics,
        max_votes=max_votes_dict,
        before_date=before_date,
        after_date=after_date,
    )


def make_message(
    num_products: int,
    num_products_by_topics: pd.DataFrame,
    max_votes: dict,
    after_date: str,
    before_date: str,
) -> list[str]:
    messages = []
    message_part1 = (
        f"There are {num_products} products found in "
        f"selected categories after {after_date} and before {before_date}.\n\n"
    )
    message_part1 += "Number of products by topics:\n"
    message_part1 += "------------------------------------\n"
    message_part1 += str(num_products_by_topics)
    message_part1 += "\n------------------------------------"
    messages.append(message_part1)
    message_part2 = (
        "\nThese products got the highest number of votes in their categories:\n"
    )
    messages.append(message_part2)
    for product in max_votes:
        product_message = (
            f"Topic: {product['topic']}\n"
            f"Name: {product['name']}\n"
            f"Tagline: {product['tagline']}\n"
            f"Description: {product['description']}\n"
            f"Number of votes: {product['num_votes']}\n"
            f"Link: {product['product_link']}\n\n"
        )
        messages.append(product_message)

    return messages


def send_message(messages: list[str]) -> None:
    for message in messages:
        httpx.post(URL_MESSAGE, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})


def main() -> None:
    posts_data = get_producthunt_data(
        before_date=BEFORE_DATE,
        after_date=AFTER_DATE,
        topics=TOPICS,
        url=URL,
        headers=HEADERS,
    )
    messages = summarize_data(
        posts_data=posts_data, before_date=BEFORE_DATE, after_date=AFTER_DATE
    )
    send_message(messages)


if __name__ == "__main__":
    main()
