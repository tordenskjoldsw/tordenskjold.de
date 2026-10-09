---
title: A separate app for the second factor
summary: Why my second Sailfish OS app is an authenticator, and why it stores its codes in a KeePass file.
date: 2026-10-07
project: sailtoken
---

In my first post I wrote that I would not stop at one app. Here is the
second one: [SailToken](/projects/sailtoken), an authenticator for the
time-based codes (TOTP) that many services ask for after the password.

## Why a second app

When I built SailVault, I decided early that it would not generate these
codes. Keeping them next to the passwords turns two factors into one:
whoever gets the password file gets both. So the codes need a home of
their own, with their own file and their own master password.

I only use these codes on my phone. The authenticators I found for
Sailfish OS are either described as unmaintained in the forum or no
longer in the Jolla Store, and I want one there, for the same reason as
SailVault.

To be clear about the limits: the separation helps when the password
manager's file or its master password leaks. It does not help against a
compromised phone, which holds both apps.

## Which file format

This was the decision I weighed longest. For my own use, the vault format
of Aegis, a popular authenticator on Android, would have been enough. It
is small and made for exactly this job. A list of codes encrypted with the
age tool was another option.

What decided it was the worst case: the phone is gone. With a KeePass
(KDBX 4) file, KeePassXC on any computer opens the backup on my Nextcloud
and shows the same codes, and other KeePass apps on Sailfish OS can read
it too. That only works if the Nextcloud login itself does not need a
code from this file, so the app will say so when sync is set up. Moving
over from Aegis or Google Authenticator is a one-time import, which works
with any storage format.

## Building it

SailToken reuses the KeePass code from SailVault, which has been tested
on the Jolla Phone and reviewed twice. The two apps stay independent: the
code is copied, not shared, and a fix in one is carried over to the other.

The first step is done. The app skeleton passes the Jolla Store validator
and runs on my phone, even if it shows little more than its version so
far.

## What's next

Next is the camera. Scanning a QR code is the one part SailVault taught
me nothing about, so it comes first, before any code is generated. The
source is public from the first commit, and the
[plan](https://github.com/tordenskjoldsw/harbour-sailtoken/blob/main/PLAN.md)
is in the repository if you want to follow along.
