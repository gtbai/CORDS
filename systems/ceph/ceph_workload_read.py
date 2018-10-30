#!/usr/bin/env  python

import sys
import os
import time
import subprocess
import logging

remote_user_name = 'cephor'
cords_dir = '/home/cephor/CORDS/'
workload_home = cords_dir + '/systems/ceph/'
hosts = ['p2-instance-group-1-139b', 'p2-instance-group-1-6j90', 'p2-instance-group-1-jvj5']
CURR_DIR = os.path.dirname(os.path.realpath(__file__))

ceph_cluster_dir = '/home/cephor/my-cluster'

def invoke_cmd(cmd):
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, 	stderr=subprocess.PIPE)
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

def copy_file_to_remote(machine_ip, from_file_path, to_file_path):
	cmd = 'scp {0} {1}@{2}:{3}'.format(from_file_path, remote_user_name, machine_ip, to_file_path)
	os.system(cmd)
def copy_file_from_remote(machine_ip, from_file_path, to_file_path):
	cmd = 'scp {0}@{1}:{2} {3}'.format(remote_user_name, machine_ip, from_file_path, to_file_path)
	os.system(cmd)

# The CORDS framework passes the following arguments to the workload program
# ceph_workload_read.py trace/cords workload_dir1 workload_dir2 .. workload_dirn [log_dir]
# For now assume only 3 nodes
assert len(sys.argv) >= 5
osd_data_dirs = []
for i in range(2, 5):
    osd_data_dirs.append(sys.argv[i])

log_dir = None
#if logdir specified
if len(sys.argv) >= 6:
	log_dir = sys.argv[-1]

# Kill all ceph osds on remote nodes
for host_idx, host in enumerate(hosts):
    kill_cmd = 'sudo stop ceph-osd id={0};'.format(host_idx)
    kill_cmd += 'sleep 1s'
    run_remote(host, kill_cmd)

os.system('sleep 10s')

# Generate ceph.conf and update cluster conf
update_conf_cmd = 'cd ' + ceph_cluster_dir + ';'
update_conf_cmd += 'mv ceph.conf ceph.conf.backup;'
update_conf_cmd += 'cp ceph.conf.base ceph.conf;'
for host_idx in range(len(hosts)):
    update_conf_cmd += 'echo "[osd.{0}]" >> ceph.conf;'.format(host_idx)
    update_conf_cmd += 'echo "osd_data = {0}" >> ceph.conf;'.format(osd_data_dirs[host_idx])
update_conf_cmd += 'ceph-deploy --overwrite-conf config push '
for host in hosts:
    update_conf_cmd += host + ' '
print(update_conf_cmd)
os.system(update_conf_cmd)

os.system('cd ' + CURR_DIR)

# Start 3 osds in the ceph cluster.
for host_idx, host in enumerate(hosts):
    start_cmd = 'sudo start ceph-osd id={0};'.format(host_idx)			
    start_cmd += 'sleep 1s;'
    run_remote(host, start_cmd)

os.system('sleep 10s')

out, err = '', ''

# Get state of ceph osds before reading data
if log_dir is not None:
    out, err = invoke_cmd('sudo ceph osd tree')
    client_log_file = os.path.join(log_dir, 'log-client')
    with open(client_log_file, 'w') as f:
        f.write(out)
        f.write('----------------------------------------------\n')

out, err = '', ''

present_value = 'a' * 8192 
os.system('rm -f read_output.txt')

# Issue read requests on ceph osds and check its value
try:
    os.system('sudo rados get -p cords_test_pool cords_test_obj read_output.txt')
    read_output_f = open('read_output.txt', 'r') 
    read_output = read_output_f.read()
    is_proper = str(read_output == present_value)
    read_output_f.close()
    out += 'Get succeeded, Proper: ' + is_proper + '\n'
except Exception as e:
    err += 'Get failed: ' + str(e)

print out
print err

# Get state of ceph osds after reading data
if log_dir is not None:
    out, err = invoke_cmd('sudo ceph osd tree')
    client_log_file = os.path.join(log_dir, 'log-client')
    with open(client_log_file, 'a') as f:
        f.write(out)
        f.write('----------------------------------------------\n')

# Kill all ceph osds on remote nodes
for host_idx, host in enumerate(hosts):
    kill_cmd = 'sudo stop ceph-osd id={0};'.format(host_idx)
    kill_cmd += 'sleep 1s'
    run_remote(host, kill_cmd)

os.system('sleep 10s')

