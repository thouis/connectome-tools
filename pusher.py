import os
import sys
import glob
import subprocess
import shutil
import time

# include trailing slashes in paths
SSD_dir = '/cygdrive/v/LGNS1_Montages/'
Local_dir = '/cygdrive/f/LGNS1_Montages/'
Remote_dir = '/cygdrive/x/joshm/LGNs1/rawMontages/'

def rsync(from_dir, to_dir, *args):
    result = subprocess.call(["/usr/bin/rsync",
                              "-a",] + list(args) +
                             [from_dir,
                              to_dir])
    return (result == 0)  # zero exit on success

def delay():
    # Wait 60 seconds
    print "Sleeping for 60 seconds",
    sys.stdout.flush()
    for i in range(6):
        time.sleep(10)
        print "...%d" % (60 - ((i + 1) * 10)),
        sys.stdout.flush()
    print ""


if __name__ == '__main__':
    while True:
        # Search the SSD for directories that have finished
        finished_files = glob.glob(os.path.join(SSD_dir, '*', 'finished.mat'))
        finished_dirs = [os.path.dirname(f) for f in finished_files]
        if finished_dirs:
            print "Will remove these directories after verifying checksums:"
            print "    ", "\n    ".join(finished_dirs)

        # First, sync the SSD to the Local
        print "Syncing %s to %s..." % (SSD_dir, Local_dir)
        success = rsync(SSD_dir, Local_dir, "-q")
        if not success:
            print "Syncing SSD to Local sync failed.  Retrying, not removing anything."
            delay()
            continue

        # Then, sync the SSD to the Remote
        print "Syncing %s to %s..." % (SSD_dir, Remote_dir)
        success = rsync(SSD_dir, Remote_dir, "-q")
        if not success:
            print "Syncing SSD to Remote sync failed.  Retrying, not removing anything."
            delay()
            continue

        # Then, resync the SSD to any finished directories, but use checksumming
        # instead of size and modification time.
        for d in finished_dirs:
            remote_subdir = os.path.join(Remote_dir, os.path.split(d)[1])
            "Checksum-based sync of %s to %s..." % (d, remote_subdir)
            success = rsync(d, remote_subdir, "-c", "-vv")
            if not success:
                print "    Sync failed, not removing %s" % (d)
            else:
                print "    Removing %s" % (d)
                try:
                    # shutil.rmtree(d)
                    print "Would remove %s" % d
                except:
                    print "Could not remove finished directory %d" % (d)

        delay()
