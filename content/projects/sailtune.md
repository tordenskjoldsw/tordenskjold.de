---
title: SailTune
summary: Music player for Sailfish OS, for the music on the phone and on your own Jellyfin server
platform: Sailfish OS
order: 4
tags: [C++, Qt, QML]
license: MIT
repository: https://github.com/tordenskjoldsw/harbour-sailtune
icon: img/projects/sailtune/icon.svg
cover:
  path: img/projects/sailtune/cover.png
  alt: "SailTune: music player for Sailfish OS"
  width: 1080
  height: 540
# The screenshots show Jellyfin's public demo server; the covers are
# Binärpilot's, under CC BY-NC-ND.
screenshots:
  - path: img/projects/sailtune/screenshot-1-albums.jpg
    alt: Album list with covers and the mini player
    width: 480
    height: 1057
  - path: img/projects/sailtune/screenshot-2-album.jpg
    alt: An album with its tracks
    width: 480
    height: 1057
  - path: img/projects/sailtune/screenshot-3-player.jpg
    alt: Now playing with cover, seek bar and controls
    width: 480
    height: 1057
---

SailTune plays the music on your Sailfish phone and the music on your own
Jellyfin server in one app. At home or over a VPN it streams from the
server; for the road, it downloads albums and playlists to the phone and
plays them without any network.

## Why a music player

On Android, I listened to music through a streaming subscription. With
the Jolla Phone, I wanted to get away from it and play my music
collection from my own server instead, for the same reason I self-host a
few other services at home. I wanted a player for it in the Jolla Store,
made for music only and for listening without a network.

## What it does

- Plays the music on the phone from the first start, with the album art
  Sailfish found; no server and no login needed
- Adds Jellyfin servers with the password or with Quick Connect; several
  servers can be set up, one is active at a time
- Streams over https, or over plain http with a warning, for use at home
  or through a VPN
- Downloads albums, playlists and favorites in their original quality,
  or all albums at once; downloads continue where they stopped, also
  after a lost connection or a restart
- Saves downloads on the phone or, if you choose, on the memory card
- Shows only the downloaded music, with its covers, when the server is
  out of reach
- Lock screen, cover and Bluetooth controls; keeps the track and the
  position when the app is closed
- Sends plays and favorites to the server, also those made offline, and
  adds tracks to playlists or starts new ones

It plays music only: no video, photos, books or podcasts. Servers that
speak OpenSubsonic, such as Navidrome, are planned after the first
release.

## Security and privacy

SailTune talks only to the servers you add: no account, no analytics, no
advertising. Your password is used once to log in and never stored; the
access token lives in a file only SailTune can read, and removing a server
logs it out. The
[security review](https://github.com/tordenskjoldsw/harbour-sailtune/blob/main/docs/security-review-2026-10.md)
lists what was checked and fixed before the first release, and the
[privacy policy](https://github.com/tordenskjoldsw/harbour-sailtune/blob/main/PRIVACY.md)
says what is stored where. Please report vulnerabilities privately as
described in
[SECURITY.md](https://github.com/tordenskjoldsw/harbour-sailtune/blob/main/SECURITY.md).

## Status and install

SailTune 0.5.2 is written for Sailfish OS 5.2 and tested on the Jolla
Phone. It is not in the Jolla Store (Harbour) yet; the submission is under
way. Until then, you can build the RPM yourself as described in the
[README](https://github.com/tordenskjoldsw/harbour-sailtune#building).
The [plan](https://github.com/tordenskjoldsw/harbour-sailtune/blob/main/PLAN.md)
lists every phase and the decisions behind them.

## Contributing

Bug reports and ideas are welcome as
[issues](https://github.com/tordenskjoldsw/harbour-sailtune/issues). If
you plan a pull request, please open an issue first. Never attach your
password, an access token or the address of your own server.
