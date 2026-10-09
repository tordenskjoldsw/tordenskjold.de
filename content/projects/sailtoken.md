---
title: SailToken
summary: TOTP authenticator for Sailfish OS, apart from the password manager
platform: Sailfish OS
order: 3
tags: [Rust, C++, Qt, QML]
license: MIT
repository: https://github.com/tordenskjoldsw/harbour-sailtoken
icon: img/projects/sailtoken/icon.svg
cover:
  path: img/projects/sailtoken/cover.png
  alt: "SailToken: authenticator for Sailfish OS"
  width: 1080
  height: 540
# The screenshots show a demo file with made-up accounts.
screenshots:
  - path: img/projects/sailtoken/screenshot-1-accounts.jpg
    alt: Account list with codes and countdown rings
    width: 480
    height: 1057
  - path: img/projects/sailtoken/screenshot-2-add.jpg
    alt: Typing in an account
    width: 480
    height: 1057
  - path: img/projects/sailtoken/screenshot-3-settings.jpg
    alt: Settings with sync, merging and the file
    width: 480
    height: 1057
---

SailToken is an authenticator for the time-based codes (TOTP) that many
services ask for after the password. It keeps them in an encrypted file of
their own, with its own master password, in the standard KeePass (KDBX 4)
format: KeePassXC on a computer opens the same file and shows the same
codes.

## Why a separate app

When I built SailVault, I decided early that it would not generate these
codes: keeping them next to the passwords turns two factors into one. So
the codes get an app of their own, with their own file and their own
master password. I only use them on my phone, and the authenticators I
found for Sailfish OS are either described as unmaintained or no longer
in the Jolla Store.

The separation helps when the password manager's file or its master
password leaks. It does not help against a compromised phone, which holds
both apps.

## What it does

- Adds accounts by scanning the QR code a service shows or by typing the
  secret; the first code shows before the account is saved
- Shows codes for SHA-1, SHA-256 and SHA-512, 1 to 10 digits, any period,
  and Steam Guard, the same codes KeePassXC shows for the same file
- Reads every way KeePassXC and KeePass store TOTP settings in an entry
- Copies a code with a tap and clears the clipboard after 30 seconds
- Renames and deletes accounts, with a recycle bin and entry history as in
  KeePassXC
- Locks after 2 minutes without use and after 30 seconds in the
  background; every change is saved at once, with three backups
- Adds a file from KeePassXC, with or without a key file, from Documents
  or Downloads, and saves a copy for the computer there
- Syncs with your own Nextcloud while the app runs and merges changes made
  on both sides, the way KeePassXC does, or merges a copy by hand

It does not support counter-based codes (HOTP) and does not show codes on
the cover or the lock screen. Importing accounts from Aegis and Google
Authenticator is planned after the first release.

## Security

SailToken connects to nothing but your own Nextcloud, and only once you
set up sync. It never writes decrypted data to disk. The
[threat model](https://github.com/tordenskjoldsw/harbour-sailtoken/blob/main/docs/threat-model.md)
describes what it protects against and where its limits are. Please report
vulnerabilities privately as described in
[SECURITY.md](https://github.com/tordenskjoldsw/harbour-sailtoken/blob/main/SECURITY.md).

## Status and install

SailToken 0.3.0 is written for Sailfish OS 5.2 and tested on the Jolla
Phone. It is not in the Jolla Store (Harbour) yet; submitting it is the
next step. Until then, you can build the RPM yourself as described in the
[README](https://github.com/tordenskjoldsw/harbour-sailtoken#building).
The [plan](https://github.com/tordenskjoldsw/harbour-sailtoken/blob/main/PLAN.md)
lists every phase and the decisions behind them.

## Contributing

Bug reports and ideas are welcome as
[issues](https://github.com/tordenskjoldsw/harbour-sailtoken/issues). If
you plan a pull request, please open an issue first. Never attach a real
secret, a real QR code or a real database, not even an encrypted one.
