# Archey 4

> Archey is a simple system information tool written in Python

![archey4](https://horlogeskynet.github.io/img/blog/the-archey-project-what-i-ve-decided-to-do.png?v4.3.1)

## Why (again) a f*cking new Archey fork ?

The answer is [here](https://horlogeskynet.github.io/archey4).

> Note : Since the 21st September of 2017, you may notice that this repository no longer has the official status of fork.  
> Actually, the maintainer decided to separate it from the original one's "network" with the help of _GitHub_'s staff.  
> Nevertheless, **this piece of software is still a fork of [djmelik's Archey project](https://github.com/djmelik/archey.git)**.

## Which packages do I need to run this script ?

### Required packages

* python3
* lsb-release
* procps

### Highly recommended packages

| Environments |  Packages  |                Reasons                | Notes |
| :----------- | :--------: | :-----------------------------------: | :---: |
| All          | `dnsutils`<br>`net-tools` | **WAN_IP** and **LAN_IP** would be detected faster | They will provide `dig` and `hostname` |
| Graphical    |  `pciutils`<br>`wmctrl`  | **GPU** wouldn't be detected without it<br>**WindowManager** would be more accurate | `pciutils` will provide `lspci` |
| Virtual      | `virt-what`<br>`dmidecode` | **Model** would contain details about the hypervisor | `archey` will need to be run as **root** |

**Without `dnsutils` (or `bind-tools` on Arch Linux), you'll need `wget` in order to retrieve your public IP address.**

## Installation

### Install from package

First, grab a package for your distribution from the latest release [here](https://github.com/HorlogeSkynet/archey4/releases/latest).  
Now, it's time to use your favorite package manager. Some examples :

* Arch-based distributions ([source](https://aur.archlinux.org/packages/archey4/))

	```shell
	pacman -U ./archey4-v4.Y.Z-R-any.pkg.tar.xz
	```

* Debian-based distributions ([source](https://labs.pixelswap.fr/HorlogeSkynet/archey4-packaging))

	```shell
	apt install ./archey4-4.Y.Z-R-all.deb
	```

* Red Hat, Fedora, OpenSuse, ... ([source](https://labs.pixelswap.fr/HorlogeSkynet/archey4-packaging))

	```shell
	dnf install ./archey4-4.Y.Z-R.noarch.rpm
	```

### Install from source

#### Latest stable release

First, grab the archive containing the source code for the latest release [here](https://github.com/HorlogeSkynet/archey4/releases/latest), and then :

```shell
$ tar xvzf archey4-4.X.Y.tar.gz
$ cd archey4-4.X.Y/
$ chmod +x archey
$ sudo cp archey /usr/local/bin/archey
```

#### Development version

```shell
$ git clone https://github.com/HorlogeSkynet/archey4.git
$ cd archey4/
$ chmod +x archey
# Fetch latest changes (update your local version)
$ git pull
$ sudo cp archey /usr/local/bin/archey
```

## Usage

```shell
$ archey
```

## Configuration (optional)

Since the version 4.3.0, Archey 4 **may** be "tweaked" a bit with external configuration.  
You can place a [`config.json`](config.json) file in these locations :

1. `/etc/archey4/config.json` (system preferences)
2. `~/.config/archey4/config.json` (user preferences)
3. `./config.json` (local preferences)

**If an option is defined in multiple places, it will be overridden according to the order above (local preferences > user preferences > system preferences).**

The [example file](config.json) provided in this repository lists exhaustively the parameters you can set.  
Below, some further explanations of each option available :

```cpp
{
	// If set to `false`, configurations defined afterwards won't be loaded.
	// Developers running Archey from the original project may keep in there the original `config.json` while having their own external configuration set elsewhere.
	"allow_overriding": true,
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
		// `false` would make Archey displays only IPv4 WAN addresses.
		"wan_ip_v6_support": true
	},
	"temperature": {
		// The character to display between the temperature value and the unit (as '°' in 53.2°C).
		// Set to ' ' (space) by default for backward compatibility with non-Unicode locales.
		"char_before_unit": " ",
		// Display temperature values in Fahrenheit instead of Celsius.
		"use_fahrenheit": false
	},
	"timeout": {
		// Some values you can adjust if the default ones look undersized for your system (seconds)
	}
}
```

## Notes to users

* If you run `archey` as root, the script will list the processes running by other users on your system in order to display the **Window Manager** & **Desktop Environment** outputs correctly.

* During the setup procedure, I advised you to copy this script into the `/usr/local/bin/` folder, you may want to check what it does beforehand.

* If you experience any trouble during the installation or usage, please do **[open an issue](https://github.com/HorlogeSkynet/archey4/issues/new)**.

* If you had to adapt the script to make it working with your system, please **[open a pull request](https://github.com/HorlogeSkynet/archey4/pulls)** so as to share your modifications with the rest of the world and participate in this project !
