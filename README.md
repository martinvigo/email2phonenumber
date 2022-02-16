# email2phonenumber
email2phonenumber is an OSINT tool that allows you to obtain a target's phone number just by having his email address.

For full details check: [https://www.martinvigo.com/email2phonenumber](https://www.martinvigo.com/email2phonenumber)

Demo: [https://www.youtube.com/watch?v=dfvqhDUn81s](https://www.youtube.com/watch?v=dfvqhDUn81s)

***IMPORTANT:*** *email2phonenumber is a proof-of-concept tool I wrote during my research on new OSINT methodologies to obtain a target's phone number. The supported services (Ebay, Lastpass, Amazon and Twitter) have long added protections to protect from these type of scraping like having to receive a code over email first or simply adding captchas. There are of course many other sites that are still leaking phone number digits but I am focused on other research projects. Feel free to submit pull request if you want to add support for new sites.

Please check out my newer tool "[Phonerator](https://www.martinvigo.com/tools/phonerator/)", which is maintained and focuses on the novel aspect of this research, generating valid phone numbers. 
[See more details](https://www.martinvigo.com/phonerator-an-advanced-valid-phone-number-generator/). There is also a small OSINT challenge in there... ;)

## Basic info
This tool helps automate discovering someone's phone number by abusing password reset design weaknesses and publicly available data. It supports 3 main functions:

* "scrape" - scrapes websites for phone number digits by initiating password reset using the target's email address
* "generate" - creates a list of valid phone numbers based on the country's Phone Numbering Plan publicly available information
* "bruteforce" - iterates over a list of phone numbers and initiates password reset on different websites to obtain associated masked emails and correlate it to the victim's one

## Setup
email2phonenumber was developed on Python 3.x

You will need couple 3rd party libraries: BeautifulSoup and requests. These can be easily installed with pip

```
pip3 install beautifulsoup4 requests
```

## Usage
Scrape websites for phone number digits
```
python3 email2phonenumber.py scrape -e target@email.com
```

Generate a dictionary of valid phone numbers based on a phone number mask
```
python3 email2phonenumber.py generate -m 555XXX1234 -o /tmp/dic.txt
```
Find target's phone number by resetting passwords on websites that do not alert the target using a phone number mask and proxies to avoid captchas and other abuse protections
```
python3 email2phonenumber.py bruteforce -m 555XXX1234 -e target@email.com -p /tmp/proxies.txt -q
```

## Demo video
[![email2phonenumber demo video](https://img.youtube.com/vi/dfvqhDUn81s/0.jpg)](https://www.youtube.com/watch?v=dfvqhDUn81s)

## Tool presentation at BSides Las Vegas 2019
[![Tool presentation at Bsides Las Vegas 2019](https://img.youtube.com/vi/1zssBR85vDA/0.jpg)](https://www.youtube.com/watch?v=1zssBR85vDA)

## Authors
Martin Vigo - @martin_vigo - [martinvigo.com](https://www.martinvigo.com)
