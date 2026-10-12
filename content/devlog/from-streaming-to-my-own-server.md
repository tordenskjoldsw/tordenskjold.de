---
title: From streaming to my own server
summary: Why my third Sailfish OS app is a music player for my own server, and the decisions that shaped it.
date: 2026-10-12
project: sailtune
---

After a password manager and an authenticator, my third app for Sailfish
OS is [SailTune](/projects/sailtune), a music player for the music on the
phone and on your own Jellyfin server.

## Why a music player

On Android, I listened to music through a streaming subscription. With
the Jolla Phone, I wanted to get away from it: my music collection, on
my own server, for the same reason I self-host a few other services at
home.

What I was missing was a player for that server in the Jolla Store, made
for music and for listening without a network. There are clients for
self-hosted servers on OpenRepos, and that freedom of choice is a good
thing. But as with SailVault, I believe there should be good native apps
in the Jolla Store, because that is where most people will look first.

## The decisions

**Offline first.** SailTune never opens on a login page, not even on the
first start. It opens on the music on the phone, like any music player,
and a server is something you add. When the server is out of reach, the
app shows what is downloaded and plays it, with no network and no login.

**Downloads you can rely on.** Albums and playlists download in their
original quality. A download that is cut off, because I left the WLAN or
closed the app, continues from the byte where it stopped, and a file is
checked against the size the server announced before it counts as
downloaded. Since today, downloads can also go to the memory card.

**Jellyfin first, more servers later.** To ship sooner, the first version
talks to Jellyfin only. Everything that depends on the server sits behind
one line in the code, so that servers speaking OpenSubsonic, such as
Navidrome, can follow without reshaping the app.

**No stored password.** The password is used once to log in and never
stored. The app keeps only the server's access token, in a file only
SailTune can read, and removing a server logs it out.

**Music only.** No video, photos, books or podcasts. Artists, albums,
playlists and the queue are enough for me.

## Building it

The one real surprise was playback. Qt's media player reports the end of
a track a moment before it has actually stopped, so starting the next
track on that report did not work. Waiting for the player to stop fixed
it. Since then, SailTune has played my music over Bluetooth in the car,
through a whole drive with the screen off, without interruption.

## What's next

SailTune 0.5.2 is on its way into the Jolla Store (Harbour) and waits for
QA. Until it is there, you can build it yourself as described on the
[project page](/projects/sailtune). Next on the
[plan](https://github.com/tordenskjoldsw/harbour-sailtune/blob/main/PLAN.md)
are OpenSubsonic servers.
