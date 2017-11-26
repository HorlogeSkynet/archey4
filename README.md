# Archey 4

![archey4](https://horlogeskynet.github.io/img/blog/the-archey-project-what-i-ve-decided-to-do.png?v410)

## Why (again) a f*cking new Archey fork ?

The answer is [here](https://horlogeskynet.github.io/archey4).

> Note : Since the 21st September of 2017, you may notice that this repository no longer has the official status of fork.  
> Actually, the maintainer decided to separate it from the original one's "network" with the help of the _GitHub_'s staff.  
> Nevertheless, **this piece of software is still a fork of the [djmelik's Archey project](https://github.com/djmelik/archey.git)**.

## Which packages do I need to run this script ?

### Required packages

* python3
* lsb-release

### Highly recommended packages

| Environments |  Packages  |                Reasons                | Notes |
| :----------- | :--------: | :-----------------------------------: | :---: |
| All          | `dnsutils` | **WAN_IP** would be detected 5x faster   |   ∅   |
| Graphical    |  `wmctrl`  | **WindowManager** would be more accurate |   ∅   |
| Virtual      | `virt-what`<br>`dmidecode` | **Model** would contain details about the hypervisor | `archey` will need to be run as **root** |

## Installation

### Install latest stable release from source

```shell
$ wget -O archey4.tar.gz https://github.com/HorlogeSkynet/archey4/archive/master.tar.gz
$ tar xvzf archey4.tar.gz
$ cd archey4-master/
$ chmod +x archey
$ sudo cp archey /usr/local/bin/archey
```

### Install (or update) development version from source

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

## Notes to users

* If you run `archey` as root, the script will list the processes running by other users on your system in order to display correctly **Window Manager** & **Desktop Environment** outputs.

* During the setup procedure, I advised you to copy this script into the `/usr/local/bin/` folder, you may want to check what it does beforehand.

* If you experience any trouble during installation or usage, please do **[open an issue](https://github.com/HorlogeSkynet/archey4/issues/new)**.

* If you had to adapt the script to make it working with your system, please **[open a pull request](https://github.com/HorlogeSkynet/archey4/pulls)** so as to share your modifications with the rest of the world and participate in this project !
