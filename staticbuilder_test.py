#!/usr/bin/env python

import subprocess
import os

def test():
    """Test harness for static builder.
    
       Checks SB both as imported object and command line utility.
       Test paths must be set up correctly:
       (TODO: UPDATE correct structure here or readme?)
    """

    print "Testing SB from the command line"

    # Test bad local path.
    print "Testing bad local path"
    cmd = "python staticbuilder.py \
           ~/projects/staticbuilder/sb_test_bucket/file0.txt"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 2

    # Test that an absolute file path in works.
    print "Testing single in path, absolute."
    cmd = "python staticbuilder.py \
           ~/projects/staticbuilder/sb_test_bucket/testfile0.txt"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test that a relative file path in works.
    print "Testing single in path, relative."
    cmd = "python staticbuilder.py \
           sb_test_bucket/testdir1/testfile1.txt"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test that out path works.
    print "Testing out path."
    cmd = "python staticbuilder.py \
           sb_test_bucket/testdir1/testfile1.txt sb_test_bucket"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test that two in-paths work.
    print "Testing two in paths."
    cmd = "python staticbuilder.py \
           sb_test_bucket/testfile2in1.txt \
           sb_test_bucket/testfile2in2.txt \
           sb_test_bucket"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test that three in-paths work - no more after this!.
    print "Testing three in paths."
    cmd = "python staticbuilder.py \
           sb_test_bucket/testdir1/testfile3in1.txt \
           sb_test_bucket/testdir1/testfile3in2.txt \
           sb_test_bucket/testfile3in3.txt \
           sb_test_bucket/testdir1/"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test a directory - not recursive
    print "Testing directory - no recursion"
    cmd = "python staticbuilder.py \
           sb_test_bucket/testdir1/testdir2 \
           sb_test_bucket/testdir1/testdir2"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test a directory - recursive
    print "Testing directory - with recursion"
    cmd = "python staticbuilder.py -r \
           sb_test_bucket/testdir1/testdir2 \
           sb_test_bucket/testdir1/testdir2"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test no arguments - should upload cwd
    print "Testing no arguments"
    os.chdir("sb_test_bucket")
    cmd = "python ../staticbuilder.py"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test no arguments with recursion
    print "Testing no arguments"
    #os.chdir("sb_test_bucket")
    cmd = "python ../staticbuilder.py -R"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test list bad bucket name
    print "Testing option -l buckets (list buckets)"
    os.chdir("..")
    cmd = "python staticbuilder.py -l no_bucket"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 2

    # Test that SB can list all buckets
    print "Testing option -l buckets (list buckets)"
    cmd = "python staticbuilder.py -l buckets"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test that SB can list all keys in a bucket
    print "Testing option -l sb_test_bucket (list all keys in bucket)"
    cmd = "python staticbuilder.py -l sb_test_bucket"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test that SB can list filtered keys
    print "Testing option -l sb_test_bucket/testdir1 \
           (list all keys in directory)"
    cmd = "python staticbuilder.py -l sb_test_bucket/testdir1"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    #print "Testing no upload of unchanged content."

    # TODO - add options and tests

    # Kinda Need ability to rename files
    # Don't use config, use environmental variables.

    # Test that SB can create a website profile ***
    #print "Testing option -w (--website)."

    # Test that SB can delete a file/directory *** 
    # Use boto to delete key or bucket,
    # but SB could delete a folder recursively
    #print "Testing option -d (--delete)."


    # Test that SB can view and set ACLs
    #print "Testing option -a (--access)

    # Test that SB can place file in a different region ***
    # Must be able to pull from config file (bashrc)
    #print "Testing option -p (--place)."

    # Test that SB can view and set meta data
    #print "Testing option -m (metadata)."

    # Test that SB can view and set cross origin resource sharing 
    #print "Testing option -c (cors)."

    # Test that SB can force overwrite files
    #print "Testing option -f (force)."

    print "Complete SB test from command line."


if __name__ == "__main__":

    test()
