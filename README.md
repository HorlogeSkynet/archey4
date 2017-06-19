# Archey4

![Archey4](https://horlogeskynet.github.io/img/blog/the-archey-project-what-i-ve-decided-to-do.png)

### Why, again, a f*cking new Archey fork ?

The answer is [here](https://horlogeskynet.github.io/Archey4).

### What do I need to get and use this script ?

Required packages:

* python3
* lsb-release

Recommended packages:

* wmctrl

### Setup procedure

```
$  git clone https://github.com/HorlogeSkynet/Archey4.git
$  cd Archey4/
$  chmod +x archey
#  cp archey /usr/bin/archey
$  cd .. && rm -rf Archey4/
```

### Usage

```
$  archey
```

### Notes

* If you run `archey` as root, the script will list the processes running by other users on your system in order to display correctly Window Manager & Desktop Environment outputs.

* During the setup procedure, I advised you to copy this script into the `/usr/bin/` folder, you may want to check what it does beforehand.

* If you experience any trouble during installation or usage, please do **open an _issue_**.

* If you had to adapt the script to make it working with your system, please **open a _pull request_** so as to share your modifications with the rest of the world and participate to this project !
