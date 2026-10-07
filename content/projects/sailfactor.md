---
title: SailFactor
summary: TOTP authenticator for Sailfish OS, apart from the password manager
platform: Sailfish OS
order: 3
tags: [Rust, C++, Qt, QML]
license: MIT
repository: https://github.com/tordenskjoldsw/harbour-sailfactor
icon: img/projects/sailfactor/icon.svg
---

SailFactor is an authenticator for the time-based codes (TOTP) that many
services ask for after the password. It keeps them in an encrypted file of
their own, with its own master password, apart from the password manager.

## Why a separate app

SailVault deliberately does not generate TOTP codes: keeping them next to
the passwords would turn two factors into one. SailFactor is the app for
the second factor. The separation protects the codes when the password
manager's file or its master password leaks. It does not protect against a
compromised phone, which holds both apps.

## What it will do

- Add accounts by scanning their QR code with the camera or by typing the
  secret
- Show the current codes with a countdown, and clear the clipboard after
  copying
- Keep the accounts in a standard KeePass (KDBX 4) file, the way KeePassXC
  stores them, so KeePassXC on a computer shows the same codes
- Sync that file with your own Nextcloud, like SailVault
- Import accounts from Aegis and Google Authenticator after the first
  release

It will not support counter-based codes (HOTP) and will not show codes on
the cover or the lock screen.

## Status

SailFactor is in development and not usable yet. The app skeleton builds,
passes the Jolla Store (Harbour) validator and runs on the Jolla Phone.
Scanning QR codes comes next. The
[plan](https://github.com/tordenskjoldsw/harbour-sailfactor/blob/main/PLAN.md)
lists every phase and the decisions behind them.

## Contributing

Ideas and bug reports are welcome as
[issues](https://github.com/tordenskjoldsw/harbour-sailfactor/issues).
Never attach a real secret, a real QR code or a real database, not even an
encrypted one.
