# CLI tools for Flipper zero

## Install

* $ `sudo apt install python3 python3-venv python3-pip`
* $ `git clone https://github.com/lomalkin/flipperzero-cli-tools`
* $ `cd flipper-cli-tools`
* $ `python3 -m venv venv`
* $ `pip install -r requirements.txt`

## Usage

* $ `. venv/bin/activate` - to activate python virtual environment
* $ `deactivate` - to deactivate

### Tools

* `./screen /dev/tty<path to Flipper serial>` - Make screenshot directly to console and save to `screen.png`
