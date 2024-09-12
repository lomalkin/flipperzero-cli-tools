# CLI tools for Flipper zero

## Install

* $ `sudo apt install python3 python3-venv python3-pip`
* $ `git clone https://github.com/fireostendere/clipper_windows`
* $ `cd flipper-cli-tools`
* $ `git submodule update --init --recursive`
* $ `python3 -m venv venv`
* $ `. venv/bin/activate`
* $ `pip install -r requirements.txt`
* $ `deactivate`

## Usage

**Preparing**

* $ `. venv/bin/activate` - to activate python virtual environment
* $ `deactivate` - to deactivate

### Interactive CLI tool with screen streaming with unicode

```
./clipper.py <flipper_name or /dev/tty..>
```

### Interactive CLI tool with screen streaming with braille

```
./clipper.py <flipper_name or /dev/tty..> braille
```

### Controls: Arrows - D-pad, Enter - OK, Backspace/Delete - BACK, key+shift - long press, Esc - quit
