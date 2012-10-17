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
                              "-a", "--chmod=Dug+rwx,Fug+rw"] + list(args) +
                             [from_dir,
                              to_dir])
    return (result == 0)  # zero exit on success

def write_md5s(path):
    try:
        tif_files = glob.glob(os.path.join(path, "*.tif"))
        md5subproc = subprocess.Popen(["/usr/bin/md5sum"] + tif_files,
                                      stdout=subprocess.PIPE)
        stdout, stderr = md5subproc.communicate()
        f = open(os.path.join(path, "MD5_CHECKSUMS.txt"), "w")
        f.write(stdout)
        f.close()
    except Exception, e:
        print "Could not write MD5 checksums", e

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

        # Then, resync the SSD to any finished directories, but use checksumming
        # instead of size and modification time.
        for d in finished_dirs:
            databuffer_subdir = os.path.join(Local_dir, os.path.split(d)[1], '')
            success = rsync(os.path.join(d, ''), databuffer_subdir, "-v", "-W", "--progress", "-h")
            # Create md5 checksums for every .tif file in the finished directories
            write_md5s(databuffer_subdir)
            if not success:
                print "    Sync failed, not removing %s" % (d)
            else:
                print "    Removing %s" % (d)
                try:
                    shutil.rmtree(d)
                except:
                    print "Could not remove finished directory %d" % (d)

        # sync the SSD to the Local
        print "Syncing %s to %s..." % (SSD_dir, Local_dir)
        success = rsync(SSD_dir, Local_dir, "-v", "-W", "--progress", "-h")
        if not success:
            print "Syncing SSD to Local sync failed.  Retrying."

        delay()
