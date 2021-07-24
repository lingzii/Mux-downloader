def playsound(sound, block=True):
    from ctypes import c_buffer, windll
    from random import random
    from time import sleep
    from os.path import abspath, join
    import sys

    class PlaysoundException(Exception):
        pass

    def winCommand(*command):
        buf = c_buffer(255)
        command = ' '.join(command).encode(sys.getfilesystemencoding())
        errorCode = int(windll.winmm.mciSendStringA(command, buf, 254, 0))
        if errorCode:
            errorBuffer = c_buffer(255)
            windll.winmm.mciGetErrorStringA(errorCode, errorBuffer, 254)
            exceptionMessage = ('\n    Error ' + str(errorCode) + ' for command:'
                                '\n        ' + command.decode() +
                                '\n    ' + errorBuffer.value.decode())
            raise PlaysoundException(exceptionMessage)
        return buf.value

    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except:
            base_path = abspath(".")
        return join(base_path, relative_path)

    sound = resource_path(sound)
    alias = 'playsound_' + str(random())
    winCommand('open "' + sound + '" alias', alias)
    winCommand('set', alias, 'time format milliseconds')
    durationInMS = winCommand('status', alias, 'length')
    winCommand('play', alias, 'from 0 to', durationInMS.decode())

    if block:
        sleep(float(durationInMS) / 1000.0)
