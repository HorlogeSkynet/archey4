# archey4

![archey4](https://horlogeskynet.github.io/img/blog/the-archey-project-what-i-ve-decided-to-do.png?v410)

#### Why (again) a f*cking new Archey fork ?

The answer is [here](https://horlogeskynet.github.io/archey4).

#### Which packages do I need to run this script ?

##### Required packages

* python3
* lsb-release

##### Highly recommended packages

| Environments |  Packages  |                Reasons                | Notes |
| :----------- | :--------: | :-----------------------------------: | :---: |
| All          | `dnsutils` | _WAN\_IP_ will be detected 5x faster  |   ∅   |
| Graphical    |  `wmctrl`  | _WindowManager_ will be more accurate |   ∅   |
| Virtual      | `virt-what`<br />`dmidecode` | _Model_ will contain details about the hypervisor | `archey` will need to be run as **root** |

## Installation

### Install latest stable release from source

```bash
$ wget -O archey4.tar.gz https://github.com/HorlogeSkynet/archey4/archive/master.tar.gz
$ tar xvzf archey4.tar.gz
$ cd archey4-master/
$ chmod +x archey
$ sudo cp archey /usr/local/bin/archey
```

### Install (or update) development version from source

```bash
$ git clone https://github.com/HorlogeSkynet/archey4.git
$ cd archey4/
$ chmod +x archey
# Fetch latest changes (update your local version)
$ git pull
$ sudo cp archey /usr/local/bin/archey
```

## Usage

```bash
$ archey
```

#### Notes to users

* If you run `archey` as root, the script will list the processes running by other users on your system in order to display correctly _Window Manager_ & _Desktop Environment_ outputs.

* During the setup procedure, I advised you to copy this script into the `/usr/local/bin/` folder, you may want to check what it does beforehand.

* If you experience any trouble during installation or usage, please do **open an _issue_**.

* If you had to adapt the script to make it working with your system, please **open a _pull request_** so as to share your modifications with the rest of the world and participate to this project !
