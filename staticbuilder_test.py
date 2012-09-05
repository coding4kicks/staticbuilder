#!/usr/bin/env python

import subprocess

def test():
    """Test harness for static builder.
    
       Checks SB both as imported object and command line utility.
       Test paths must be set up correctly:
       sb_test_bucket -> testfile0.txt, testdir1 -> 
       testfile1.txt, testdir2 -> testfile3.txt
    """

    print "Testing SB from the command line"

    # Test that with no argument, SB copies the current directory.
    #print "Testing with no arguments."

    # Test bad local path.
    #print "Testing bad local path"
    #cmd = "python staticbuilder.py \
    #       ~/projects/staticbuilder/sb_test_bucket/file0.txt"
    #ret = subprocess.call(cmd, shell=True)
    #assert ret == 2

    # Test that an absolute file path in works.
    print "Testing single in path, absolute."
    cmd = "python staticbuilder.py \
           ~/projects/staticbuilder/sb_test_bucket/testfile0.txt"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test that a relative file path in works.
    #print "Testing single in path, relative."
    #cmd = "python staticbuilder.py \
    #       sb_test_bucket/testdir1/testfile1.txt"
    #ret = subprocess.call(cmd, shell=True)
    #assert ret == 0

    # Test that out path works.
    #print "Testing out path."
    #cmd = "python staticbuilder.py \
    #       sb_test_bucket/testdir1/testfile1.txt sb_test_bucket"
    #ret = subprocess.call(cmd, shell=True)
    #assert ret == 0


    # Test that two in paths work.
    #print "Testing in path only, relative."
    #cmd = "python staticbuilder.py \
    #       sb_test_bucket/testfile0.txt sb_test_bucket/testfile00.txt"
    #ret = subprocess.call(cmd, shell=True)
    #assert ret == 0




    #print "Testing in and out path, out path relative."

    #print "Testing no upload of unchanged content."

    # TODO - add options and tests

    # Test that SB recursively copies files
    #print "Testing option -r (recursive)."

    # Test that SB can create a website profile
    #print "Testing option -w (website)."

    # Test that SB can delete a file/directory
    #print "Testing option -d (delete)."

    # Test that SB can list all buckets
    #print "Testing option -l (list).

    # Test that SB can view and set ACLs
    #print "Testing option -a (acl)

    # Test that SB can put/place in a different region 
    #print "Testing option -p (place/region)."

    # Test that SB can view and set meta data
    #print "Testing option -m (metadata)."

    # Test that SB can view and set cross origin resource sharing 
    #print "Testing option -c (cors)."

    # Test that SB can force overwrite files
    #print "Testing option -f (force)."

    print "Complete SB test from command line."



if __name__ == "__main__":

    test()
