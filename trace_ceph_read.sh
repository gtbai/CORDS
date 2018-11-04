#!/bin/bash

./remotetrace.py --trace_files ./systems/ceph/trace0 ./systems/ceph/trace1 ./systems/ceph/trace2 --machines p2-instance-group-3-6d9j p2-instance-group-3-h85p p2-instance-group-3-pf4g --data_dirs /home/cephor/osd0 /home/cephor/osd1 /home/cephor/osd2 --workload_command ./systems/ceph/ceph_workload_read.py --ignore_file ./systems/ceph/ignore
