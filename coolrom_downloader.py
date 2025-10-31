#!/usr/bin/python3

#Copyright © 2018 Victor Oliveira <victor.oliveira@gmx.com>
#This work is free. You can redistribute it and/or modify it under the
#terms of the Do What The Fuck You Want To Public License, Version 2,
#as published by Sam Hocevar. See the COPYING file for more details.
#Version 3 contributions © 2025 AloysiusAntioch

#Changelog:
#v3.0 - Major feature expansion by AloysiusAntioch
# * Added support for CLI arguments:
#     - --console / -c       : Select console by index
#     - --letter / -l        : Filter ROMs by first letter
#     - --search / -s        : Search for ROMs by substring
#     - --rom / -r           : Select one or more ROMs to download
#     - --output / -o        : Save and extract to custom path
#     - --clean / -C         : Delete archive after extraction
#     - --user / -u          : chown extracted files to user:user
#     - --perms / -p         : chmod extracted files (e.g. 755)
# * Added automatic archive extraction for:
#     - .zip, .tar, .tar.gz, .tgz, .gz, .7z formats
# * Installed and used external modules:
#     - py7zr (for .7z extraction)
# * Automatically overwrites files on extraction
# * Automatically applies user/group ownership and permissions
# * Added progress display and graceful keyboard interrupt handling
# * Improved error handling, formatting, and user experience
#v2.1 - Fixed HTTP error 401
#v2.0 - Rewritten from scratch in Python3
# * The parsing system uses proper Python3 module
# * It load supported consoles directly from the page
# * Uses only Python3 STDLIB (No need to install other modules)
#v1.0 - Written in BASH

import urllib.request as ur
import urllib.parse
from html.parser import HTMLParser
import os
import argparse
import string
import zipfile
import tarfile
import gzip
import shutil
import py7zr  # For .7z extraction

buffer_size = 1024 * 8

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = list()
        self.attrib = list()
        self.starttag = list()

    def handle_starttag(self, tag, attrib):
        if tag:
            self.starttag.append(tag)
        if attrib:
            self.attrib.append(attrib)

    def handle_data(self, data):
        data = data.strip()
        if data:
            self.data.append(data)

def _getHtml(url):
    req = ur.Request(url)
    req.add_header('User-Agent', 'Bla')
    req = ur.urlopen(req)
    html = req.read().decode()
    return html

def _getConsoles():
    url = 'http://coolrom.com.au/roms/'
    html_page = _getHtml(url)
    html_parser = MyHTMLParser()
    html_parser.feed(html_page)
    consoles = list()
    for line in html_parser.attrib:
        try:
            if 'roms' in line[0][1]:
                if len(line) == 1:
                    console_name = line[0][1].split('/')[2]
                    consoles.append(console_name)
        except:
            pass
    return consoles

def _getRomslist(console, letter):
    url = f'http://coolrom.com.au/roms/{console}/{letter}/'
    html_page = _getHtml(url)
    html_parser = MyHTMLParser()
    html_parser.feed(html_page)
    roms = dict()
    for line in html_parser.attrib:
        try:
            if 'roms' in line[0][1] and len(line) == 1 and 'php' in line[0][1]:
                rom = line[0][1]
                rom_link = rom
                rom_name = rom.split('/')[-1].split('.php')[0].replace('_', ' ')
                roms[rom_name] = rom_link
        except:
            pass
    return roms

def _downloadRom(rom_link, save_path='.', auto_clean=False, user=None, perms=None):
    rom_id = rom_link.split('/')[3]
    rom_name = rom_link.split('/')[-1].split('.php')[0].replace('_', ' ')
    console_name = rom_link.split('/')[2]
    url = f'http://coolrom.com.au/dlpop.php?id={rom_id}'
    html_page = _getHtml(url)
    html_parser = MyHTMLParser()
    html_parser.feed(html_page)
    html_parser.feed(''.join(html_parser.data))

    url_download = None
    for line in html_parser.attrib:
        try:
            if 'action' in line[1][0]:
                url_download = line[1][1]
                break
        except IndexError:
            pass

    if not url_download:
        print(f'[-] Could not find download URL for ROM: {rom_name}')
        return

    req_header = {'Referer': f'http://coolrom.com.au/{rom_link}', 'User-Agent': 'Bla'}
    req = ur.Request(url_download, headers=req_header)
    req = ur.urlopen(req)

    file_size = int(req.getheader('Content-Length'))
    file_name = req.getheader('Content-Disposition').split('=')[-1].strip('"')
    file_name = urllib.parse.unquote(file_name)

    os.makedirs(save_path, exist_ok=True)
    file_path = os.path.join(save_path, file_name)

    print(f'\nConsole: {console_name}')
    print(f'Rom: {rom_name}')
    print(f'File: {file_name}')
    print('File Size: {:.2f}MB'.format(file_size / 1000 / 1000))

    with open(file_path, 'wb') as file:
        i = 0
        try:
            while True:
                buffer = req.read(buffer_size)
                if buffer:
                    file.write(buffer)
                    i += 1
                    print('{:.1f}%'.format((i * buffer_size / file_size) * 100), end='\r')
                else:
                    break
        except KeyboardInterrupt:
            os.remove(file_path)
            print('Download cancelled.\nLeftover file deleted.')
            return

    print(f'\n[+] Download complete: {file_name}')

    # === Auto Extraction ===
    def extract_archive(archive_path, extract_to, user=None, perms=None):

        def apply_permissions_and_ownership(target_dir):
            for root, dirs, files in os.walk(target_dir):
                for dname in dirs:
                    path = os.path.join(root, dname)
                    if perms:
                        os.chmod(path, int(perms, 8))
                    if user:
                        shutil.chown(path, user=user, group=user)
                for fname in files:
                    path = os.path.join(root, fname)
                    if perms:
                        os.chmod(path, int(perms, 8))
                    if user:
                        shutil.chown(path, user=user, group=user)

        try:
            if file_name.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(path=extract_to)
                print(f'[+] Extracted ZIP to {extract_to}')
            elif file_name.endswith(('.tar.gz', '.tgz', '.tar')):
                with tarfile.open(archive_path, 'r:*') as tar:
                    tar.extractall(path=extract_to)
                print(f'[+] Extracted TAR to {extract_to}')
            elif file_name.endswith('.gz') and not file_name.endswith('.tar.gz'):
                extracted_file = os.path.splitext(file_name)[0]
                extracted_path = os.path.join(extract_to, extracted_file)
                with gzip.open(archive_path, 'rb') as f_in:
                    with open(extracted_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f'[+] Extracted GZ to {extract_to}')
            elif file_name.endswith('.7z'):
                with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                    archive.extractall(path=extract_to)
                print(f'[+] Extracted 7Z to {extract_to}')
            else:
                print('[*] Not a supported archive type. Skipping extraction.')
                return False

            apply_permissions_and_ownership(extract_to)
            return True

        except Exception as e:
            print(f'[-] Extraction failed: {e}')
            return False

    extracted = extract_archive(file_path, save_path, user=user, perms=perms)

    if extracted and auto_clean:
        try:
            os.remove(file_path)
            print(f'[\u2713] Cleaned up archive: {file_name}')
        except Exception as e:
            print(f'[!] Failed to delete archive: {e}')

def parse_args():
    parser = argparse.ArgumentParser(
        description='CoolROM Downloader - search, select, extract ROMs, and set permissions.'
    )
    parser.add_argument('-c', '--console', type=int,
                        help='Console number')
    parser.add_argument('-l', '--letter', type=str,
                        help='Filter ROMs by first letter')
    parser.add_argument('-s', '--search', type=str,
                        help='Search ROMs by substring')
    parser.add_argument('-r', '--rom', type=int, nargs='+',
                        help='ROM index(es) to download')
    parser.add_argument('-o', '--output', type=str,
                        help='Directory to save & extract ROMs')
    parser.add_argument('--clean', '-C', action='store_true',
                        help='Delete archive file after extraction')
    parser.add_argument('-u', '--user', type=str,
                        help='chown extracted files to user')
    parser.add_argument('-p', '--perms', type=str,
                        help='chmod extracted files recursively (e.g., 755)')
    return parser.parse_args()

# === MAIN START ===
if __name__ == '__main__':
    print('''
 ▄▄·             ▄▄▌  ▄▄▄        • ▌ ▄ ·.                                   
▐█ ▌▪▪     ▪     ██•  ▀▄ █·▪     ·██ ▐███▪                                  
██ ▄▄ ▄█▀▄  ▄█▀▄ ██▪  ▐▀▀▄  ▄█▀▄ ▐█ ▌▐▌▐█·                                  
▐███▌▐█▌.▐▌▐█▌.▐▌▐█▌▐▌▐█•█▌▐█▌.▐▌██ ██▌▐█▌                                  
·▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀ .▀  ▀ ▀█▄▀▪▀▀  █▪▀▀▀                                  
                ·▄▄▄▄        ▄▄▌ ▐ ▄▌ ▐ ▄ ▄▄▌         ▄▄▄· ·▄▄▄▄  ▄▄▄ .▄▄▄  
                ██▪ ██ ▪     ██· █▌▐█•█▌▐███•  ▪     ▐█ ▀█ ██▪ ██ ▀▄.▀·▀▄ █·
                ▐█· ▐█▌ ▄█▀▄ ██▪▐█▐▐▌▐█▐▐▌██▪   ▄█▀▄ ▄█▀▀█ ▐█· ▐█▌▐▀▀▪▄▐▀▀▄ 
                ██. ██ ▐█▌.▐▌▐█▌██▐█▌██▐█▌▐█▌▐▌▐█▌.▐▌▐█ ▪▐▌██. ██ ▐█▄▄▌▐█•█▌
                ▀▀▀▀▀•  ▀█▄▀▪ ▀▀▀▀ ▀▪▀▀ █▪.▀▀▀  ▀█▄▀▪ ▀  ▀ ▀▀▀▀▀•  ▀▀▀ .▀  ▀
                                CoolROM Downloader - v3
    ''')

    args = parse_args()

    print('\n== CONSOLE SELECT ==')
    consoles = _getConsoles()
    for idx, console in enumerate(consoles):
        print(f'{idx}) {console}')

    if args.console is not None and 0 <= args.console < len(consoles):
        console_selected = args.console
        print(f'\n[+] Console selected via CLI: ({consoles[console_selected]})')
    else:
        print('\nInput console number:')
        console_selected = int(input('> '))

    console_name = consoles[console_selected]
    roms_list = {}

    if args.search:
        print(f'\n[+] Searching for ROMs matching: "{args.search}"...')
        for letter in string.ascii_lowercase:
            roms = _getRomslist(console_name, letter)
            for name, link in roms.items():
                if args.search.lower() in name.lower():
                    roms_list[name] = link
        if not roms_list:
            print(f'\n[-] No ROMs found matching: "{args.search}"')
            exit(0)
    else:
        if args.letter and len(args.letter) == 1 and args.letter.isalpha():
            rom_letter = args.letter.lower()
            print(f'\n[+] ROM letter selected via CLI: {rom_letter}')
        else:
            print('\n== ROM SEARCH ==')
            print('\nInput rom letter:')
            rom_letter = input('> ')
        roms_list = _getRomslist(console_name, rom_letter)

    roms_names = list(roms_list.keys())

    print('\n== ROM SELECT ==')
    for idx, rom_name in enumerate(roms_names):
        print(f'{idx}) {rom_name}')

    selected_roms = []
    if args.rom:
        for r in args.rom:
            if 0 <= r < len(roms_names):
                selected_roms.append(r)
            else:
                print(f'[-] Ignoring invalid ROM index: {r}')
    else:
        print('\nInput rom number(s):')
        selected_roms = list(map(int, input('> ').split()))

    save_dir = args.output if args.output else '.'
    auto_clean = args.clean

    print('\n== ROM DOWNLOAD ==')
    for rom_index in selected_roms:
        rom_selected_name = roms_names[rom_index]
        _downloadRom(
            roms_list[rom_selected_name],
            save_dir,
            auto_clean,
            args.user,
            args.perms
        )
