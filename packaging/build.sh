#!/usr/bin/env bash


# ##########################################################
#      Archey 4 distribution packages building script
#
# Dependencies :
# * fpm >= 1.11.0
# * rpm >= 4.14.2
# * twine >= 3.1.1
#
# Procedure to install them on Debian :
# $ sudo apt install ruby ruby-dev rubygems build-essential
# $ sudo apt install python3-pip rpm
# $ sudo gem install --no-document fpm
# $ sudo pip3 install twine
#
# Run it as :
# $ bash packaging/build.sh [REVISION]
#
# Known errors for the Debian package :
# * lintian: file-in-etc-not-marked-as-conffile etc/archey4/config.json
# ##########################################################



# Let's gather some metadata from the `setup.py` file.
author="$(python3 setup.py --author)"
author_email="$(python3 setup.py --author-email)"


# Prepare the configuration file under a regular `etc/` directory.
mkdir -p etc/archey4 && cp archey/config.json etc/archey4/config.json


# Build .DEB (Debian), .RPM (Red Hat/Fedora) & .TAR.XZ (Arch Linux) packages.
for type in deb rpm pacman; do
	fpm \
		--input-type python \
		--output-type "$type" \
		--force \
		--iteration "${1:-1}" \
		--category 'utils' \
		--depends python3 \
		--depends procps \
		--provides 'archey' \
		--provides 'archey4' \
		--config-files etc/archey4/config.json \
		--architecture all \
		--maintainer "$(printf '%s <%s>' "$author" "$author_email")" \
		--after-install packaging/after_install \
		--before-remove packaging/before_remove \
		--deb-priority 'optional' \
		--deb-field 'Suggests: dnsutils, lm-sensors, pciutils, wmctrl, virt-what' \
		--deb-no-default-config-files \
		--python-bin python3 \
		--python-package-name-prefix 'python3' \
		--no-python-fix-name \
		--python-fix-dependencies \
		--python-install-bin usr/bin \
		--python-install-lib usr/lib/python3/dist-packages/ \
		--python-dependencies \
		setup.py
done


# Move obtained packages to the `dist/` directory.
mv ./*.{deb,rpm,tar.xz} dist/


# Remove the fake `etc/` directory.
rm -rf etc/ conffiles
