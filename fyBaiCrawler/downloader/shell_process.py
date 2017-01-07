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
            self.process = subprocess.Popen(cmd, close_fds=platform.system() != "Windows",
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
        return self.process.returncode, self.process.communicate()

    def stop(self):
        if self.process is None:
            return

        try:
            if self.process:
                for stream in [self.process.stdin,
                               self.process.stdout,
                               self.process.stderr]:
                    try:
                        stream.close()
                    except AttributeError:
                        pass
                self.process.terminate()
                self.process.kill()
                self.process.wait()
                self.process = None
        except OSError:
            # kill may not be available under windows environment
            pass

    def __del__(self):
        self.stop()
