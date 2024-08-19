# Archey4 AppArmor profile
# Copyright (C) 2023-2024 - Michael Bromilow
# Copyright (C) 2023-2024 - Samuel Forestier <samuel+dev@forestier.app>

# /!\ DO NOT MODIFY THIS FILE /!\
# Please edit local profile extension (/etc/apparmor.d/local/usr.bin.archey4).

abi <abi/3.0>,

include <tunables/global>

profile archey4 /usr/{,local/}bin/archey{,4} {
	include <abstractions/base>
	include <abstractions/consoles>
	include <abstractions/nameservice>
	include <abstractions/openssl>
	include <abstractions/python>
	include <abstractions/ssl_certs>

	/usr/bin/ r,
	/usr/{,local/}bin/archey{,4} r,

	# configuration files
	owner @{HOME}/.config/archey4/*.json r,
	/etc/archey4/*.json r,

	# required in order to kill sub-processes in timeout
	capability kill,
	signal (send),

	# allow running processes listing through ps
	/{,usr/}bin/ps PUx,

	# allow distro to parse system data sources
	/usr/lib/os-release r,
	/etc/*[-_]{release,version} r,
	/{,usr/}bin/lsb_release PUx,
	/{,usr/}bin/uname PUx,

	# allow screenshot tools execution
	/{,usr/}bin/escrotum PUx,
	/{,usr/}bin/flameshot PUx,
	/{,usr/}bin/gnome-screenshot PUx,
	/{,usr/}bin/grim PUx,
	/{,usr/}bin/import-im6.q16{,hdri} PUx,
	/{,usr/}bin/maim PUx,
	/{,usr/}bin/scrot PUx,
	/{,usr/}bin/shutter PUx,
	/{,usr/}bin/spectacle PUx,
	/{,usr/}bin/xfce4-screenshoter PUx,

	# [CPU] entry
	/{,usr/}bin/lscpu PUx,

	# [Disk] entry
	/{,usr/}bin/df PUx,

	# [GPU] entry
	/{,usr/}bin/lspci PUx,
	@{sys}/kernel/debug/dri/[0-9]*/{name,v3d_ident} r,

	# [Hostname] entry
	/etc/hostname r,

	# [Load Average] entry
	@{PROC}/loadavg r,

	# [Model] entry
	@{PROC}/device-tree/model r,
	@{sys}/devices/virtual/dmi/id/* r,
	/{,usr/}bin/systemd-detect-virt PUx,
	/{,usr/}{,s}bin/virt-what PUx,
	/{,usr/}bin/getprop PUx,

	# [Packages] entry
	/{,usr/}bin/ls rix,
	/{,usr/}bin/apk PUx,
	#/{,usr/}bin/apt PUx,
	/{,usr/}bin/dnf PUx,
	/{,usr/}bin/dpkg PUx,
	/{,usr/}bin/emerge PUx,
	/usr/{,local/}bin/flatpak PUx,
	/{,usr/}bin/nix-env PUx,
	/{,usr/}bin/pacman PUx,
	/{,usr/}bin/pacstall PUx,
	/{,usr/}bin/pkgin PUx,
	/{,usr/}bin/port PUx,
	/{,usr/}bin/rpm PUx,
	/usr/{,local/}bin/snap PUx,
	/{,usr/}bin/yum PUx,
	/{,usr/}bin/zypper PUx,

	# [RAM] entry
	/{,usr/}bin/free rix,

	# [Temperature] entry
	@{sys}/devices/thermal/thermal_zone[0-9]*/temp r,
	/{,usr/}bin/sensors PUx,
	/{,opt/vc/,usr/}bin/vcgencmd PUx,

	# [Uptime] entry
	@{PROC}/uptime r,
	/{,usr/}bin/uptime rix,

	# [User] & [Shell] entries
	/{,usr/}bin/getent rix,

	# [WAN IP] entry (and potentially [Kernel])
	/{,usr/}bin/dig PUx,
	network inet stream,  # urllib (HTTP/IP)
	network inet6 stream,  # urllib (HTTP/IPv6)

	# [Window Manager] entry
	/{,usr/}bin/wmctrl PUx,

	# allow profile extension (e.g. for user-defined [Custom] entries)
	include if exists <local/usr.bin.archey4>
}
