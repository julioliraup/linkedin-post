import os
import sys
import requests

ACCESS_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
AUTHOR_URN = os.environ["LINKEDIN_PERSON_URN"]
IMAGE_PATH = os.environ.get("IMAGE_PATH", "")
POST_TEXT = os.environ.get("POST_TEXT", "Posted automatically via GitHub Actions!")

API_BASE = "https://api.linkedin.com/rest"
LINKEDIN_VERSION = "202504"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "LinkedIn-Version": LINKEDIN_VERSION,
    "X-Restli-Protocol-Version": "2.0.0",
}


def upload_image(image_path: str) -> str:
    init_payload = {
        "initializeUploadRequest": {
            "owner": AUTHOR_URN,
        }
    }

    init_resp = requests.post(
        f"{API_BASE}/images?action=initializeUpload",
        headers=HEADERS,
        json=init_payload,
    )

    if init_resp.status_code != 200:
        raise Exception(
            f"Failed to initialize image upload: "
            f"{init_resp.status_code} {init_resp.text}"
        )

    value = init_resp.json()["value"]
    upload_url: str = value["uploadUrl"]
    image_urn: str = value["image"]

    with open(image_path, "rb") as fh:
        binary_data = fh.read()

    upload_resp = requests.put(
        upload_url,
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/octet-stream",
        },
        data=binary_data,
    )

    if upload_resp.status_code not in (200, 201):
        raise Exception(
            f"Failed to upload image binary: "
            f"{upload_resp.status_code} {upload_resp.text}"
        )

    print(f"Image uploaded: {image_urn}")
    return image_urn


def create_post(image_urn: str | None = None) -> str:
    payload: dict = {
        "author": AUTHOR_URN,
        "commentary": POST_TEXT,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    if image_urn:
        payload["content"] = {"media": {"id": image_urn}}

    post_resp = requests.post(
        f"{API_BASE}/posts",
        headers=HEADERS,
        json=payload,
    )

    if post_resp.status_code != 201:
        raise Exception(
            f"Failed to create post: "
            f"{post_resp.status_code} {post_resp.text}"
        )

    post_id = post_resp.headers.get("x-restli-id", "unknown")
    print(f"Post published: {post_id}")
    return post_id


def main() -> None:
    image_urn = None

    if IMAGE_PATH:
        if not os.path.isfile(IMAGE_PATH):
            raise Exception(f"Image file not found: {IMAGE_PATH}")
        image_urn = upload_image(IMAGE_PATH)

    create_post(image_urn=image_urn)


if __name__ == "__main__":
    main()
