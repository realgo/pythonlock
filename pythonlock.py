#!/usr/bin/env python
#
#  Generic locking routines

'''
Just select a lock-file name, and create a jlock instance using that
name any any parameters you want to override.  Then either let the
object fall out of scope or (preferred) call the "release()" method:

    import jlock
    lock = jlock.lock('/dev/shm/mylockfile', retries=100, doRaise=True)
    if not lock.haveLock:
        print "Didn't get lock"
        print "This shouldn't happen because doRaise=1 is set"
        sys.exit(0)
    [do stuff]
    lock.release()

The lock sleeps for one second, so the above will wait for the lock for
100 seconds.  You can tune both of those settings.

"retries" is the number of attempts that will be made before the locking
code gives up trying to get the lock.

"doRaise" if raise an exception if the lock cannot be aquired.

"tryBreak" if set will cause the code to read the lock-file and if the
process ID listed in it is no longer running, the lock-file will be
deleted.

"sleepTime" is the number of seconds between retries.  This can be
floating-point, as provided to "time.sleep()".
'''


class LockError(Exception):
    def __init__(self, *args):
        apply(Exception.__init__, (self,) + args)


class lock:
    def __init__(
            self, name, retries=0, tryBreak=True, doRaise=False,
            sleepTime=1):
        import os
        import time

        self.lockedByPid = None
        self.pid = str(os.getpid())
        self.lockFile = name
        self.lockFile2 = self.lockFile + '.' + self.pid
        self.haveLock = False
        self.sleepTime = sleepTime

        while not self.haveLock:
            if tryBreak and os.path.exists(self.lockFile):
                self.break_existing_lock()

            #  try to obtain the lock
            try:
                #  write our PID to our lock-file
                fp = open(self.lockFile2, 'w')
                fp.write('%s\n' % self.pid)
                fp.close()

                os.link(self.lockFile2, self.lockFile)
                self.haveLock = True
            except OSError:
                if retries > 0:
                    time.sleep(self.sleepTime)

            #  exit if we aren't supposed to wait
            if retries < 1:
                break
            retries = retries - 1

        if not self.haveLock:
            os.unlink(self.lockFile2)
            if doRaise:
                raise(LockError, "Unable to obtain lock")

    def break_existing_lock(self):
        import os
        import time

        self.lockedByPid = open(self.lockFile, 'r').readline().strip()
        try:
            self.lockedByPid = int(self.lockedByPid)
        except ValueError:
            self.lockedByPid = None
        try:
            if self.lockedByPid is not None:
                os.kill(int(self.lockedByPid), 0)
        except OSError:
            try:
                os.unlink(self.lockFile + '.' + self.lockedByPid)
            except OSError:
                pass
            try:
                os.unlink(self.lockFile)
            except OSError:
                pass
            time.sleep(self.sleepTime)

    def release(self):
        import os

        try:
            if os.path.exists(self.lockFile2):
                os.unlink(self.lockFile2)
            if self.haveLock and os.path.exists(self.lockFile):
                os.unlink(self.lockFile)
            self.haveLock = False
        except OSError:
            pass

    def __del__(self):
        self.release()
