# Archey 4

> Archey is a simple system information tool written in Python

<p align="center">
	<!-- TRAVIS CI -->
	<a href="https://travis-ci.org/HorlogeSkynet/archey4"><img src="https://img.shields.io/travis/HorlogeSkynet/archey4/master.svg?style=for-the-badge"></a>
	<br />
	<!-- GITHUB -->
	<a href="https://github.com/HorlogeSkynet/archey4/issues"><img src="https://img.shields.io/github/issues/HorlogeSkynet/archey4.svg?style=for-the-badge"></a>
	<a href="https://github.com/HorlogeSkynet/archey4/pulls"><img src="https://img.shields.io/github/issues-pr/HorlogeSkynet/archey4.svg?style=for-the-badge"></a>
	<br />
	<a href="https://github.com/HorlogeSkynet/archey4/releases/latest"><img src="https://img.shields.io/github/release/HorlogeSkynet/archey4.svg?style=for-the-badge"></a>
	<a href="https://github.com/HorlogeSkynet/archey4/commits/master"><img src="https://img.shields.io/github/last-commit/HorlogeSkynet/archey4.svg?style=for-the-badge"></a>
	<br />
	<!-- AUR -->
	<a href="https://aur.archlinux.org/packages/archey4/"><img src="https://img.shields.io/aur/version/archey4.svg?style=for-the-badge"></a>
	<a href="https://aur.archlinux.org/packages/archey4/"><img src="https://img.shields.io/aur/votes/archey4.svg?style=for-the-badge"></a>
	<a href="https://aur.archlinux.org/packages/archey4/"><img src="https://img.shields.io/aur/license/archey4.svg?style=for-the-badge"></a>
	<br />
	<!-- PYPI -->
	<a href="https://pypi.org/project/archey4/"><img src="https://img.shields.io/pypi/v/archey4.svg?style=for-the-badge"></a>
	<a href="https://pypi.org/project/archey4/"><img src="https://img.shields.io/pypi/wheel/archey4.svg?style=for-the-badge"></a>
	<a href="https://pypi.org/project/archey4/"><img src="https://img.shields.io/pypi/pyversions/archey4.svg?style=for-the-badge"></a>
</p>

![archey4](https://blog.samuel.domains/img/blog/the-archey-project-what-i-ve-decided-to-do.png?v4.7.0)

## Why (again) a f\*cking new Archey fork ?

The answer is [here](https://blog.samuel.domains/archey4).

> Note : Since the 21st September of 2017, you may notice that this repository no longer has the official status of fork.  
> Actually, the maintainer decided to separate it from the original one's "network" with the help of _GitHub_'s staff.  
> Nevertheless, **this piece of software is still a fork of [djmelik's Archey project](https://github.com/djmelik/archey.git)**.

## Which packages do I need to run this script ?

### Required packages

* `python3`
* `python3-distro` (`python-distro` on Arch Linux)
* `python3-netifaces` (`python-netifaces` on Arch Linux)
* `procps` (`procps-ng` on Arch Linux)

### Highly recommended packages

| Environments |  Packages  |                Reasons                | Notes |
| :----------- | :--------: | :-----------------------------------: | :---: |
| All          | `dnsutils` or `bind-tools` | **WAN\_IP** would be detected faster | Would provide `dig` |
| All          | `lm-sensors` or `lm_sensors` | **Temperature** would be more accurate | φ |
| Graphical    | `pciutils` | **GPU** wouldn't be detected without it | Would provide `lspci` |
| Graphical    | `wmctrl` | **WindowManager** would be more accurate | φ |
| Virtual      | `virt-what` and `dmidecode` | **Model** would contain details about the hypervisor | `archey` would have to be run as **root** |

### :warning: Various notes to read before going down :warning:

* **Note to Debian Jessie users : As `python3-distro` module is not available in your repositories, you should opt for an [installation from PIP](#install-with-pip).**

* **`virt-what` call will be skipped if `systemd` tools are available on your system.**

## Installation

### Install from package

First, grab a package for your distribution from the latest release [here](https://github.com/HorlogeSkynet/archey4/releases/latest).  
Now, it's time to use your favorite package manager. Some examples :

* Arch-based distributions : `pacman -U ./archey4-v4.Y.Z-R-any.pkg.tar.xz`
* Debian-based distributions : `apt install ./archey4_v4.Y.Z-R-all.deb`
* RPM-based distributions : `dnf install ./archey4-4.Y.Z-R.noarch.rpm`

### Install with PIP

```shell
$ sudo pip3 install archey4
```

### Install from source

```shell
### Step 1 : Fetch the source ###

# If you want the latest release :
$ wget https://github.com/HorlogeSkynet/archey4/archive/v4.7.0.tar.gz
$ tar xvzf v4.7.0.tar.gz
$ cd archey4-4.7.0/
# _______________________________

# If you want the latest changes :
$ git clone https://github.com/HorlogeSkynet/archey4.git
$ cd archey4/
# _______________________________


### Step 2 : Installation ###

# If you have PIP installed on your system :
$ sudo pip3 install .
# So if one day you wanna uninstall Archey
$ sudo pip3 uninstall archey4
# _________________________________________

# But if you don't have PIP, no worries :
$ sudo python3 setup.py install
# _______________________________________

### Step 3 (Optional) : Configuration files

# System-wide configuration :
$ sudo mkdir /etc/archey4
$ sudo cp archey/config.json /etc/archey4/config.json
# ___________________________
# User-specific configuration :
$ mkdir ~/.config/archey4
$ cp archey/config.json ~/.config/archey4/config.json
# _____________________________

### Step 4 (Optional) : I want a standalone script, as before !

# You can go through StickyTape for this :
$ sudo pip3 install stickytape
$ stickytape --add-python-path . --output-file dist/archey archey/__main__.py
$ python3 dist/archey
# ________________________________________

# You can either use PyInstaller :
$ sudo pip3 install pyinstaller
$ pyinstaller --distpath dist --specpath dist --name archey --onefile archey/__main__.py
$ ./dist/archey
# ________________________________

# You can now move this script anywhere, as before :
$ chmod +x dist/archey
$ sudo mv dist/archey /usr/local/bin/
# __________________________________________________
```

## Usage

```shell
$ archey
```

or if you only want to try this out (for instance, from source) :

```shell
$ python3 -m archey
```

## Configuration (optional)

Since the version 4.3.0, Archey 4 **may** be "tweaked" a bit with external configuration.  
You can place a [`config.json`](archey/config.json) file in these locations :

1. `/etc/archey4/config.json` (system preferences)
2. `~/.config/archey4/config.json` (user preferences)
3. `./config.json` (local preferences)

**If an option is defined in multiple places, it will be overridden according to the order above (local preferences > user preferences > system preferences).**

The [example file](archey/config.json) provided in this repository lists exhaustively the parameters you can set.  
Below, some further explanations of each option available :

<!-- We use JavaScript syntax coloration below because JSON does not allow the usage of comments in it -->
```javascript
{
	// If set to `false`, configurations defined afterwards won't be loaded.
	// Developers running Archey from the original project may keep in there the original `config.json` while having their own external configuration set elsewhere.
	"allow_overriding": true,
	// If set to `true`, any execution warning or error would be hidden.
	// It may not apply to configuration parsing warnings.
	"suppress_warnings": false,
	"entries": {
		// Set to `false` each entry you want to mask.
	},
	"colors_palette": {
		// Set this option to `true` to display a beautiful colors palette.
		// `false` by default for backward compatibility with non-Unicode locales.
		"use_unicode": false
	},
	"default_strings": {
		// Use this section to override default strings.
	},
	"ip_settings": {
		// The maximum number of local addresses you want to display.
		// `false` --> Unlimited.
		"lan_ip_max_count": 2,
		// `false` would make Archey displays only IPv4 LAN addresses.
		"lan_ip_v6_support": true,
		// `false` would make Archey displays only IPv4 WAN addresses.
		"wan_ip_v6_support": true
	},
	"limits": {
		// Some threshold values you can adjust affecting disk/ram warning/danger color (percent).
		"ram": {
			"warning": 33.3,
			"danger": 66.7
		},
		"disk": {
			"warning": 50,
			"danger": 75
		}
	},
	"temperature": {
		// The character to display between the temperature value and the unit (as '°' in 53.2°C).
		// Set to ' ' (space) by default for backward compatibility with non-Unicode locales.
		"char_before_unit": " ",
		// Display temperature values in Fahrenheit instead of Celsius.
		"use_fahrenheit": false
	},
	"timeout": {
		// Some values you can adjust if the default ones look undersized for your system (seconds).
	}
}
```

## Test cases

Tests are now available. Here is a short procedure to run them (you'll only need `python3`) :

```shell
$ git clone https://github.com/HorlogeSkynet/archey4.git
$ cd archey4/
# If you got `setuptools` installed
$ python3 setup.py test
# But if you still don't, no worries !
$ python3 -m unittest
```

Any improvement would be appreciated.

## Notes to users

* If you run `archey` as root, the script will list the processes running by other users on your system in order to display the **Window Manager** & **Desktop Environment** outputs correctly.

* During the setup procedure, I advised you to copy this script into the `/usr/local/bin/` folder, you may want to check what it does beforehand.

* If you experience any trouble during the installation or usage, please do **[open an issue](https://github.com/HorlogeSkynet/archey4/issues/new)**.

* If you had to adapt the script to make it work on your system, please **[open a pull request](https://github.com/HorlogeSkynet/archey4/pulls)** so as to share your modifications with the rest of the world and participate in this project !

* When looking up your public IP address (**WAN\_IP**), Archey will try at first to run a DNS query for `myip.opendns.com`, against OpenDNS's resolver(s). On error, it would fall back on regular HTTPS request(s) to <https://ident.me> ([server sources](https://github.com/pcarrier/identme)).

## Notes to developers / maintainers

You might be interested in checking/running the `packaging/build.sh` script.
