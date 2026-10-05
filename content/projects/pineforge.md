---
title: PineForge
summary: Modern PineTime firmware written in Rust with Embassy
platform: PineTime
order: 2
tags: [Rust, Embassy]
license: MIT OR Apache-2.0
repository: https://github.com/tordenskjoldsw/PineForge
download: https://github.com/tordenskjoldsw/PineForge/releases/latest
# TODO(content): icon and cover image (photo of the watch running PineForge)
---

PineForge is an independent firmware for the PineTime, written in Rust
with Embassy. It is not a fork or port of InfiniTime, but it builds on the
hardware research, protocol documentation and tooling of the PineTime,
InfiniTime, Gadgetbridge and Embassy communities.

It runs on a sealed watch through the existing InfiniTime MCUBoot
bootloader and has been the firmware on my own watch since late July 2026:
it keeps time, takes notifications, updates over the air and is worn
daily.

## What it does

- Two watchfaces: FORGE, with numerals drawn from rectangles instead of a
  font, and TERMINAL, with one labelled row per reading
- Notifications from the phone, an application launcher and settings that
  survive a reboot
- Music control for whatever is playing on the phone
- Step counting, heart rate, a flashlight and a Bluetooth switch
- Pairing, time sync, weather and firmware updates over Bluetooth with
  Gadgetbridge
- Underneath: Embassy on the nRF52832, strict `no_std`, no heap and no
  full-screen framebuffer

## Status

PineForge is worn daily, but the evidence behind it is one watch, one
bootloader version and one phone. Expect bugs, slow OTA transfers and
possible recovery work. Step counting and heart rate have not been
compared against a reference instrument yet, so their numbers are
indicative. The
[tested configurations](https://github.com/tordenskjoldsw/PineForge/blob/main/docs/TESTED-CONFIGURATIONS.md)
list exactly what has been verified.

## Install

Each release comes with a DFU ZIP that installs through the Gadgetbridge
firmware installer. A new image first runs as an unconfirmed test image
and rolls back to the previous firmware on reset until you confirm it on
the watch. Keep a known-good InfiniTime DFU ZIP on your phone, and read
[Getting started](https://github.com/tordenskjoldsw/PineForge/blob/main/GETTING-STARTED.md)
and the notes on
[testing on a sealed PineTime](https://github.com/tordenskjoldsw/PineForge/blob/main/docs/SEALED-PINETIME-TESTING.md)
before flashing.

## Contributing

PineForge is maintained on a best-effort basis by one person, in the
evenings around a day job. Issues and pull requests are welcome, see
[CONTRIBUTING.md](https://github.com/tordenskjoldsw/PineForge/blob/main/CONTRIBUTING.md).

## Thanks

PineForge would not exist without
[InfiniTime](https://github.com/InfiniTimeOrg/InfiniTime), whose Bluetooth
services and hardware work it builds on, and without
[Embassy](https://github.com/embassy-rs/embassy) and the wider PineTime
community.
