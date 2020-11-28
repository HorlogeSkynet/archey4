# Archey 4

> Archey is a simple system information tool written in Python

<p align="center">
	<!-- GITHUB -->
	<a href="https://github.com/HorlogeSkynet/archey4/releases/latest"><img src="https://img.shields.io/github/release/HorlogeSkynet/archey4.svg?style=for-the-badge"></a>
	<a href="https://github.com/HorlogeSkynet/archey4/actions"><img src="https://img.shields.io/github/workflow/status/HorlogeSkynet/archey4/Integration/master.svg?style=for-the-badge"></a>
	<a href="https://github.com/HorlogeSkynet/archey4/commits"><img src="https://img.shields.io/github/last-commit/HorlogeSkynet/archey4.svg?style=for-the-badge"></a>
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
* Extensive local and public IP addresses detection
* General temperature detection
* JSON output
* Screen capture ("best effort")

## Which packages do I need to run this project ?

### Required packages

* `python3` (>= 3.5)
* `python3-distro` (`python-distro` on Arch Linux)
* `python3-netifaces` (`python-netifaces` on Arch Linux)
* `procps` (`procps-ng` on Arch Linux)

> PyPy is supported and may replace CPython.

> Looking for Python 3.4 support ? Please refer to the latest v4.9 release.

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

#### Step 1 : Fetch sources

```bash
# If you want the latest release :
LATEST_VERSION="v4.9.0"
wget "https://github.com/HorlogeSkynet/archey4/archive/${LATEST_VERSION}.tar.gz"
tar xvzf "${LATEST_VERSION}.tar.gz"
cd "archey4-${LATEST_VERSION}/"

# If you want the latest (stable) changes :
git clone https://github.com/HorlogeSkynet/archey4.git
cd archey4/
```

#### Step 2 : Installation

```bash
# If you have PIP installed on your system :
sudo pip3 install .

# But if you don't have PIP, no worries :
sudo python3 setup.py install
```

#### Step 3 (optional) : Configuration

```bash
# System-wide configuration file :
sudo mkdir /etc/archey4
sudo cp config.json /etc/archey4/config.json

# User-specific configuration file :
mkdir -p ~/.config/archey4
cp config.json ~/.config/archey4/config.json
```

#### Step 4 (optional) : Standalone building

> Some years ago, Archey was a simple and unique Python file.  
> Project evolved, and now it's a proper module.  
> Some procedures below walk you through several ways of building Archey as a standalone program.

```bash
# Using Stickytape :
sudo pip3 install stickytape
stickytape \
	--copy-shebang \
	--add-python-path . \
	--output-file dist/archey \
	archey/__main__.py
chmod +x dist/archey

# Using PyInstaller :
sudo pip3 install pyinstaller
pyinstaller \
	--distpath dist \
	--specpath dist \
	--name archey \
	--onefile archey/__main__.py

# Using PEX :
sudo pip3 install pex
pex \
	-o dist/archey \
	-m archey \
	.
```

Resulting program may now be installed system-wide.

```bash
# Execute program resulting from step 4.
./dist/archey

# You can now move this file for a system-wide install :
sudo mv dist/archey /usr/local/bin/
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
You can place a [`config.json`](config.json) file in these locations :

1. `/etc/archey4/config.json` (system preferences)
2. `~/.config/archey4/config.json` (user preferences)
3. `./config.json` (local preferences)

**If an option is defined in multiple places, it will be overridden according to the order above (local preferences > user preferences > system preferences).**

Alternatively, you may specify your own configuration file with the `-c` command-line option.

The [example file](config.json) provided in this repository lists exhaustively the parameters you can set.  
Below stand further descriptions for each available (default) option :

<!-- We use JavaScript syntax coloration below because JSON does not allow the usage of comments in it -->
```javascript
{
	// If set to `false`, configurations defined afterwards won't be loaded.
	// Developers running Archey from the original project may keep in there the original `config.json`,
	//   while having their own external configuration set elsewhere.
	"allow_overriding": true,
	// Set to `false` to disable multi-threaded loading of entries.
	"parallel_loading": true,
	// If set to `true`, any execution warning or error would be hidden.
	// Configuration parsing warnings **would** still be shown.
	"suppress_warnings": false,
	// Set this option to `false` to force Archey to use its own colors palettes.
	// `true` by default to honor os-release(5) `ANSI_COLOR` option.
	"honor_ansi_color": true,
	// Entries list.
	// Add a `disabled` option set to `true` to temporary hide one.
	// You may change entry displayed name by adding a `name` option.
	// You may re-order the entries list as you wish.
	"entries": [
		{ "type": "User" },
		{ "type": "Hostname" },
		{ "type": "Model" },
		{ "type": "Distro" },
		{ "type": "Kernel" },
		{ "type": "Uptime" },
		{ "type": "Processes" },
		{ "type": "WindowManager" },
		{ "type": "DesktopEnvironment" },
		{ "type": "Shell" },
		{
			"type": "Terminal",
			// Leave this option set to `true` to display a beautiful colors palette.
			// Set it to `false` to allow compatibility with non-Unicode locales.
			"use_unicode": true
		},
		{ "type": "Packages" },
		{
			"type": "Temperature",
			// The character to display between the temperature value and the unit (as '°' in 53.2°C).
			"char_before_unit": " ",
			"sensors_chipsets": [
				// White-list of chipset identifiers (strings) passed to LM-SENSORS when computing the average temperature.
				// Use `sensors -A` to list the available chipsets on your system (e.g. `coretemp-isa-0000`, `acpitz-acpi-0`, ...).
				// Leaving empty (default) would make Archey process input data from all available chipsets.
				// Use this option if a sensor happens to return irrelevant values, or if you want to exclude it.
			],
			// Display temperature values in Fahrenheit instead of Celsius.
			"use_fahrenheit": false
		},
		{
			"type": "CPU",
			// Set to `true` to join all CPUs on the same line.
			"one_line": false,
			// Set to `false` to hide the number of cores.
			"show_cores": true,
			//
			// As explained above, you may rename entries as you wish.
			"name": "Processor"
		},
		{
			"type": "GPU",
			// Set to `true` to join all GPUs on the same line.
			"one_line": false,
			// The maximum number of GPUs you want to display.
			// `false` --> Unlimited.
			"max_count": 2
		},
		{
			"type": "RAM",
			// Some threshold values you can adjust affecting warning/danger colors.
			"warning_use_percent": 33.3,
			"danger_use_percent": 66.7
		},
		{
			"type": "LAN_IP",
			// The maximum number of local addresses you want to display.
			// `false` --> Unlimited.
			"max_count": 2,
			// Set to `false` to only display IPv4 LAN addresses.
			"ipv6_support": true
		},
		{
			"type": "Disk",
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
			"hide_entry_name": null,
			// Some threshold values you can adjust affecting warning/danger colors.
			"warning_use_percent": 50,
			"danger_use_percent": 75
		},
		{
			"type": "WAN_IP",
			//
			// As explained above, you may temporary hide entries as you wish.
			// See below example to hide your public IP addresses before posting your configuration on Internet.
			//"disabled": true,
			//
			// Below are settings relative to IPv4/IPv6 public addresses retrieval.
			// I hope options are self-explanatory.
			// You may set `dns_query` (or `http_url`) to `false` to disable them.
			// You may directly set `ipv4` or `ipv6` fields to `false` to completely disable them.
			//
			// <https://ident.me/> server sources : <https://github.com/pcarrier/identme>.
			"ipv4": {
				"dns_query": "myip.opendns.com",
				"dns_resolver": "resolver1.opendns.com",
				"dns_timeout": 1,
				"http_url": "https://v4.ident.me/",
				"http_timeout": 1
			},
			"ipv6": {
				"dns_query": "myip.opendns.com",
				"dns_resolver": "resolver1.opendns.com",
				"dns_timeout": 1,
				"http_url": "https://v6.ident.me/",
				"http_timeout": 1
			}
		}
	],
	"default_strings": {
		// Use this section to override default strings (internationalization).
	}
}

```

## Test cases

An extensive tests suite is available.  
Here is a short procedure to run them (you'll only need `python3`) :

```bash
git clone https://github.com/HorlogeSkynet/archey4.git
cd archey4/

# Run the suite from SetupTools.
python3 setup.py test

# Run the suite from the unit testing framework itself.
python3 -m unittest
```

Any improvement would be appreciated.

## Notes to users

* If you experience any trouble during the installation or usage, please do **[open an issue](https://github.com/HorlogeSkynet/archey4/issues/new)**.

* If you had to tweak this project to make it work on your system, please **[open a pull request](https://github.com/HorlogeSkynet/archey4/pulls)** so as to share your modifications with the rest of the world and participate in this project ! You should also check [Info for contributors](https://github.com/HorlogeSkynet/archey4/wiki/Info-for-contributors).

* If your distribution is not (currently) supported, please check [How do I add a distribution to Archey?](https://github.com/HorlogeSkynet/archey4/wiki/How-do-I-add-a-distribution-to-Archey%3F).
