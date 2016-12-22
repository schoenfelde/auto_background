## Synopsis

Welcome to an automated way of setting and changing your background with Python. This currently has only been tested on Windows 10. If you would like to automate this process, you can use schtasks on the cmd line.

## Motivation

I created this as an effort to become more acquainted with python, and do something that seems fun.

## Installation

First install the required packages:

`python3 -m pip install -r requirements.txt`

Where python3 is the python 3 executable. 

To get access to reddit go to [Reddit's Api Page](https://www.reddit.com/dev/api/) and create an account. When you have registered a new client application, enter your new credentials in reddit.py.

Then you can run the program with:

`python3 change_background.py`

Tools for automating the process: 

[Configuring a windows task to run a Python script](https://blogs.esri.com/esri/arcgis/2013/07/30/scheduling-a-scrip/)

## Tests

Will be added later.

## License

This code is available under the MIT license