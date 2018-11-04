#!/usr/bin/env python

import sys
import os
import time
import subprocess
import logging

remote_user_name = 'cephor'
workload_home= '/home/cephor/CORDS/systems/ceph/'

hosts = ['p2-instance-group-2-8v1n', 'p2-instance-group-2-c851', 'p2-instance-group-2-n0g3']

def invoke_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return (out, err)

def invoke_remote_cmd(machine_ip, command):
    cmd = 'ssh {0}@{1} \'{2}\''.format(remote_user_name, machine_ip, command)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 	stderr=subprocess.PIPE)
    out, err = p.communicate()
    return (out, err)

def run_remote(machine_ip, command):
    cmd = 'ssh {0}@{1} \'{2}\''.format(remote_user_name, machine_ip, command)
    os.system(cmd)

def copy_file_remote(machine_ip, from_file_path, to_file_path):
    cmd = 'scp {0} {1}@{2}:{3}'.format(from_file_path, remote_user_name, machine_ip, to_file_path)
    os.system(cmd)

# Create a clean start state
# Kill ceph OSDs.
# Delete CORDS trace files
# Delete ceph workload directories
# Create workload directories
for host_idx, host in enumerate(hosts):
    clear_cmd = 'sudo stop ceph-osd id={0};'.format(host_idx)
    clear_cmd += 'rm -rf {0}/debuglogs;'.format(workload_home)
    clear_cmd += 'rm -rf {0}/trace*;'.format(workload_home)
    clear_cmd += 'rm -rf {0}/workload_dir{1}*;'.format(workload_home, host_idx)
    clear_cmd += 'sleep 1s;'
    clear_cmd += 'mkdir -p {0}/debuglogs/{1};'.format(workload_home, host_idx)
    clear_cmd += 'mkdir -p {0}/workload_dir{1};'.format(workload_home, host_idx)
    run_remote(host, clear_cmd)

# Stop ceph MONs.
for host_idx, host in enumerate(hosts):
    stop_mon_cmd = 'sudo stop ceph-mon id={0};'.format(host)
    run_remote(host, stop_mon_cmd)

os.system('sleep 10s')
print 'After stopping 1st time:'
# os.system('sudo ceph osd tree')

# Start ceph MONs.
for host_idx, host in enumerate(hosts):
    start_mon_cmd = 'sudo start ceph-mon id={0};'.format(host)
    run_remote(host, start_mon_cmd)

# Start all daemons in the ceph cluster.
for host_idx, host in enumerate(hosts):
    start_cmd = 'sudo start ceph-osd id={0};'.format(host_idx)			
    start_cmd += 'sleep 1s;'
    run_remote(host, start_cmd)

os.system('sleep 10s')
print 'After starting 1st time:'
os.system('sudo ceph osd tree')

delete_file_cmd = 'sudo rados rm -p cords_test_pool cords_test_obj;'
delete_file_cmd += 'sleep 2s;'
delete_file_cmd += 'sudo ceph osd pool delete cords_test_pool cords_test_pool --yes-i-really-really-mean-it'
os.system(delete_file_cmd)

os.system('sleep 10s')

# Create a test file, write it into ceph object cluster.
write_file_cmd = 'echo -n ' + 'a'*8192 + ' > cords_test_file.txt &&'
write_file_cmd += 'sudo ceph osd pool create cords_test_pool 100 100 &&'
write_file_cmd += 'sudo rados put cords_test_obj cords_test_file.txt --pool=cords_test_pool'
os.system(write_file_cmd)

# Stop all ceph OSDs.
for host_idx, host in enumerate(hosts):
    kill_cmd = 'sudo stop ceph-osd id={0};'.format(host_idx)
    kill_cmd += 'sleep 1s'
    run_remote(host, kill_cmd)

# Stop ceph MONs.
for host_idx, host in enumerate(hosts):
    stop_mon_cmd = 'sudo stop ceph-mon id={0};'.format(host)
    run_remote(host, stop_mon_cmd)

print 'After stopping 2nd time:'
os.system('sleep 10s')
# os.system('sudo ceph osd tree')
