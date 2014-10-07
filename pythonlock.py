#!/usr/bin/env python
#
#  Generic locking routines for Python

'''
Just select a lock-file name, and create a jlock instance using that
name any any parameters you want to override.  Then either let the
object fall out of scope or (preferred) call the "release()" method:

    import jlock
    lock = jlock.lock('/dev/shm/mylockfile', retries=100, do_raise=True)
    if not lock.have_lock:
        print "Didn't get lock"
        print "This shouldn't happen because do_raise is True"
        sys.exit(0)
    [do stuff]
    lock.release()

The lock sleeps for one second, so the above will wait for the lock for
100 seconds.  You can tune both of those settings.

"retries" is the number of attempts that will be made before the locking
code gives up trying to get the lock.

"do_raise" if raise an exception if the lock cannot be aquired.

"try_break" if set will cause the code to read the lock-file and if the
process ID listed in it is no longer running, the lock-file will be
deleted.

"sleep_time" is the number of seconds between retries.  This can be
floating-point, as provided to "time.sleep()".
'''

import os
import time


class LockError(Exception):
    def __init__(self, *args):
        apply(Exception.__init__, (self,) + args)


class lock:
    def __init__(
            self, name, retries=0, try_break=True, do_raise=False,
            sleep_time=1):
        #  imports
        self.locked_by_pid = None
        self.pid = str(os.getpid())
        self.lock_file = name
        self.lock_file2 = self.lock_file + '.' + self.pid
        self.have_lock = False
        self.sleep_time = sleep_time

        while not self.have_lock:
            if try_break and os.path.exists(self.lock_file):
                self.break_existing_lock()

            #  try to obtain the lock
            try:
                #  write our PID to our lock-file
                fp = open(self.lock_file2, 'w')
                fp.write('%s\n' % self.pid)
                fp.close()

                os.link(self.lock_file2, self.lock_file)
                self.have_lock = True
            except OSError:
                if retries > 0:
                    time.sleep(self.sleep_time)

            #  exit if we aren't supposed to wait
            if retries < 1:
                break
            retries = retries - 1

        if not self.have_lock:
            os.unlink(self.lock_file2)
            if do_raise:
                raise(LockError, "Unable to obtain lock")

    def break_existing_lock(self):
        self.locked_by_pid = open(self.lock_file, 'r').readline().strip()
        try:
            self.locked_by_pid = int(self.locked_by_pid)
        except ValueError:
            self.locked_by_pid = None
        try:
            if self.locked_by_pid is not None:
                os.kill(int(self.locked_by_pid), 0)
        except OSError:
            try:
                os.unlink(self.lock_file + '.' + self.locked_by_pid)
            except OSError:
                pass
            try:
                os.unlink(self.lock_file)
            except OSError:
                pass
            time.sleep(self.sleep_time)

    def release(self):
        try:
            if os.path.exists(self.lock_file2):
                os.unlink(self.lock_file2)
            if self.have_lock and os.path.exists(self.lock_file):
                os.unlink(self.lock_file)
            self.have_lock = False
        except OSError:
            pass

    def __del__(self):
        self.release()
