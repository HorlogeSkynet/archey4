# Archey 4

> Archey is a simple system information tool written in Python

<p align="center">
	<!-- GITHUB & TRAVIS CI -->
	<a href="https://github.com/HorlogeSkynet/archey4/releases/latest"><img src="https://img.shields.io/github/release/HorlogeSkynet/archey4.svg?style=for-the-badge"></a>
	<a href="https://travis-ci.org/HorlogeSkynet/archey4"><img src="https://img.shields.io/travis/HorlogeSkynet/archey4/master.svg?style=for-the-badge"></a>
	<a href="https://github.com/HorlogeSkynet/archey4/commits/master"><img src="https://img.shields.io/github/last-commit/HorlogeSkynet/archey4.svg?style=for-the-badge"></a>
	<br />
	<!-- AUR -->
	<a href="https://aur.archlinux.org/packages/archey4/"><img src="https://img.shields.io/aur/version/archey4.svg?style=for-the-badge"></a>
	<a href="https://aur.archlinux.org/packages/archey4/"><img src="https://img.shields.io/aur/license/archey4.svg?style=for-the-badge"></a>
	<a href="https://aur.archlinux.org/packages/archey4/"><img src="https://img.shields.io/aur/votes/archey4.svg?style=for-the-badge"></a>
	<a href="https://aur.archlinux.org/packages/archey4/"><img src="https://img.shields.io/aur/last-modified/archey4.svg?style=for-the-badge"></a>
	<br />
	<!-- PYPI -->
	<a href="https://pypi.org/project/archey4/"><img src="https://img.shields.io/pypi/v/archey4.svg?style=for-the-badge"></a>
	<a href="https://pypi.org/project/archey4/"><img src="https://img.shields.io/pypi/pyversions/archey4.svg?style=for-the-badge"></a>
	<a href="https://pypi.org/project/archey4/"><img src="https://img.shields.io/pypi/dm/archey4?style=for-the-badge"></a>
</p>

<p align="center">
	<img alt="Archey4" src="https://blog.samuel.domains/img/blog/the-archey-project-what-i-ve-decided-to-do.png?v4.7.0">
</p>

## Why (again) a f\*cking new Archey fork ?

The answer is [here](https://blog.samuel.domains/archey4).

> Note : Since the 21st September of 2017, you may notice that this repository no longer has the official status of fork.  
> Actually, the maintainer decided to separate it from the original one's "network" with the help of _GitHub_'s staff.  
> Nevertheless, **this piece of software is still a fork of [djmelik's Archey project](https://github.com/djmelik/archey.git)**.

## Features

* Run as quickly as possible
* Stay as light as possible
* Keep entries ordered despite parallelism
* Extensive local IP addresses detection
* General temperature detection
* JSON output
* Screen capture ("best effort")

## Which packages do I need to run this project ?

### Required packages

* `python3`
* `python3-distro` (`python-distro` on Arch Linux)
* `python3-netifaces` (`python-netifaces` on Arch Linux)
* `procps` (`procps-ng` on Arch Linux)

> PyPy is supported and may replace CPython.

### Highly recommended packages

|     Environments      |             Packages              |                       Reasons                        |            Notes             |
| :-------------------- | :-------------------------------- | :--------------------------------------------------- | :--------------------------- |
| All                   | `dnsutils` (maybe `bind-tools`)   | **WAN\_IP** would be detected faster                 | Would provide `dig`          |
| All                   | `lm-sensors` (maybe `lm_sensors`) | **Temperature** would be more accurate               | N/A                          |
| Graphical (desktop)   | `pciutils`                        | **GPU** wouldn't be detected without it              | Would provide `lspci`        |
| Graphical (desktop)   | `wmctrl`                          | **WindowManager** would be more accurate             | N/A                          |
| Virtual w/o `systemd` | `virt-what` and `dmidecode`       | **Model** would contain details about the hypervisor | **root** privileges required |

## Installation

### Install from package

First, grab a package for your distribution from the latest release [here](https://github.com/HorlogeSkynet/archey4/releases/latest).  
Now, it's time to use your favorite package manager. Some examples :

* Arch-based distributions : `pacman -U ./archey4-4.Y.Z-R-any.pkg.tar.xz`
* Debian-based distributions : `apt install ./archey4_4.Y.Z-R_all.deb`
* RPM-based distributions : `dnf install ./archey4-4.Y.Z-R.py??.noarch.rpm`

**Note to Debian 8 (Jessie) users** : As [`python3-distro`](https://tracker.debian.org/pkg/python-distro) is not available in your repositories, **you should opt for an [installation from PyPI](#install-from-pypi).**

Further information about packaging are available [here](https://github.com/HorlogeSkynet/archey4/wiki/Packaging).

### Install from [PyPI](https://pypi.org/project/archey4/)

```bash
sudo pip3 install archey4
```

### Install from [AUR](https://aur.archlinux.org/packages/archey4/)

```bash
sudo yay -S archey4
```

### Install from source

```bash
### Step 1 : Fetch the source ###

# If you want the latest release :
LATEST_VERSION="v4.8.1"
wget "https://github.com/HorlogeSkynet/archey4/archive/${LATEST_VERSION}.tar.gz"
tar xvzf "${LATEST_VERSION}.tar.gz"
cd "archey4-${LATEST_VERSION}/"
# _______________________________

# If you want the latest changes :
git clone https://github.com/HorlogeSkynet/archey4.git
cd archey4/
# _______________________________


### Step 2 : Installation ###

# If you have PIP installed on your system :
sudo pip3 install .
# _________________________________________

# But if you don't have PIP, no worries :
sudo python3 setup.py install
# _______________________________________

### Step 3 (Optional) : Configuration files

# System-wide configuration :
sudo mkdir /etc/archey4
sudo cp archey/config.json /etc/archey4/config.json
# ___________________________
# User-specific configuration :
mkdir ~/.config/archey4
cp archey/config.json ~/.config/archey4/config.json
# _____________________________

### Step 4 (Optional) : I want a standalone script, as before !

# You can go through StickyTape for this :
sudo pip3 install stickytape
stickytape \
	--copy-shebang \
	--add-python-path . \
	--output-file dist/archey \
	archey/__main__.py
chmod +x dist/archey
./dist/archey
# ________________________________________

# You can either use PyInstaller :
sudo pip3 install pyinstaller
pyinstaller \
	--distpath dist \
	--specpath dist \
	--name archey \
	--onefile archey/__main__.py
./dist/archey
# ________________________________

# You can now move this script anywhere, as before :
sudo mv dist/archey /usr/local/bin/
# __________________________________________________
```

## Usage

```bash
archey --help
```

or if you only want to try this out (for instance, from source) :

```bash
python3 -m archey --help
```

## Configuration (optional)

Since v4.3.0, Archey 4 **may** be "tweaked" a bit with external configuration.  
You can place a [`config.json`](archey/config.json) file in these locations :

1. `/etc/archey4/config.json` (system preferences)
2. `~/.config/archey4/config.json` (user preferences)
3. `./config.json` (local preferences)

**If an option is defined in multiple places, it will be overridden according to the order above (local preferences > user preferences > system preferences).**

The [example file](archey/config.json) provided in this repository lists exhaustively the parameters you can set.  
Below stand further descriptions for each available option :

<!-- We use JavaScript syntax coloration below because JSON does not allow the usage of comments in it -->
```javascript
{
	// If set to `false`, configurations defined afterwards won't be loaded.
	// Developers running Archey from the original project may keep in there the original `config.json` while having their own external configuration set elsewhere.
	"allow_overriding": true,
	// Set to `false` to disable multi-threaded loading of entries.
	"parallel_loading": true,
	// If set to `true`, any execution warning or error would be hidden.
	// It may not apply to configuration parsing warnings.
	"suppress_warnings": false,
	"entries": {
		// Set to `false` each entry you want to mask.
	},
	"colors_palette": {
		// Leave this option set to `true` to display a beautiful colors palette.
		// Set it to `false` to allow compatibility with non-Unicode locales.
		"use_unicode": true,
		// Set this option to `false` to force Archey to use its own colors palettes.
		// `true` by default to honor `os-release`'s `ANSI_COLOR` option.
		"honor_ansi_color": true
	},
	"disk": {
		// Which filesystems to show:
		// `["local"]` shows only local filesystems.
		// You can alternatively list specific filesystems as:
		//  * A list of device paths - e.g. `["/dev/sda1", "/dev/nvme0n1p1"]`
		//  * A list of mount points - e.g. `["/", "/mnt"]`
		//  * A combination of the above - e.g. `["/", "/dev/sda2"]`
		"show_filesystems": ["local"],
		// Set to `false` to write each filesystem on its own line.
		"combine_total": true,
		// Defines which labels to use for each disk (only works if `combine_total` is false!)
		// The options available are:
		//  * `"mount_points"`: Shows the mount point of the filesystem.
		//      e.g. `Disk (/): 10.0 GiB/100.0 GiB`
		//           `Disk (/mnt): 15.0 GiB / 200.0 GiB`
		//  * `"device_paths"`: Shows the device path of the filesystem.
		//      e.g. `Disk (/dev/sda1): 10.0 GiB / 100.0 GiB`
		//           `Disk (/dev/mmcblk0p1): 15.0 GiB / 200.0 GiB`
		//  * `false` or `null` (no quote marks!): Don't show any device labels.
		//      e.g. `Disk: 10.0 GiB / 100.0 GiB`
		//           `Disk: 15.0 GiB / 200.0 GiB`
		"disk_labels": null,
		// Set to `true` to hide the "Disk" entry name from the output.
		// i.e. null  --> `Disk (/):`
		//      false --> `Disk (/):`
		//      true  --> `(/):`
		"hide_entry_name": null
	},
	"default_strings": {
		// Use this section to override default strings.
	},
	"ip_settings": {
		// The maximum number of local addresses you want to display.
		// `false` --> Unlimited.
		"lan_ip_max_count": 2,
		// `false` would make Archey display IPv4 LAN addresses only.
		"lan_ip_v6_support": true,
		// `false` would make Archey display IPv4 WAN addresses only.
		"wan_ip_v6_support": true
	},
	"gpu": {
		// Display GPUs on multiple lines if set to `false`.
		"one_line": true,
		// The maximum number of GPUs you want to display.
		// `false` --> Unlimited.
		"max_count": 2
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
		"sensors_chipsets": [
			// White-list of chipset identifiers (strings) passed to LM-SENSORS when computing the average temperature.
			// Uses `sensors -A` to list the available chipsets on your system (e.g. `coretemp-isa-0000`, `acpitz-acpi-0`, ...).
			// Leaving empty (default) would make Archey process input data from each existing chipset.
			// Use this option if a sensor happens to return irrelevant values, or if you want to exclude it.
		],
		// Display temperature values in Fahrenheit instead of Celsius.
		"use_fahrenheit": false
	},
	"timeout": {
		// Some values you can adjust if the default ones look undersized for your system (seconds).
	}
}
```

## Test cases

An extensive tests suite is available.  
Here is a short procedure to run them (you'll only need `python3`) :

```bash
git clone https://github.com/HorlogeSkynet/archey4.git
cd archey4/
# If you got `setuptools` installed
python3 setup.py test
# But if you don't, no worries !
python3 -m unittest
```

Any improvement would be appreciated.

## Notes to users

* If you experience any trouble during the installation or usage, please do **[open an issue](https://github.com/HorlogeSkynet/archey4/issues/new)**.

* If you had to tweak this project to make it work on your system, please **[open a pull request](https://github.com/HorlogeSkynet/archey4/pulls)** so as to share your modifications with the rest of the world and participate in this project ! You should also check [Info for contributors](https://github.com/HorlogeSkynet/archey4/wiki/Info-for-contributors).

* If your distribution is not (currently) supported, please check [How do I add a distribution to Archey?](https://github.com/HorlogeSkynet/archey4/wiki/How-do-I-add-a-distribution-to-Archey%3F).

* When looking up your public IP address (**WAN\_IP**), Archey will try at first to run a DNS query for `myip.opendns.com`, against OpenDNS's resolver(s). On error, it would fall back on regular HTTPS request(s) to <https://ident.me> ([server sources](https://github.com/pcarrier/identme)).
