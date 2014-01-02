# deviantart-dl

A feature-ritch script for downloading deviantART galleries or individual photos.
Tested on python 2.7.5 and Arch Linux
Requires Mechanize

***

### Install

I would suggest giving it it's own directory as artist directories will be created automatically when downloading.

Download and install [Mechanize](https://pypi.python.org/pypi/mechanize/)

### Running

Run from terminal with `python deviantart-dl.py`

On some systems (like Arch Linux) `python2 deviantart-dl.py`

If you choose not to log in, Mature images will be downloaded as thumbnails.

You only need to log in once, so use a throwaway account.

Unless it is the first run or you want to switch accounts just say `n` to `New Account? (y/n):`

`Enter artist:` is case insensitive

A message indicitates if the artist is found and how many pages he/she has in their gallery.

#### 1) Download all pages
This can take a while depending on gallery size and image quality
#### 2) Select pages
This will prompt you for a range of pages. Input can also be comma seperated.
Example:
1-4,6,8,11-24,28
#### 3) Select images page by page
You will again be prompted for a selection of pages.
Each page will be displayed one by one and you can enter the number next to the title of
the images you want in the same format as page numbers.
#### 4) Search for image
Search a user's gallery for an image and select which ones to download
#### 5) Choose different artist
Start Over
#### 6) Quit
Guess what this one does..

***
BleuCadet

jesset513@gmail.com