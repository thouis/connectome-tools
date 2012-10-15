import os
import sys
import glob
import subprocess
import shutil
import time

# include trailing slashes in paths
SSD_dir = '/cygdrive/v/LGNS1_Montages/'
Local_dir = '/cygdrive/e/MerlinDataBuffer/'
Remote_dir = '/cygdrive/z/joshm/LGNs1/rawMontages/'

def rsync(from_dir, to_dir, *args):
    result = subprocess.call(["/usr/bin/rsync",
                              "-a", "--chmod=Dg+rwx,Fg+rw"] + list(args) +
                             [from_dir,
                              to_dir])
    # subprocess.call("setfacl -m o::r-x".split(' ') + [to_dir])
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
        # Sync the Databuffer to the Remote
        print "Syncing %s to %s..." % (Local_dir, Remote_dir)
        success = rsync(Local_dir, Remote_dir, "-v", "-W", "--progress", "-h",
                        "--exclude=.*")
        if not success:
            print "Syncing Local to Remote sync failed.  Retrying..."

        delay()
