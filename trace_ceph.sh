#!/bin/bash

./remotetrace.py --trace_files ./systems/ceph/trace0 ./systems/ceph/trace1 ./systems/ceph/trace2 --machines p2-instance-group-1-139b p2-instance-group-1-6j90 p2-instance-group-1-jvj5 --data_dirs  /mnt/sdb/osd0 /mnt/sdb/osd1 /mnt/sdb/osd2 --workload_command ./systems/ceph/ceph_workload_read.py --ignore_file ./systems/ceph/ignore
