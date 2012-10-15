import os
import sys
import glob
import subprocess
import shutil
import time
import traceback

def filesize(path):
    if os.path.exists(path):
        return os.stat(path).st_size
    return 0

def newer(path1, path2):
    '''True is path1 is newer than path2, or path2 does not exist.'''
    if not os.path.exists(path2):
        return True
    return os.stat(path1).st_mtime > os.stat(path2).st_mtime

def dup_mtime(path1, path2):
    '''Sets path2's modification time from path1's modification time.'''
    st = os.stat(path1)
    os.utime(path2, (st.st_atime, st.st_mtime))

def dup_file(src, dest):
    '''duplicate a file, its modification time, and set its permissions to something reasonable.'''
    shutil.copyfile(src, dest)
    dup_mtime(src, dest)
    os.chmod(dest, 0770 if os.access(src, os.X_OK) else 0660)

def duplicate_dir(src, dest):
    oldpath = os.getcwd()
    try:
        # work in source directory
        os.chdir(src)
        for (dirpath, subdirs, files) in os.walk('.'):
            # duplicate any files that are out of date
            for f in files:
                if f.startswith('.'):
                    continue
                sourcefile = os.path.join(dirpath, f)
                destfile = os.path.join(oldpath, dest, dirpath, f)
                sourcefile_size = filesize(sourcefile)
                if ((sourcefile_size != filesize(destfile)) or
                    newer(sourcefile, destfile)):
                    t1 = time.time()
                    dup_file(sourcefile, destfile)
                    dt = time.time() - t1
                    bandwidth = (sourcefile_size / dt) / (1024 * 1024)
                    print "Copied %s, %0.02f MB in %d sec, %0.02f MB/s" % \
                        (sourcefile, sourcefile_size / (1024.0 * 1024), dt, bandwidth)
            # note that this directory can be deleted
            if 'finished.mat' in files:
                yield os.path.join(oldpath, src, dirpath)
            # create any missing directories
            for sd in subdirs:
                destdir = os.path.join(oldpath, dest, dirpath, sd)
                if not os.path.exists(destdir):
                    os.mkdir(destdir, 0770)
    finally:
        os.chdir(oldpath)

def delay():
    # Wait 60 seconds
    print "Sleeping for 60 seconds",
    sys.stdout.flush()
    for i in range(6):
        time.sleep(10)
        print ""
        return
        print "...%d" % (60 - ((i + 1) * 10)),
        sys.stdout.flush()
    print ""

if __name__ == '__main__':
    while True:
        try:
            removable_dirs = [d for d in duplicate_dir(sys.argv[1], sys.argv[2])]
            for d in removable_dirs:
                print "REMOVING", d
        except Exception, e:
            traceback.print_exc()
        delay()

