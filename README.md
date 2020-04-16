# Archey 4

> Archey is a simple system information tool written in Python

<p align="center">
	<!-- TRAVIS CI -->
	<a href="https://travis-ci.org/HorlogeSkynet/archey4"><img src="https://img.shields.io/travis/HorlogeSkynet/archey4/master.svg?style=for-the-badge"></a>
	<br />
	<!-- GITHUB -->
	<a href="https://github.com/HorlogeSkynet/archey4/releases/latest"><img src="https://img.shields.io/github/release/HorlogeSkynet/archey4.svg?style=for-the-badge"></a>
	<a href="https://github.com/HorlogeSkynet/archey4/commits/master"><img src="https://img.shields.io/github/last-commit/HorlogeSkynet/archey4.svg?style=for-the-badge"></a>
	<br />
	<a href="https://github.com/HorlogeSkynet/archey4/issues"><img src="https://img.shields.io/github/issues/HorlogeSkynet/archey4.svg?style=for-the-badge"></a>
	<a href="https://github.com/HorlogeSkynet/archey4/pulls"><img src="https://img.shields.io/github/issues-pr/HorlogeSkynet/archey4.svg?style=for-the-badge"></a>
	<br />
	<!-- AUR -->
	<a href="https://aur.archlinux.org/packages/archey4/"><img src="https://img.shields.io/aur/version/archey4.svg?style=for-the-badge"></a>
	<a href="https://aur.archlinux.org/packages/archey4/"><img src="https://img.shields.io/aur/votes/archey4.svg?style=for-the-badge"></a>
	<a href="https://aur.archlinux.org/packages/archey4/"><img src="https://img.shields.io/aur/license/archey4.svg?style=for-the-badge"></a>
	<br />
	<!-- PYPI -->
	<a href="https://pypi.org/project/archey4/"><img src="https://img.shields.io/pypi/v/archey4.svg?style=for-the-badge"></a>
	<a href="https://pypi.org/project/archey4/"><img src="https://img.shields.io/pypi/pyversions/archey4.svg?style=for-the-badge"></a>
	<a href="https://pypi.org/project/archey4/"><img src="https://img.shields.io/pypi/dm/archey4?style=for-the-badge"></a>
	<a href="https://pypi.org/project/archey4/"><img src="https://img.shields.io/pypi/wheel/archey4.svg?style=for-the-badge"></a>
</p>

![archey4](https://blog.samuel.domains/img/blog/the-archey-project-what-i-ve-decided-to-do.png?v4.7.0)

## Why (another) new f\*cking Archey fork?

The answer is [here](https://blog.samuel.domains/archey4).

> Note: Since the 21st September 2017, you may notice that this repository no longer has the official status of fork.  
> The maintainer actually decided to separate it from the original one's "network" with the help of _GitHub_'s staff.  
> Nevertheless, **this piece of software is still a fork of [djmelik's Archey project](https://github.com/djmelik/archey.git)**.

## Installation

### **:warning: Before continuing**

* **Debian Jessie** users: The `python3-distro` module is not available in the repositories, you should opt for an [installation from PIP](#install-with-pip).

* Users in **virtual environments**: The `virt-what` call will be skipped if `systemd` tools are available on your system.

### Required packages

* `python3`
* `python3-distro` (`python-distro` on Arch Linux)
* `python3-netifaces` (`python-netifaces` on Arch Linux)
* `procps` (`procps-ng` on Arch Linux)

### Highly recommended packages

| Environments |  Packages  |                Reason                | Notes |
| :----------- | :--------: | :----------------------------------: | :---: |
| All          | `dnsutils` or `bind-tools` | Faster detection of WAN IP | Provides `dig` |
| All          | `lm-sensors` or `lm_sensors` | Possibly more accurate Temperature | φ |
| Graphical    | `pciutils` | **Required for GPU detection** | Provides `lspci` |
| Graphical    | `wmctrl` | Possibly more accurate Window Manager detection | φ |
| Virtual      | `virt-what` and `dmidecode` | **Hypervisor details** included in Model. | **Root** required |

### Install via package

First, grab a package for your distribution from the latest release [here](https://github.com/HorlogeSkynet/archey4/releases/latest).  
Now, it's time to use your favorite package manager. Some examples:

* Arch-based distributions : `pacman -U ./archey4-v4.Y.Z-R-any.pkg.tar.xz`
  * Or use the official package [in the AUR](https://aur.archlinux.org/packages/archey4/).
* Debian-based distributions : `apt install ./archey4_v4.Y.Z-R-all.deb`
* RPM-based distributions : `dnf install ./archey4-4.Y.Z-R.noarch.rpm`

### Install with PIP

```shell
$ sudo pip3 install archey4
```

### Install from source

```shell
### Step 1: Fetch the source ###

# If you want the latest release:
$ wget https://github.com/HorlogeSkynet/archey4/archive/v4.7.0.tar.gz
$ tar xvzf v4.7.0.tar.gz
$ cd archey4-4.7.0/
# _______________________________

# If you want the latest changes:
$ git clone https://github.com/HorlogeSkynet/archey4.git
$ cd archey4/
# _______________________________


### Step 2: Installation ###

# If you have PIP installed on your system:
$ sudo pip3 install .
# This allows uninstallation as follows:
$ sudo pip3 uninstall archey4
# _________________________________________

# If you don't have PIP:
$ sudo python3 setup.py install
# _______________________________________

### Step 3: Configuration files
### A configuration file is *required* to run Archey v4.7.1+.

# System-wide configuration:
$ sudo mkdir /etc/archey4
$ sudo cp archey/config.json /etc/archey4/config.json
# ___________________________
# User-specific configuration:
$ mkdir ~/.config/archey4
$ cp archey/config.json ~/.config/archey4/config.json
# _____________________________

### Step 4 (Optional): Standalone script (like the original Archey)

# You can go through StickyTape for this:
$ sudo pip3 install stickytape
$ stickytape --add-python-path . --output-file dist/archey archey/__main__.py
$ python3 dist/archey
# ________________________________________

# You can either use PyInstaller:
$ sudo pip3 install pyinstaller
$ pyinstaller --distpath dist --specpath dist --name archey --onefile archey/__main__.py
$ ./dist/archey
# ________________________________

# You can now move this script anywhere, as before:
$ chmod +x dist/archey
$ sudo mv dist/archey /usr/local/bin/
# __________________________________________________
```

## Usage

```shell
$ archey
```

or, if you only want to try this out (for instance, from source):

```shell
$ python3 -m archey
```

## Configuration

Since v4.3.0, Archey 4 **may** be "tweaked" a bit with external configuration.
Since v4.7.1, Archey 4 **must** have a configuration file present in one of the possible locations listed below.

Place a [config.json](archey/config.json) file in one of these locations:

1. `/etc/archey4/config.json` (system preferences)
2. `~/.config/archey4/config.json` (user preferences)
3. `./config.json` (local preferences)

**If a configuration file is present in more than one of these locations, it will be overridden according to the order above (local preferences > user preferences > system preferences).**

The [example file](archey/config.json) provided in this repository lists exhaustively the parameters you can set.  
Below are explanations of each option available (please note that the configuration file **cannot** contain the comments written below):

<!-- We use JavaScript syntax coloration below because JSON does not support comments -->

```javascript
{
	// Redirects stderr to null if set to true, hiding all execution errors and warnings.
	// Configuration load errors may still show if they occur before the configuration is loaded.
	"suppress_warnings": false,
	// Place a list of all modules that you wish to run in this section.
	// They appear in the output in the order specified.
	// "display_text" controls the label printed for each entry
	// e.g. "display_text": "Hi" will print "Hi: {entry information}"
	"entries": {
		// Shows the logged in user's username.
		"User": {
			"display_text": "User"
		},
		// Shows the hostname of the computer.
		"Hostname": {
			"display_text": "Hostname"
		},
		// Shows the model of the computer based on some heuristics.
		"Model": {
			"display_text": "Model",
			// What to show if a virtual environment is detected.
			"virtual_environment_string": "Virtual Environment"
		},
		// Shows the distro currently running.
		"Distro": {
			"display_text": "Distro"
		},
		// Shows the kernel version currently running.
		"Kernel": {
			"display_text": "Kernel"
		},
		// Shows the current uptime.
		"Uptime": {
			"display_text": "Uptime"
		},
		// Shows the window manager currently running.
		"WindowManager": {
			"display_text": "Window Manager"
		},
		// Shows the desktop environment currently running.
		"DesktopEnvironment": {
			"display_text": "Desktop Environment"
		},
		// Shows the shell detected in which archey is running.
		"Shell": {
			"display_text": "Shell"
		},
		// Shows the terminal (emulator) detected in which archey is running.
		"Terminal": {
			"display_text": "Terminal"
		},
		// Shows the number of installed packages detected via the package manager.
		"Packages": {
			"display_text": "Packages"
		},
		// Shows the current and max CPU temperature.
		"Temperature": {
			"display_text": "Temperature",
			// Display a character before the unit (e.g. the degree symbol)
			"char_before_unit": " ",
			// Convert temperatures to degrees fahrenheit.
			"use_fahrenheit": false
		},
		// Shows the model and speed of the CPU in the system.
		"CPU": {
			"display_text": "CPU"
		},
		// Shows the model of GPU installed in the system.
		"GPU": {
			"display_text": "GPU"
		},
		// Shows the used and total amount of memory in the system.
		"RAM": {
			"display_text": "RAM",
			// Set warnings for memory usage (as percentages used).
			"usage_warnings": {
				// Warning level (orange text)
				"warning": 33.3,
				// Danger level (red text)
				"danger": 66.7
			}
		},
		// Shows the aggregate used and total disk space in the system.
		"Disk": {
			"display_text": "Disk",
			// Set warnings for disk usage (as percentages used).
			"usage_warnings": {
				"warning": 50,
				"danger": 75
			}
		},
		// Shows detected LAN IP addresses.
		"LanIp": {
			"display_text": "LAN IP",
			// Maximum number of IP addresses to display.
			"max_count": 2,
			// If true, try and detect IPv6 addresses.
			"ipv6_support": true
		},
		// Shows detected WAN IP addresses.
		// Warning: This entry contacts external servers!
		"WanIp": {
			"display_text": "WAN IP",
			// If true, try and detect IPv6 addresses.
			"ipv6_support": true,
			// Timeout (in seconds) for detecting the IPv4 address.
			"ipv4_timeout_secs": 1.0,
			// Timeout (in seconds) for detecting the IPv6 address.
			"ipv6_timeout_secs": 1.0
		}
	},
	"colors_palette": {
		// Display the colour blocks using unicode.
		// This is disabled by default for compatibility with non-unicode locales.
		"use_unicode": false
	},
	// These default strings are used when entries do not detect things.
	// They can be customised here.
	"default_strings": {
		"no_address": "No Address",
		"not_detected": "Not detected",
	}
}
```

## Test cases

Tests are now available. Here is a short procedure to run them (you'll only need `python3`):

```shell
$ git clone https://github.com/HorlogeSkynet/archey4.git
$ cd archey4/
# If you have `setuptools` installed
$ python3 setup.py test
# But if you haven't, no worries!
$ python3 -m unittest
```

Any improvement would be appreciated.

## Notes to users

* If you run `archey` as root, the script will list the processes running by other users on your system in order to display the **Window Manager** & **Desktop Environment** outputs correctly.

* During the setup procedure, it was advised to copy this script into the `/usr/local/bin/` folder. You may want to check the source beforehand.

* If you experience any trouble during the installation or usage, please do **[open an issue](https://github.com/HorlogeSkynet/archey4/issues/new)**.

* If you had to adapt the script to make it work on your system, please **[open a pull request](https://github.com/HorlogeSkynet/archey4/pulls)** so as to share your modifications with the rest of the world and participate in this project!

* When looking up your public IP address (**WanIp**), Archey will try at first to run a DNS query for `myip.opendns.com`, against OpenDNS's resolver(s). On error, it would fall back on regular HTTPS request(s) to <https://ident.me> ([server sources](https://github.com/pcarrier/identme)).

## Notes about packaging

At the moment, [assets published on GitHub](https://github.com/HorlogeSkynet/archey4/releases/latest) are currently built with the `packaging/build.sh` script (a wrapper to [FPM](https://github.com/jordansissel/fpm), [Setuptools](https://github.com/pypa/setuptools) and [Twine](https://github.com/pypa/twine)).

PIP source and wheel distributions (as long as Debian packages since v4.7.0) are GPG-signed using [this key](https://github.com/HorlogeSkynet.gpg).  
Wheels (and their signatures) are uploaded on GitHub too, whereas source distributions could be watched [here](https://pypi.debian.net/archey4/).

For the Arch Linux community, [an official package is (still) maintained in the AUR](https://aur.archlinux.org/packages/archey4/).
