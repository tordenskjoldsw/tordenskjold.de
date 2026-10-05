---
title: SailVault
summary: KeePass-compatible password manager for Sailfish OS
platform: Sailfish OS
order: 1
tags: [Rust, C++, Qt, QML]
license: MIT
repository: https://github.com/tordenskjoldsw/harbour-sailvault
icon: img/projects/sailvault/icon.svg
cover:
  path: img/projects/sailvault/cover.png
  alt: "SailVault: password manager for Sailfish OS"
  width: 1080
  height: 540
# The screenshots show a demo database with made-up data.
screenshots:
  - path: img/projects/sailvault/screenshot-1-entries.jpg
    alt: Entry list with groups and entries
    width: 480
    height: 1057
  - path: img/projects/sailvault/screenshot-2-entry.jpg
    alt: An entry with its password hidden
    width: 480
    height: 1057
  - path: img/projects/sailvault/screenshot-3-settings.jpg
    alt: Settings with sync, merge and import
    width: 480
    height: 1057
---

SailVault keeps your passwords in a standard KeePass (KDBX 4) file. No
account, no server, no lock-in: the same file opens in KeePassXC on your
computer.

## Why another password manager

I wanted my passwords on my phone, in a format I control, in
an app that runs sandboxed.

## What it does

- Opens KDBX 4.0 and 4.1 databases with a master password, a key file or
  both
- Creates, edits, moves and deletes entries and groups, with entry history
  and a recycle bin as in KeePassXC
- Adds older KDBX 3.1 databases by storing them as KDBX 4 with Argon2id;
  the original file stays unchanged
- Syncs with your own Nextcloud and merges changes made on both sides, the
  way KeePassXC does
- Imports Bitwarden and Vaultwarden JSON exports
- Clears the clipboard after 30 seconds and locks after five minutes
  without use

It deliberately does not generate TOTP codes, unlock with the fingerprint
reader or autofill. The
[README](https://github.com/tordenskjoldsw/harbour-sailvault#what-sailvault-does-not-do)
explains why.

## Security

SailVault connects to nothing but your own Nextcloud, and only once you
set up sync. It never writes decrypted data to disk. The
[threat model](https://github.com/tordenskjoldsw/harbour-sailvault/blob/main/docs/threat-model.md)
describes what it protects against and where its limits are. Please report
vulnerabilities privately as described in
[SECURITY.md](https://github.com/tordenskjoldsw/harbour-sailvault/blob/main/SECURITY.md).

## Status and install

SailVault is written for Sailfish OS 5.2 and tested on the Jolla Phone. It
is submitted to the Jolla Store (Harbour) and waits for review. Until it is
available there, you can build the RPM yourself as described in the
[README](https://github.com/tordenskjoldsw/harbour-sailvault#building).

## Contributing

Bug reports and ideas are welcome as
[issues](https://github.com/tordenskjoldsw/harbour-sailvault/issues). If you
plan a pull request, please open an issue first. Never attach a real
database or export, not even an encrypted one.
