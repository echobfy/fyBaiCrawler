# -*- encoding: utf-8 -*-

import errno
import os
import platform
import subprocess
from subprocess import PIPE


class ShellException(Exception):
    pass


class ShellProcess(object):

    def __init__(self, executable, options=(), args=()):
        options = ' '.join(options)
        arguments = ' '.join(args)
        self.path = executable + " " + options + " " + arguments

    def start(self):

        try:
            cmd = self.path
            self.process = subprocess.Popen(cmd, close_fds=platform.system() != "Windows", bufsize=4096,
                                            stdout=PIPE, shell=True)
        except TypeError:
            raise
        except OSError as err:
            if err.errno == errno.ENOENT:
                raise ShellException(
                    "'%s' executable needs to be in PATH." % (
                        os.path.basename(self.path))
                )
            elif err.errno == errno.EACCES:
                raise ShellException(
                    "'%s' executable may have wrong permissions" % (
                        os.path.basename(self.path))
                )
            else:
                raise
        except Exception as e:
            raise ShellException(
                "The executable %s needs to be available in the path. \n%s" %
                (os.path.basename(self.path), str(e)))

    def read(self):
        stdout, stderr = self.process.communicate()
        retcode = self.process.poll()
        if retcode:
            return retcode, stdout
        else:
            return None, stdout

    def stop(self):
        pass

    def __del__(self):
        self.stop()
