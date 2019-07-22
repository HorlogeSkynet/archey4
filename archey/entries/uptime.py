"""Uptime detection class"""


class Uptime:
    """Returns a pretty-formatted string representing the host uptime"""
    def __init__(self):
        with open('/proc/uptime') as file:
            fuptime = int(file.read().split('.')[0])

        day, fuptime = divmod(fuptime, 86400)
        hour, fuptime = divmod(fuptime, 3600)
        minute = fuptime // 60

        uptime = ''
        if day:
            uptime += str(day) + ' day'
            if day > 1:
                uptime += 's'

            if hour or minute:
                if bool(hour) != bool(minute):
                    uptime += ' and '

                else:
                    uptime += ', '

        if hour:
            uptime += str(hour) + ' hour'
            if hour > 1:
                uptime += 's'

            if minute:
                uptime += ' and '

        if minute:
            uptime += str(minute) + ' minute'
            if minute > 1:
                uptime += 's'

        else:
            if not day and not hour:
                uptime = '< 1 minute'

        self.value = uptime
