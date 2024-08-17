import logging
import os
import random
import yaml

import atproto
import click
import mastodon

from typing import List

logging.basicConfig(level=logging.INFO)


def get_random_extract(path: str | os.PathLike) -> List[str | os.PathLike]:
    """Returns a sorted list of paths to files that describe a single extract

    This assumes the following structure in path
        path
        ├── folder1
        │   ├── image1_from_folder1.jpg
        │   └── image2.jpg
        ├── folder2
        │   ├── image1.jpg
        │   ├── image2.jpg
        │   └── image3.jpg
        ├── ...
        │   ├── ...
        │   └── ...
        ├── other_image_at_the_root.jpg
        ├── ...
        └── yet_another_image_at_the_root.pn

        It will sample a random path in the first level paths, e.g. it can return
        [path/other_image_at_the_root.jpg] or [path/folder1/image1.jpg, path/folder1/image2.jpg].
    """
    all_extracts = os.listdir(path)
    random_extract = random.sample(all_extracts, 1)[0]
    path_to_random_extract = os.path.join(path, random_extract)
    if os.path.isdir(path_to_random_extract):
        # Get sorted list of paths to all the images in folder
        return [
            os.path.join(path_to_random_extract, file)
            for file in sorted(os.listdir(path_to_random_extract))
        ]
    else:
        return [path_to_random_extract]


def post_to_bluesky(
    extract: List[str | os.PathLike],
    login: str,
    password: str,
    base_url: str = "https://bsky.social/xrpc",
) -> None:
    """Sends a post to Bluesky including media listed in extract"""
    client = atproto.Client(base_url=base_url)
    client.login(login=login, password=password)
    images = [open(path, "rb").read() for path in extract]
    post = client.send_images(text="", images=images)
    logging.info(f"Sent {extract} to Bluesky at post {post.uri}")


def post_to_mastodon(
    extract: List[str | os.PathLike], base_url: str, access_token: str
):
    """Sends a post to Mastodon including media listed in extract"""
    client = mastodon.Mastodon(
        api_base_url=base_url,
        access_token=access_token,
    )
    medias = [
        client.media_post(open(path_to_extract, "rb").read(), mime_type="image/jpeg")[
            "id"
        ]
        for path_to_extract in extract
    ]
    post = client.status_post("", media_ids=medias)
    logging.info(f"Sent {extract} to Mastodon at post {post.uri}")


@click.command(help="Post a random set of images from FOLDER to social medias")
@click.argument("folder", type=click.Path(exists=True), default="./images")
@click.option("--config", type=click.Path(exists=True), default="./config.yml")
@click.option("--bluesky/--no-bluesky", default=True, help="Post to Bluesky")
@click.option("--mastodon/--no-mastodon", default=True, help="Post to Mastodon")
def post_random_extract(folder, bluesky=True, mastodon=True, config=None):
    random_extract = get_random_extract(folder)
    with open(config, "r") as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)
    logging.debug("Using configuration file at {config}")
    logging.info(f"Posting {random_extract}")
    if bluesky and "bluesky" in config:
        logging.debug("Posting to Bluesky")
        post_to_bluesky(
            random_extract,
            login=config["bluesky"]["login"],
            password=config["bluesky"]["password"],
        )
    if mastodon and "mastodon" in config:
        logging.debug("Posting to Mastodon")
        post_to_mastodon(
            random_extract,
            base_url=config["mastodon"]["base_url"],
            access_token=config["mastodon"]["access_token"],
        )


if __name__ == "__main__":
    post_random_extract()
