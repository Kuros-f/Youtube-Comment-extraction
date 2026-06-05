import os
import json
import time
import pandas as pd

from urllib.parse import (
    urlparse,
    parse_qs
)

from googleapiclient.discovery import build

# =========================
# SETTINGS
# =========================

API_KEY = "Put your Youtube API"

VIDEO_URL = "Put your Youtube URL like https://www.youtube........"

CHECKPOINT_FILE = "data/checkpoint.json"

EXCEL_FILE = "data/comments.xlsx"

# =========================
# YOUTUBE API
# =========================

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

# =========================
# EXTRACT VIDEO ID
# =========================

def extract_video_id(url):

    parsed_url = urlparse(url)

    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]

    if parsed_url.hostname in (
        "www.youtube.com",
        "youtube.com"
    ):

        if parsed_url.path == "/watch":
            return parse_qs(
                parsed_url.query
            )["v"][0]

        if parsed_url.path.startswith(
            "/shorts/"
        ):
            return parsed_url.path.split(
                "/"
            )[2]

    raise ValueError(
        "Invalid YouTube URL"
    )


VIDEO_ID = extract_video_id(
    VIDEO_URL
)

# =========================
# CHECKPOINT LOAD
# =========================

def load_checkpoint():

    if os.path.exists(CHECKPOINT_FILE):

        with open(
            CHECKPOINT_FILE,
            "r"
        ) as f:

            return json.load(f)

    return {
        "nextPageToken": None
    }

# =========================
# CHECKPOINT SAVE
# =========================

def save_checkpoint(token):

    with open(
        CHECKPOINT_FILE,
        "w"
    ) as f:

        json.dump(
            {
                "nextPageToken": token
            },
            f
        )

# =========================
# SAVE TO EXCEL
# =========================

def save_to_excel(rows):

    df_new = pd.DataFrame(rows)

    if os.path.exists(EXCEL_FILE):

        df_old = pd.read_excel(
            EXCEL_FILE
        )

        df = pd.concat(
            [df_old, df_new],
            ignore_index=True
        )

    else:

        df = df_new


    df = df[
        df["comment"].str.len() > 2
    ]

    df = df[
        df["comment"].notna()
    ]

    df.to_excel(
        EXCEL_FILE,
        index=False
    )

# =========================
# MAIN EXTRACTION
# =========================

def fetch_comments():

    checkpoint = load_checkpoint()

    next_page_token = checkpoint.get(
        "nextPageToken"
    )

    while True:

        response = youtube.commentThreads().list(
            part="snippet",
            videoId=VIDEO_ID,
            maxResults=100,
            pageToken=next_page_token,
            textFormat="plainText"
        ).execute()

        rows = []

        for item in response["items"]:

            comment = item["snippet"][
                "topLevelComment"
            ]

            snippet = comment["snippet"]

            text = snippet.get(
                "textDisplay",
                ""
            )

            text = text.strip()

            text = " ".join(
                text.split()
            )

            rows.append({

                "comment_type": "parent",

                "parent_id":
                    comment["id"],

                "author_channel_id":
                    snippet.get(
                        "authorChannelId",
                        {}
                    ).get(
                        "value",
                        ""
                    ),

                "author_name":
                    snippet.get(
                        "authorDisplayName"
                    ),

                "comment":
                    text,

                "likes":
                    snippet.get(
                        "likeCount"
                    ),

                "published_at":
                    snippet.get(
                        "publishedAt"
                    ),

                "video_id":
                    snippet.get(
                        "videoId"
                    )
            })

            if item["snippet"].get(
                "totalReplyCount",
                0
            ) > 0:

                parent_id = comment["id"]

                replies_response = youtube.comments().list(
                    part="snippet",
                    parentId=parent_id,
                    maxResults=100,
                    textFormat="plainText"
                ).execute()

                for reply_item in replies_response["items"]:

                    reply_snippet = reply_item[
                        "snippet"
                    ]

                    reply_text = reply_snippet.get(
                        "textDisplay",
                        ""
                    )

                    reply_text = reply_text.strip()

                    reply_text = " ".join(
                        reply_text.split()
                    )

                    rows.append({

                        "comment_type": "reply",

                        "parent_id":
                            parent_id,

                        "author_channel_id":
                            reply_snippet.get(
                                "authorChannelId",
                                {}
                            ).get(
                                "value",
                                ""
                            ),

                        "author_name":
                            reply_snippet.get(
                                "authorDisplayName"
                            ),

                        "comment":
                            reply_text,

                        "likes":
                            reply_snippet.get(
                                "likeCount"
                            ),

                        "published_at":
                            reply_snippet.get(
                                "publishedAt"
                            ),

                        "video_id":
                            reply_snippet.get(
                                "videoId"
                            )
                    })

        save_to_excel(rows)

        next_page_token = response.get(
            "nextPageToken"
        )

        save_checkpoint(
            next_page_token
        )

        print("Batch saved")

        if not next_page_token:

            print("Finished")

            break

        time.sleep(1)

# =========================
# START
# =========================

if __name__ == "__main__":

    fetch_comments()