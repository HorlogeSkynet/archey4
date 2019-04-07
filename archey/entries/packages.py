from subprocess import check_output, DEVNULL, CalledProcessError


class Packages:
    def __init__(self, not_detected=None):
        for packages_tool in [['dnf', 'list', 'installed'],
                              ['dpkg', '--get-selections'],
                              ['emerge', '-ep', 'world'],
                              ['pacman', '-Q'],
                              ['rpm', '-qa'],
                              ['yum', 'list', 'installed'],
                              ['zypper', 'search', '-i']]:
            try:
                results = check_output(
                    packages_tool,
                    stderr=DEVNULL, env={'LANG': 'C'}, universal_newlines=True
                )
                packages = results.count('\n')

                # Deduct extra heading line
                if 'dnf' in packages_tool:
                    packages -= 1

                # Packages removed but not purged
                elif 'dpkg' in packages_tool:
                    packages -= results.count('deinstall')

                # Deduct extra heading lines
                elif 'emerge' in packages_tool:
                    packages -= 5

                # Deduct extra heading lines
                elif 'yum' in packages_tool:
                    packages -= 2

                # Deduct extra heading lines
                elif 'zypper' in packages_tool:
                    packages -= 5

                break

            except (FileNotFoundError, CalledProcessError):
                pass

        else:
            packages = not_detected

        self.value = packages

