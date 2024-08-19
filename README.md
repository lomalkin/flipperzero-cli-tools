# CLI tools for Flipper zero

## Install

* $ `sudo apt install python3 python3-venv python3-pip`
* $ `git clone https://github.com/lomalkin/flipperzero-cli-tools`
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

### Interactive CLI tool with screen streaming

```
./clipper.py <flipper_name or /dev/tty..>
```

### RPC Examples

**Command line arguments**

```./rpc.py <Flipper> [commands]```
* `Flipper` - name of your Flipper or full path to Flipper serial in your OS.
* `commands` - list of spaced short command aliases, see below:

### Command aliases
* `ok`, `bk`, `up`, `dn`, `lt`, `rt` - Key control:  Ok, Back, Up, Down, Left, Right
* `ping` - ping-pong
* `alert` - play built-in vibro-audio-visual alert
* `screen` - dump screen image to console
* `exit` - exit from RPC app
* `s1` - sleep for 1 sec between commands

#### Examples

1. Dump screenshot to console

```./rpc.py Lotak screen```

2. Run music_player app via keyboard from default state, wait 5 seconds and exit:

```./rpc.py Lotak ok dn dn dn dn dn dn dn dn ok dn ok dn ok s1 s1 s1 s1 s1 bk bk bk```

3. Play alert on your Flipper

```./rpc.py Lotak alert```
