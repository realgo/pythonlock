#!/usr/bin/env python
#
#  Generic locking routines

'''
Basically, you just select a lock-file name, and create a jlock instance
using tha tname any any parameters you want to override.  Then either
let the object fall out of scope or (preferred) call the "release"
method on it:

       import jlock
   lock = jlock.lock('/dev/shm/mylockfile', retries = 100, doRaise = 1)
   if !lock.haveLock:
              print "Didn't get lock"
      print "This shouldn't happen because doRaise=1 is set"
      sys.exit(0)
   [do stuff]
   lock.release()

The lock currently sleeps for one second, so the above will wait for the
lock for 100 seconds.  You can tune both of those settings, though for
the lock wait time you'll have to modify the code.  If you ever expect
to have more than 100 outstanding processes waiting for the resource at
a given time, you will have to either adjust the retries, sleep time, or
move to a different mechanism.

retries is the number of attempts that will be made before the locking
code gives up trying to get the lock.

doRaise if raise an exception if the lock cannot be aquired.

tryBreak if set will cause the code to read the lock-file and if the
process ID listed in it is no longer running, the lock-file will be
deleted.
'''

import time
import os
import string


class LockError(Exception):
    def __init__(self, *args):
        apply(Exception.__init__, (self,) + args)


class lock:
    def __init__(self, name, retries=0, tryBreak=1, doRaise=0):
        self.lockedByPid = None
        self.pid = str(os.getpid())
        self.lockFile = name
        self.lockFile2 = self.lockFile + '.' + self.pid

        self.haveLock = 0
        while not self.haveLock:

            #  break a lock for a non-existant pid
            if tryBreak and os.path.exists(self.lockFile):
                self.lockedByPid = string.strip(
                    open(self.lockFile, 'r').readline())
                try:
                    self.lockedByPid = int(self.lockedByPid)
                except ValueError:
                    self.lockedByPid = None
                try:
                    if self.lockedByPid:
                        os.kill(int(self.lockedByPid), 0)
                except OSError:
                    try:
                        os.unlink(self.lockFile)
                        os.unlink(self.lockFile + '.' + self.lockedByPid)
                        time.sleep(1)
                    except OSError:
                        pass

            #  try to obtain the lock
            try:
                #  write our PID to our lock-file
                fp = open(self.lockFile2, 'w')
                fp.write('%s\n' % self.pid)
                fp.close()

                os.link(self.lockFile2, self.lockFile)
                self.haveLock = 1
            except OSError:
                if retries > 0:
                    time.sleep(1)

            #  exit if we aren't supposed to wait
            if retries < 1:
                break
            retries = retries - 1

        if not self.haveLock:
            os.unlink(self.lockFile2)
            if doRaise:
                raise(LockError, "Unable to obtain lock")

    def release(self):
        try:
            if os.path.exists(self.lockFile2):
                os.unlink(self.lockFile2)
            if self.haveLock and os.path.exists(self.lockFile):
                os.unlink(self.lockFile)
            self.haveLock = 0
        except OSError:
            pass

    def __del__(self):
        self.release()

############
#  run tests
if __name__ == '__main__':
    lock = lock('test', retries=10, tryBreak=0, doRaise=1)
    print lock.haveLock
