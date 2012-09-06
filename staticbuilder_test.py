#!/usr/bin/env python

import subprocess
import os

def test():
    """Test harness for static builder.
    
       Checks SB both as imported object and command line utility.
       Test paths must be set up correctly:
       sb_test_bucket -> testfile0.txt, testdir1 -> 
       testfile1.txt, testdir2 -> testfile3.txt (TODO: UPDATE)
    """

    print "Testing SB from the command line"

    # Test that with no argument, SB copies the current directory.
    #print "Testing with no arguments."

#    # Test bad local path.
#    print "Testing bad local path"
#    cmd = "python staticbuilder.py \
#           ~/projects/staticbuilder/sb_test_bucket/file0.txt"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 2
#
#    # Test that an absolute file path in works.
#    print "Testing single in path, absolute."
#    cmd = "python staticbuilder.py \
#           ~/projects/staticbuilder/sb_test_bucket/testfile0.txt"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test that a relative file path in works.
#    print "Testing single in path, relative."
#    cmd = "python staticbuilder.py \
#           sb_test_bucket/testdir1/testfile1.txt"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test that out path works.
#    print "Testing out path."
#    cmd = "python staticbuilder.py \
#           sb_test_bucket/testdir1/testfile1.txt sb_test_bucket"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test that two in-paths work.
#    print "Testing two in paths."
#    cmd = "python staticbuilder.py \
#           sb_test_bucket/testfile2in1.txt \
#           sb_test_bucket/testfile2in2.txt \
#           sb_test_bucket"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test that three in-paths work - no more after this!.
#    print "Testing three in paths."
#    cmd = "python staticbuilder.py \
#           sb_test_bucket/testdir1/testfile3in1.txt \
#           sb_test_bucket/testdir1/testfile3in2.txt \
#           sb_test_bucket/testfile3in3.txt \
#           sb_test_bucket/testdir1/"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test a directory - not recursive
#    print "Testing directory - no recursion"
#    cmd = "python staticbuilder.py \
#           sb_test_bucket/testdir1/testdir2 \
#           sb_test_bucket/testdir1/"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0

#    # Test a directory - recursive
#    print "Testing directory - with recursion"
#    cmd = "python staticbuilder.py -r \
#           sb_test_bucket/testdir1/testdir2 \
#           sb_test_bucket/testdir1/"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0

    # Test no arguments - should upload cwd
    print "Testing no arguments"
    os.chdir("sb_test_bucket")
    #precmd = "cd sb_test_bucket"
    #subprocess.call(precmd, shell=True)
    cmd = "python ../staticbuilder.py"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0


    #print "Testing no upload of unchanged content."

    # TODO - add options and tests

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
