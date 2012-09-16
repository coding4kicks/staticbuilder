#!/usr/bin/env python

import subprocess
import os

import staticbuilder

def test():
    """Test harness for static builder.
    
       Checks SB both as imported object and command line utility.
       Test paths must be set up correctly:
       (TODO: UPDATE correct structure here or readme?)
    """

    # TEST COMMAND LINE
    print "Testing SB from the command line"

    # Test bad local path.
    print "Testing bad local path"
    cmd = "python staticbuilder.py \
           ~/projects/staticbuilder/sb_test_bucket/file0.txt"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 2

    # Test invalid location.
    print "Testing bad local path"
    cmd = "python staticbuilder.py \
           -p invalid_location \
           ~/projects/staticbuilder/sb_test_bucket"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 2

    # Test that an absolute file path in works.
    print "Testing single in path, absolute."
    cmd = "python staticbuilder.py \
           /Users/scottyoung/projects/staticbuilder/sb_test_bucket/testfile0.txt"
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

    # Test for a single directory in
    print "Testing single directory in - no recursion"
    cmd = "python staticbuilder.py \
           sb_test_bucket"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test for a single sub directory recursive
    print "Testing single directory in - with recursion"
    cmd = "python staticbuilder.py -r \
           sb_test_bucket/testdir1"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test a directory with out path - not recursive
    print "Testing directory - no recursion"
    cmd = "python staticbuilder.py \
           sb_test_bucket/testdir1/testdir2 \
           sb_test_bucket/testdir1/testdir2"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test a directory with out path - recursive
    print "Testing directory - with recursion"
    cmd = "python staticbuilder.py -r \
           sb_test_bucket/testdir1/testdir2 \
           sb_test_bucket/testdir1/testdir2"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test deletion of a file 
    print "Testing deletion of a file"
    cmd = "python staticbuilder.py -f \
           -d sb_test_bucket/testfile0.txt"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test deletion of a directory 
    print "Testing deletion of a file"
    cmd = "python staticbuilder.py -f -r \
           -d sb_test_bucket/testdir1"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test no arguments - should upload cwd
    print "Testing no arguments - no recursion"
    os.chdir("sb_test_bucket")
    cmd = "python ../staticbuilder.py"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test no arguments with recursion
    print "Testing no arguments - with recursion"
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
    print "Testing option -l sb_test_bucket/testdir1 (list all keys in directory)"
    cmd = "python staticbuilder.py -l sb_test_bucket/testdir1"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test rename with too few arguments errors
    print "Testing option -n with 0 args"
    cmd = "python staticbuilder.py -n new_name.txt"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 2

    # Test rename with too many arguments errors
    print "Testing option -n with 3 args"
    cmd = "python staticbuilder.py -N new_name.text file1.txt file2.txt path/out "
    ret = subprocess.call(cmd, shell=True)
    assert ret == 2

    # Test rename
    print "Testing option -n (rename)"
    cmd = "python staticbuilder.py --name new_name.txt sb_test_bucket/testfile0.txt"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    # Test metadata
    print "Testing option -m (metadata)"
    cmd = "python staticbuilder.py -m kick:ass sb_test_bucket/metadata.txt"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0
  
    # Test acl
    print "Testing option -a (acl)"
    cmd = "python staticbuilder.py -a public-read sb_test_bucket/public.txt"
    ret = subprocess.call(cmd, shell=True)
    assert ret == 0

    print "Complete SB test from command line."

    ##########################################

    # TEST OBJECT
    print "Testing SB as an object"

#    options = None

#    sb = StaticBuilder(options) 

#    # Test bad local path.
#    print "Testing bad local path"
#    cmd = "python staticbuilder.py \
#           ~/projects/staticbuilder/sb_test_bucket/file0.txt"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 2
#
#    # Test invalid location.
#    print "Testing bad local path"
#    cmd = "python staticbuilder.py \
#           -p invalid_location \
#           ~/projects/staticbuilder/sb_test_bucket"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 2
#
#    # Test that an absolute file path in works.
#    print "Testing single in path, absolute."
#    cmd = "python staticbuilder.py \
#           /Users/scottyoung/projects/staticbuilder/sb_test_bucket/testfile0.txt"
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
#    # Test for a single directory in
#    print "Testing single directory in - no recursion"
#    cmd = "python staticbuilder.py \
#           sb_test_bucket"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test for a single sub directory recursive
#    print "Testing single directory in - with recursion"
#    cmd = "python staticbuilder.py -r \
#           sb_test_bucket/testdir1"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test a directory with out path - not recursive
#    print "Testing directory - no recursion"
#    cmd = "python staticbuilder.py \
#           sb_test_bucket/testdir1/testdir2 \
#           sb_test_bucket/testdir1/testdir2"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test a directory with out path - recursive
#    print "Testing directory - with recursion"
#    cmd = "python staticbuilder.py -r \
#           sb_test_bucket/testdir1/testdir2 \
#           sb_test_bucket/testdir1/testdir2"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test deletion of a file 
#    print "Testing deletion of a file"
#    cmd = "python staticbuilder.py -f \
#           -d sb_test_bucket/testfile0.txt"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test deletion of a directory 
#    print "Testing deletion of a file"
#    cmd = "python staticbuilder.py -f -r \
#           -d sb_test_bucket/testdir1"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test no arguments - should upload cwd
#    print "Testing no arguments - no recursion"
#    os.chdir("sb_test_bucket")
#    cmd = "python ../staticbuilder.py"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test no arguments with recursion
#    print "Testing no arguments - with recursion"
#    cmd = "python ../staticbuilder.py -R"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test list bad bucket name
#    print "Testing option -l buckets (list buckets)"
#    os.chdir("..")
#    cmd = "python staticbuilder.py -l no_bucket"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 2
#
#    # Test that SB can list all buckets
#    print "Testing option -l buckets (list buckets)"
#    cmd = "python staticbuilder.py -l buckets"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test that SB can list all keys in a bucket
#    print "Testing option -l sb_test_bucket (list all keys in bucket)"
#    cmd = "python staticbuilder.py -l sb_test_bucket"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test that SB can list filtered keys
#    print "Testing option -l sb_test_bucket/testdir1 (list all keys in directory)"
#    cmd = "python staticbuilder.py -l sb_test_bucket/testdir1"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test rename with too few arguments errors
#    print "Testing option -n with 0 args"
#    cmd = "python staticbuilder.py -n new_name.txt"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 2
#
#    # Test rename with too many arguments errors
#    print "Testing option -n with 3 args"
#    cmd = "python staticbuilder.py -N new_name.text file1.txt file2.txt path/out "
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 2
#
#    # Test rename
#    print "Testing option -n (rename)"
#    cmd = "python staticbuilder.py --name new_name.txt sb_test_bucket/testfile0.txt"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#
#    # Test metadata
#    print "Testing option -m (metadata)"
#    cmd = "python staticbuilder.py -m kick:ass sb_test_bucket/metadata.txt"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0
#  
#    # Test acl
#    print "Testing option -a (acl)"
#    cmd = "python staticbuilder.py -a public-read sb_test_bucket/public.txt"
#    ret = subprocess.call(cmd, shell=True)
#    assert ret == 0

    print "Complete SB test from command line."

if __name__ == "__main__":

    test()
