Lock-file routines for Python.  This code is a cleaned up version from
some internal tummy.com projects, called "jlock.py", but never released
separately.  That code has been used in many projects over the years.

This code is meant to be easily embedded within some other code, just
by reading it into the other source file.  This is 50% of how I've
used it.

Examples
--------

Just select a lock-file name, and create a "lock" instance using that
name any any parameters you want to override.  Then either let the
object fall out of scope or (preferred) call the "release()" method:

    import pythonlock
    lock = pythonlock.lock('/dev/shm/mylockfile', retries=100, do_raise=True)
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
