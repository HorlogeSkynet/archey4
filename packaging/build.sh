#!/usr/bin/env bash


# ################################################################################
#                 Archey 4 distribution packages building script
#
# Dependencies :
# * python3
# * rpm
# * debsigs
# * fpm >= 1.11.0
# * twine >= 3.1.1
#
# Procedure to install them on Debian :
# $ sudo apt install ruby rubygems build-essential python3-pip debsigs rpm
# $ sudo gem install --no-document fpm
# $ sudo pip3 install setuptools twine
#
# Run it as :
# $ bash packaging/build.sh [REVISION] [0xGPG_IDENTITY]
#
# Known packages errors (FPM bugs ?) :
# * Debian :
#     * Lintian : file-in-etc-not-marked-as-conffile etc/archey4/config.json
# * Arch Linux :
#     * `--pacman-optional-depends` appears to be ignored [jordansissel/fpm#1619]
#
# ################################################################################


# Abort on error, don't allow usages of undeclared variable.
set -e ; set -u


# Let's gather some metadata from the `setup.py` file.
NAME="$(python3 setup.py --name)"
VERSION="$(python3 setup.py --version)"
AUTHOR="$(python3 setup.py --author)"
AUTHOR_EMAIL="$(python3 setup.py --author-email)"


# DRY.
REVISION="${1:-1}"
GPG_IDENTITY="${2:-}"
DIST_OUTPUT='./dist'
FAKE_CONFIG_FILE='etc/archey4/config.json'
FPM_COMMON_ARGS=(
	--input-type python \
	--force \
	--iteration "$REVISION" \
	--category 'utils' \
	--provides 'archey' \
	--provides 'archey4' \
	--config-files "$FAKE_CONFIG_FILE" \
	--architecture all \
	--maintainer "$(printf '%s <%s>' "$AUTHOR" "$AUTHOR_EMAIL")" \
	--after-install packaging/after_install \
	--before-remove packaging/before_remove \
	--python-bin python3 \
	--no-python-fix-name \
	--python-install-bin usr/bin \
	--python-install-lib usr/lib/python3/dist-packages \
	--no-python-dependencies \
)


# Prepare the configuration file under a regular `etc/` directory.
mkdir -p etc/archey4 && cp archey/config.json "$FAKE_CONFIG_FILE"


# Prevent Setuptools from generating byte-code files.
export PYTHONDONTWRITEBYTECODE=1


# Build a Debian (.DEB) package.
fpm \
	"${FPM_COMMON_ARGS[@]}" \
	--output-type deb \
	--package "${DIST_OUTPUT}/${NAME}_${VERSION}-${REVISION}_all.deb" \
	--depends 'procps' \
	--depends 'python3 >= 3.4' \
	--depends 'python3-distro' \
	--depends 'python3-netifaces' \
	--deb-priority 'optional' \
	--deb-field 'Suggests: dnsutils, lm-sensors, pciutils, wmctrl, virt-what' \
	--deb-no-default-config-files \
	setup.py

# Sign the resulting Debian package if a GPG identity has been provided.
if [ -n "$GPG_IDENTITY" ]; then
	debsigs \
		--sign=origin \
		-k "$GPG_IDENTITY" \
		./dist/*.deb
fi


# Build a Red Hat/Fedora (.RPM) package.
fpm \
	"${FPM_COMMON_ARGS[@]}" \
	--output-type rpm \
	--package "${DIST_OUTPUT}/${NAME}-${VERSION}-${REVISION}.noarch.rpm" \
	--depends 'procps' \
	--depends 'python3 >= 3.4' \
	--depends 'python3-distro' \
	--depends 'python3-netifaces' \
	setup.py


# Build an Arch Linux (.TAR.XZ) package.
fpm \
	"${FPM_COMMON_ARGS[@]}" \
	--output-type pacman \
	--package "${DIST_OUTPUT}/${NAME}-${VERSION}-${REVISION}-any.pkg.tar.xz" \
	--depends 'procps' \
	--depends 'python >= 3.4' \
	--depends 'python-distro' \
	--depends 'python-netifaces' \
	--conflicts 'archey-git' \
	--conflicts 'archey2' \
	--conflicts 'archey3-git' \
	--conflicts 'pyarchey' \
	--pacman-optional-depends 'bind-tools: WAN_IP would be detected faster' \
	--pacman-optional-depends 'lm_sensors: Temperature would be more accurate' \
	--pacman-optional-depends 'pciutils: GPU wouldn'"'"'t be detected without it' \
	--pacman-optional-depends 'wmctrl: WindowManager would be more accurate' \
	--pacman-optional-depends 'virt-what: Model would contain details about the hypervisor' \
	setup.py


# Remove the fake `etc/` directory.
rm -rf etc/


# Silence some Setuptools warnings by re-enabling byte-code generation.
unset PYTHONDONTWRITEBYTECODE

# Build Python source TAR and WHEEL distribution packages.
python3 setup.py -q sdist bdist_wheel

# Check whether packages description will render correctly on PyPI.
if twine check dist/*.{tar.gz,whl}; then
	echo 'Upload source and wheel distribution packages to PyPI ? [y/N]'
	read -r -n 1 -p '' && echo
	if [[ "$REPLY" =~ ^[yY]$ ]]; then
		twine upload \
			--sign --identity "${GPG_IDENTITY}" \
			dist/*.{tar.gz,whl}
	fi
fi
