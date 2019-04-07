import re
from subprocess import check_output
from constants import COLOR_DICT


class Disk:
    def __init__(self):
        total = re.sub(
            ',', '.',
            check_output(
                [
                    'df', '-Tlh', '-B', 'GB', '--total',
                    '-t', 'ext4', '-t', 'ext3', '-t', 'ext2',
                    '-t', 'reiserfs', '-t', 'jfs', '-t', 'zfs',
                    '-t', 'ntfs', '-t', 'fat32', '-t', 'btrfs',
                    '-t', 'fuseblk', '-t', 'xfs', '-t', 'simfs',
                    '-t', 'tmpfs', '-t', 'lxfs'
                ], universal_newlines=True
            ).splitlines()[-1]
        ).split()

        self.value = '{0}{1}{2} / {3}'.format(
            COLOR_DICT['sensors'][int(float(total[5][:-1]) // 33.34)],
            re.sub('GB', ' GB', total[3]),
            COLOR_DICT['clear'],
            re.sub('GB', ' GB', total[2])
        )
