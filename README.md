# email2phonenumber
email2phonenumber is an OSINT tool that allows you to obtain a target's phone number just by having his email address.

For full details check: [https://www.martinvigo.com/email2phonenumber](https://www.martinvigo.com/email2phonenumber)

Demo: [https://www.youtube.com/watch?v=dfvqhDUn81s](https://www.youtube.com/watch?v=dfvqhDUn81s)

## Basic info
This tool helps automate discovering someone's phone number by abusing password reset design weaknesses and publicly available data. It supports 3 main functions:

* "scrape" - scrapes websites for phone number digits by initiating password reset using the target's email address
* "generate" - creates a list of valid phone numbers based on the country's Phone Numbering Plan publicly available information
* "bruteforce" - iterates over a list of phone numbers and initiates password reset on different websites to obtain associated masked emails and correlate it to the victim's one

## Setup
email2phonenumber was developed on Python 3.x

You will need couple 3rd party libraries: BeautifulSoup and requests. These can be easely installed with pip

```
pip install beautifulsoup4 requests
```

## Usage
Scrape websites for phone number digits
```
python email2phonenumber.py scrape -e target@email.com
```

Generate a dictionary of valid phone numbers based on a phone number mask
```
python email2phonenumber.py generate -m 555XXX1234 -o /tmp/dic.txt
```
Find target's phone number by resetting passwords on websites that do not alert the target using a phone number mask and proxies to avoid captchas and other abuse protections
```
python email2phonenumber.py bruteforce -m 555XXX1234 -e target@email.com -p /tmp/proxies.txt -q
```
## Authors
Martin Vigo - @martin_vigo - [martinvigo.com](https://www.martinvigo.com)
