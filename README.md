# CoolROM Downloader v3

A powerful command‑line tool for downloading and extracting ROMs from [CoolROM](http://coolrom.com.au).

> Version 3 was developed by **AloysiusAntioch**, building on the original work by [Victor Oliveira](https://github.com/victor-oliveira1/coolrom_downloader).

---

![Screenshot](https://raw.githubusercontent.com/aloysiusantioch/coolrom_downloader_v3/refs/heads/master/coolromv3_downloader.png)

---
<br>

## 🧮 Features

- Console selection via CLI
- ROM filtering by first letter
- Keyword search across ROM names
- Multi-ROM selection and download
- Save & extract to custom path
- Archive cleanup after extraction
- Chown extracted files (`user:user`)
- Set file permissions (e.g., `755`)
- Extracts `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.gz`, `.7z`
- Keyboard interrupt support and progress reporting

<br>
---
<br>

## 📦 Requirements

- Python 3 (`/usr/bin/python3`)
- External Python module:
  - [`py7zr`](https://pypi.org/project/py7zr/) – required for `.7z` support

### Install py7zr:

```bash
sudo apt install python3-pip
sudo /usr/bin/python3 -m pip install py7zr
```

<br>
---
<br>

## 🚀 Usage

### Command-line example:

```bash
./coolrom_downloader.py \
  --console 20 \
  --search "Final Fantasy" \
  --rom 0 1 2 \
  --output /roms/psx \
  --clean \
  --user romuser \
  --perms 755
```

### Interactive mode:

```bash
./coolrom_downloader.py
# Prompts you to select console, letter/search, and ROMs
```

<br>
---
<br>

## 🧰 CLI Flags

| Flag              | Description                                           |
|-------------------|-------------------------------------------------------|
| `-c`, `--console` | Console index number (from list)                      |
| `-l`, `--letter`  | Filter ROMs by starting letter                        |
| `-s`, `--search`  | Search ROMs by keyword (case-insensitive)             |
| `-r`, `--rom`     | One or more ROM indexes to download                   |
| `-o`, `--output`  | Target directory to save & extract ROMs               |
| `-C`, `--clean`   | Delete archive file after extraction                  |
| `-u`, `--user`    | Set user/group ownership of extracted files           |
| `-p`, `--perms`   | Recursively chmod extracted files (e.g., `755`)       |

<br>
---
<br>

## 📜 Future Development Goals
- Silent mode (--quiet)
- Check for missing dependencies on startup
- Optional Logging to File with --log=logfile.txt
- Console + ROM Lists Cache (Local)
- Retry Mechanism for Failed Downloads
- Better Help Output / Categorized Flags
- Possile conversion to app for easy install

<br>
---
<br>

## 🔮 Changelog

### v3.3 – Major rewrite by **AloysiusAntioch**

- Added support for CLI arguments:
  - `--console`, `--letter`, `--search`, `--rom`, `--output`, `--clean`, `--user`, `--perms`
- Extracts `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.gz`, `.7z`
- Uses `py7zr` module for 7z archive support
- Automatically sets file ownership and permissions
- Added safe "exit" option
- Sorting and De-Duplication of Console and Rom Lists, sorting alphabetically
- Overwrites files on extract, handles existing directories
- Shows download progress and handles keyboard interrupts
- Enhanced logging and error handling

<br>
---
<br>

## 👥 Credits & License

```
Copyright © 2018 Victor Oliveira <victor.oliveira@gmx.com>
Additional contributions © 2025 AloysiusAntioch

This work is free. You can redistribute it and/or modify it under the terms of the
Do What The Fuck You Want To Public License, Version 2, as published by Sam Hocevar.
See http://www.wtfpl.net/about/ for details.
```

<br>
---
<br>

## ⚠️ Disclaimer

Use responsibly. Downloading ROMs may violate copyright law in your jurisdiction.  
This tool automates retrieval from a public site — it does not host or distribute ROMs itself.
