#!/bin/bash

./remotetrace.py --trace_files ./systems/ceph/trace0 ./systems/ceph/trace1 ./systems/ceph/trace2 --machines p2-instance-group-2-8v1n p2-instance-group-2-c851 p2-instance-group-2-n0g3 --data_dirs /home/cephor/osd0 /home/cephor/osd1 /home/cephor/osd2 --workload_command ./systems/ceph/ceph_workload_read.py --ignore_file ./systems/ceph/ignore
