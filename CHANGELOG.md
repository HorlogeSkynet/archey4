# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project (partially) adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v4.14.0.0] - 2022-09-22
### Breaking
- Project internal versioning update (v4.Y.Z -> 4.X.Y.Z)
- Distributions logo preference over Windows' one in WSL environments

### Removed
- `dmidecode` usage in `Model` for virtual environments info gathering

### Added
- `Custom` entry
- `Load Average` entry
- KWin Wayland WM detection
- Windows Terminal detection
- Missing method static types
- `CPU`, `RAM` and `Model` FreeBSD support
- Official Guix System distribution support
- Official Siduction Linux distribution support

### Changed
- Improve Rocky Linux logo
- Fix macOS APFS volumes duplication
- `CPU` and `Model` entries initialization
- Prevent vendor name duplication in `Model`
- Fix WSL virtual environment detection (without systemd) in `Model`
- Project code base formatted using Black and isort

## [v4.13.4] - 2022-03-20
### Added
- Support for `pacstall` package manager
- Official Buildroot distribution support
- New `entries_color` config option to tune entries color
- New `sensors_excluded_subfeatures` temperature config option to exclude specific sub-features

### Changed
- Update fpm to v1.14.1 for .DEB and .RPM packages building
- Improve `sensors_chipsets` temperature config option documentation

## [v4.13.3] - 2021-11-13
### Added
- Official Rocky Linux distribution support
- Official upcoming support for Python 3.11
- Support for `pkgin` (NetBSD) package manager
- Support for motherboard DMI information in `Model`
- Document terminal monospaced font recommendation for ASCII art

### Changed
- Fix possible `Uptime` discrepancies on macOS 10.12+
- Prevent `system_profiler` STDERR logs output on macOS
- Remove square brackets around architecture from `Distro` entry output
- `virt-what` and/or `dmidecode` probing for `Model`, even for unprivileged users

## [v4.13.2] - 2021-10-16
### Added
- Support for `maim` ("Make image") screenshot back-end

### Changed
- Fix `df` output parsing when file-systems column contain white-spaces in `Disk`
- Prevent program crash when calling external programs raise `PermissionError` exception
- Prevent program crash when reading from `/sys/` file system is not allowed

## [v4.13.1] - 2021-09-04
### Changed
- Only run `pkg` on \*BSD systems
- Improve Darwin (Apple) logo design
- Fix text width overlap regression introduced in v4.13.0
- Fix `brew` `Packages` count on Apple Silicon and GNU/Linux
- Prevent entries `disabled` special field from being propagated in `options`

## [v4.13.0] - 2021-08-29
### Added
- Official NetBSD support
- Archey official project logo (CC-BY Brume)
- Protected `_logger` attribute for `Entry` objects
- PEP-561 compliance (Distributing and Packaging Type Information)

### Changed
- Logos are now right-padding "unaware"
- Fix Pop!\_OS logo (reverted) coloration
- Fix `sensors_chipsets` option (when containing multiple values)
- Fix potential configuration file encoding issues on Windows platforms
- Improve logging style of multiple lines `sensors` error messages
- Extend Android system auto-detection (as CPython standard library does)

## [v4.12.0] - 2021-05-08
### Added
- `Kernel` name
- CHANGELOG.md file
- Homebrew formula in the default tap
- `CLICOLOR[_FORCE]` environment variables support
- `one_line` configuration option for `LAN_IP` & `WAN_IP` entries
- `TERM_PROGRAM_VERSION` environment variable support for `Terminal`
- `USER`, `LOGNAME` & `LNAME` environment variables support for `User` entry
- Alternative logo style support (see `-l` option with `retro` parameter for Darwin)

### Changed
- Prevent text truncation when writing output to a pipe
- "Pretty names" by default for multiple-words entries (`WanIP` -> `WAN IP`)
- `distro` & `netifaces` Python dependencies are now "frozen" to allow upstream breakages

## [v4.11.0] - 2021-03-21
### Added
- Official BSD (and its derivatives) support
- Official Darwin (macOS) support
- Official Parabola GNU/Linux-libre support
- API : new `distro` key now stores the internally detected distribution

### Changed
- `disabled` entries won't be internally executed anymore
- Internal logging has been rewritten, LM-SENSORS(1) warnings messages may now appear
- Now (very degradedly) run even without `procps[-ng]` package installed
- Fix `Disk` detection for mount points containing space characters
- `sys.exit` usages have been replaced by proper `ArcheyException` raising

### Removed
- Python 3.5 support

## [v4.10.0] - 2020-12-18
### Added
- Official Devuan support
- Code base type annotations
- Python 3.10 official support
- `DO_NOT_TRACK` environment variable support
- On GNU/Linux, `Kernel` now supports optional version comparison against <https://www.kernel.org/> (see `check_version` option)

### Changed
- `LAN_IP` now excludes global (public) IP addresses from entry by default (see new `show_global` option to keep old behavior)
- Lazy-load logo (standalone building against Stickytape and PyInstaller may break, see README or Wiki)
- Subprocess call to UNAME(1) have been replaced by proper `platform` module (standard library) usages
- `Uptime` won't crash anymore in environments implying parsing of the `uptime` command (as Android)
- Artifact for Arch-based distributions will now be available as `.tar.zst`

### Removed
- Python 3.4 support

## [v4.9.0] - 2020-11-28
### Added
- PEX building official support
- Entries may now be reordered as you wish
- `CPU` now supports multiple CPUs and show number of cores
- `WAN_IP` now supports very accurate configuration for resolvers and timeouts, including specific method disabling

### Changed
- Configuration layout has changed, please check README or Wiki
- `./config.json` path will automatically be looked up and loaded if it exists
- `GPU` will now be displayed on multiple lines by default
- `Model` now ignores fuzzy data (as "To Be Filled By O.E.M.")
- `Disk` won't soft-fail anymore due when `df` crashes "for reasons"
- `LAN_IP` internal class has been renamed to `LanIP`
- `WAN_IP` internal class has been renamed to `WanIP`
- CI now runs on GitHub Actions for performance purposes

### Removed
- Unit testing modules from releases assets

## [v4.8.1] - 2020-10-11
### Added
- Official Pop!\_OS support
- Official Elementary OS support
- Hardware "product version" for `Model` on GNU/Linux

### Changed
- Fix screenshot module crashing anyhow
- Properly set exit code on error in various situations

## [v4.8.0] - 2020-09-26
### Added
- Entries are now loaded in parallel
- Python 3.9 official support
- NixOS (basic) support
- Android (basic) support
- \*BSD (very partial) support
- BusyBox-based (final) support
- Specific distribution logo to display (`-d` option)
- Specific configuration file loading support (`-c` option)
- Screenshot taking is now supported (`-s [FILENAME]` option)
- New `Processes` entry, showing the number of running processes
- `NO_COLOR` environment variable support

### Changed
- `Disk` now supports multiple entries
- Fix support for CrunchBang distribution (broken in v4.6.0)
- Unicode will now be enabled by default (see `use_unicode` configuration option)
- Update Fedora, Ubuntu & Windows logos

## [v4.7.2] - 2020-05-20
### Added
- JSON output (`-j` option)
- GNU/Linux packages now ship a proper UNIX manual page

### Changed
- `GPU` now supports multiple entries
- `Terminal` should now properly display terminal emulator
- Fix line overlapping when output is longer than terminal width
- Arch Linux release packages will now be built AUR
- Don't crash if `netifaces` Python module is not available

## [v4.7.1] - 2020-04-24
### Added
- Official CentOS support
- Official Alpine Linux support
- Internal version output (`-v` option)
- LM-SENSORS(1) polled chipsets can now be configured (see `sensors_chipsets` configuration option)
- Distribution matching "fall-back" based on `ID_LIKE` OS-RELEASE(5) option
- `ANSI_COLOR` OS-RELEASE(5) option will now be honored by default (see `honor_ansi_color` configuration option)

### Changed
- Fix .RPM and Arch Linux packages
- Fix BTRFS file-system type `Disk` support
- Fix some entries not working in limited environments (as Docker)
- Fix `WAN_IP` timeout exceptions that may occur when relying on `urllib`
- Fix `Temperature` average value computation against fan control chipsets
- Fix `systemd-detect-virt` execution output not being honored in `Model`
- Fix configuration file not being marked as one in .DEB & .RPM packages
- Update Arch Linux, Manjaro & Ubuntu logos colors

## [v4.7.0] - 2020-03-27
### Added
- GPG signature for Debian packages
- BTRFS & TMPFS file-systems `Disk` support
- `netifaces` Python module dependency (for `LAN_IP` entry)
- Configurable thresholds for `Disk` & `RAM` entries output colors
- Basic support for Deepin windows manager & desktop environment

### Changed
- Fix (manual) `RAM` computations
- Fix units displayed for `Disk` & `RAM`
- Software architecture (now a proper Python module)
- If available, rely on `systemd-detect-virt` instead of `virt-what`
- Use FPM to build distributions packages

### Removed
- Heading and trailing newlines
- `bare_metal_environment` I18N configuration option (internally dropped)
- `wget` dependency for `WAN_IP` (replaced by `urllib` standard Python module)

## [v4.6.0] - 2018-08-25
### Added
- PyLint compliance
- SlackWare official support
- `distro` Python module dependency

### Changed
- Fix `GPU` truncation
- Fix some warnings in unit tests
- Fix `WAN_IP` addresses consistency between IPv4 and IPv6
- Update contributors list

### Removed
- LSB-RELEASE(1) dependency

## [v4.5.0] - 2018-07-23
### Added
- Python 3.7 official support
- WSL file-systems `Disk` support
- Python Wheels as GitHub releases assets (as long as their GPG signature)

### Changed

## [v4.4.1] - 2018-05-30
### Changed
- Extend `CPU` detection for some ARM architectures
- Properly handle encoding-relative errors at runtime

## [v4.4.0] - 2018-02-19
### Added
- Test cases
- CI pipeline
- .gitignore file
- Publish program on PyPI
- SetupTools compatibility
- Allow output strings to be configured (I18N)

### Changed
- Enhance `Packages` accuracy
- Fix `Packages` compatibility against non-English locales
- Warning messages can now be silenced (see `suppress_warnings` configuration option)

## [v4.3.3] - 2018-02-02
### Added
- Configurable timeout for IP addresses detection

### Changed
- Fix crash if `wget` is missing
- Redirect warnings and errors messages to STDERR

## [v4.3.2] - 2018-01-30
### Added
- Windows Subsystem Linux support
- IPv6 support for `LAN_IP` & `WAN_IP`
- New option to specify the maximum number of `LAN_IP` addresses to show

### Changed
- Fix configuration file decoding against Python 3.4

## [v4.3.1] - 2017-12-27
### Added
- Colors palette to `Terminal` entry output
- Entries can now be masked from configuration
- Implements configuration "locking" (see `allow_overriding` configuration option)

### Changed
- Fix KDE Plasma detection

## [v4.3.0] - 2017-12-10
### Added
- New `Temperature` entry
- External configuration file

### Changed
- Fix `RAM` computation

## [v4.2.2] - 2017-10-23
### Added
- Help message about LSB-RELEASE(1) dependency
- Distributions packages for Arch Linux, Debian & Red Hat

### Changed
- Fix Ubuntu logo

### Removed
- Trailing white-space

## [v4.2.1] - 2017-09-17
### Changed
- Enhance modularity
- Detach repository from djmelik/archey GitHub network

## [v4.2.0] - 2017-08-29
### Added
- `Model` now supports Raspberry Pi
- `Model` now supports virtual environments
- GitHub Issues & pull requests templates

### Changed
- Fix crash when `wmctrl` is missing
- Silence distributions packages tools error messages

## [v4.1.2] - 2017-08-22
### Changed
- Project name (lowercased)

### Removed
- "Empty set" character usages for backward-compatibility against non-Unicode platforms

## [v4.1.1] - 2017-08-08
### Changed
- Backward-compatibility for older `inetutils` packages

### Removed
- Nemo windows manager

## [v4.1.0] - 2017-07-27
### Added
- New `LAN_IP` entry
- New `WAN_IP` entry

### Changed
- Replaces `subprocess.Popen` by `subprocess.check_output`

### Removed
- Python < 3.4 support

## [v4.0.5] - 2017-06-21
### Changed
- Enhance support for Arch Linux derivatives

## [v4.0.4] - 2017-05-19
### Changed
- Allow longer `GPU` output text
- Fix a color glitch with some terminal emulators

## [v4.0.3] - 2017-05-15
### Changed
- Fix output for uncolored terminal profiles

## [v4.0.2] - 2017-05-12
### Changed
- Fix running as `root`
- Enhance backward-compatibility by removing `free -w` usage

## [v4.0.1] - 2017-05-06
### Changed
- Fix some logos
- Enhance `GPU` support for some video cards

## [v4.0.0] - 2017-05-05
### Added
- Support for new operating systems

### Changed
- Main bugs fixes
- Project officially forked from djmelik/archey

[Unreleased]: https://github.com/HorlogeSkynet/archey4/compare/v4.14.0.0...HEAD
[v4.14.0.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.13.4...v4.14.0.0
[v4.13.4]: https://github.com/HorlogeSkynet/archey4/compare/v4.13.3...v4.13.4
[v4.13.3]: https://github.com/HorlogeSkynet/archey4/compare/v4.13.2...v4.13.3
[v4.13.2]: https://github.com/HorlogeSkynet/archey4/compare/v4.13.1...v4.13.2
[v4.13.1]: https://github.com/HorlogeSkynet/archey4/compare/v4.13.0...v4.13.1
[v4.13.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.12.0...v4.13.0
[v4.12.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.11.0...v4.12.0
[v4.11.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.10.0...v4.11.0
[v4.10.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.9.0...v4.10.0
[v4.9.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.8.1...v4.9.0
[v4.8.1]: https://github.com/HorlogeSkynet/archey4/compare/v4.8.0...v4.8.1
[v4.8.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.7.2...v4.8.0
[v4.7.2]: https://github.com/HorlogeSkynet/archey4/compare/v4.7.1...v4.7.2
[v4.7.1]: https://github.com/HorlogeSkynet/archey4/compare/v4.7.0...v4.7.1
[v4.7.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.6.0...v4.7.0
[v4.6.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.5.0...v4.6.0
[v4.5.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.4.1...v4.5.0
[v4.4.1]: https://github.com/HorlogeSkynet/archey4/compare/v4.4.0...v4.4.1
[v4.4.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.3.3...v4.4.0
[v4.3.3]: https://github.com/HorlogeSkynet/archey4/compare/v4.3.2...v4.3.3
[v4.3.2]: https://github.com/HorlogeSkynet/archey4/compare/v4.3.1...v4.3.2
[v4.3.1]: https://github.com/HorlogeSkynet/archey4/compare/v4.3.0...v4.3.1
[v4.3.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.2.2...v4.3.0
[v4.2.2]: https://github.com/HorlogeSkynet/archey4/compare/v4.2.1...v4.2.2
[v4.2.1]: https://github.com/HorlogeSkynet/archey4/compare/v4.2.0...v4.2.1
[v4.2.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.1.2...v4.2.0
[v4.1.2]: https://github.com/HorlogeSkynet/archey4/compare/v4.1.1...v4.1.2
[v4.1.1]: https://github.com/HorlogeSkynet/archey4/compare/v4.1.0...v4.1.1
[v4.1.0]: https://github.com/HorlogeSkynet/archey4/compare/v4.0.5...v4.1.0
[v4.0.5]: https://github.com/HorlogeSkynet/archey4/compare/v4.0.4...v4.0.5
[v4.0.4]: https://github.com/HorlogeSkynet/archey4/compare/v4.0.3...v4.0.4
[v4.0.3]: https://github.com/HorlogeSkynet/archey4/compare/v4.0.2...v4.0.3
[v4.0.2]: https://github.com/HorlogeSkynet/archey4/compare/v4.0.1...v4.0.2
[v4.0.1]: https://github.com/HorlogeSkynet/archey4/compare/v4.0.0...v4.0.1
[v4.0.0]: https://github.com/HorlogeSkynet/archey4/releases/tag/v4.0.0
