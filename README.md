# Leverage bot poster

This is a simple Python script that posts a random set of images to Bluesky and Mastodon. See it in action on [@leverageooc.mas.to](https://mas.to/@LeverageOoc) and on [@leverageooc.bsky.social](https://leverageooc.bsky.social).

## Environment setup

Just create a virtualenv and install the dependencies listed in the requirements file:
```bash
python -m venv .venv
pip install -r requirements
```

## Configuration

See the `configuration_sample.yaml` file.

### Authentication

This is pretty straightforward, you will need either one or both of:
- a Bluesky account and a [Bluesky app password](https://bsky.app/settings/app-passwords)
- a Mastodon account and the [API access token](https://mas.to/settings/applications)

**Remember to flag your account as a bot on Mastodon!**

### Media storage

By default, the script will look for medias in the `images/` folder. It expects a structure as below:
```
images
├── folder1
│   ├── image1_from_folder1.jpg
│   └── image2.jpg
├── folder2
│   ├── image1.jpg
│   ├── image2.jpg
│   └── image3.jpg
├── ...
│   ├── ...
│   └── ...
├── other_image_at_the_root.jpg
├── ...
└── yet_another_image_at_the_root.png
```

The script will select randomly a folder or a file in the root media folder.
If the selected path is a file, then the post will be sent with a single media (e.g. `other_image_at_the_root.jpg`).
If the selected path is a folder, then the post will be sent with *all medias* inside that folder, alphabetically ordered.
I therefore recommend to use a consistent naming schemes across folders, especially if you care about the order in which the images will appear on Bluesky and Mastodon.


**Warnings**:
- do not put more than 4 files in each folder (except the root folder). Neither Bluesky nor Mastodon support more than 4 images per post as far as I know;
- do not put a media that is not supported by the platforms (basically, most image formats are fine, alongside some video formats, but everything else is no game). Videos should be fine but I haven't tested that.
- check the media requirements before adding files to the media folder. For example, Bluesky has a 1Mb limit for each image, so ensure that all your images are under this threshold.
- the script does not effort whatsoever to scrape e.g. EXIF metadata. Be careful if you want to post "anonymized" stuff.

## Run as a systemd timer

First, create a new systemd unit for this bot, typically in `/etc/systemd/system/leverage-bot.unit`. For example:

```
[Unit]
Description=Run Leverage bot to post
After=multi-user.target

[Service]
Type=simple
User=altay
Group=altay
WorkingDirectory=/path/to/leverage-bot/
ExecStart=/path/to/leverage-bot/.venv/bin/python leverage_poster.py --conf config.yml

# Security options
# You do you, that's what I use
LockPersonality=true
NoNewPrivileges=yes
ProtectSystem=true
ProtectClock=true
ProtectControlGroups=true
ProtectKernelTunables=true
ProtectKernelLogs=true
PrivateTmp=true
PrivateDevices=true

[Install]
WantedBy=multi-user.target
```

Then, setup a systemd timer `/etc/systemd/system/leverage-bot.timer` to run the bot periodically, for example every six hours in my case:

```
[Unit]
Description=Run Leverage bot to post every 6 hours

[Timer]
OnCalendar=00/6:00
# Runs everyday at midnight, six am, noon and six pm

[Install]
WantedBy=timers.target
```

Then, you can enable the systemd timer so it starts after boot with `systemctl enable leverage-bot.timer`.
You can finally start the timer using `systemctl start leverage-bot.timer`.

## Licensing


