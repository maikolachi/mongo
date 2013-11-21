#!/usr/bin/env python
#
# Public Domain 2008-2013 WiredTiger, Inc.
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#

import csv, os, zipimport
from subprocess import call

# Python script to read wtperf monitor output and create a performance
# graph.

TIMEFMT = "%b %d %H:%M:%S"

# Read the monitor file and figure out when checkpoint was running.
in_ckpt = 'N'
ckptlist=[]
with open('monitor', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
	if row[4] != in_ckpt:
	    ckptlist.append(row[0])
	    in_ckpt = row[4]

# Write a command file for gnuplot.
of = open("gnuplot.cmd", "w")
of.write('''
set terminal png nocrop
set autoscale
set grid
set style data lines
set datafile sep ','
set timefmt "%H:%M:%S"
set title "wtperf run"
set format x "%M:%S"
set xlabel "Time (minutes:seconds)"
set xtics rotate by -45
set xdata time
set ylabel "Thousands of operations per second"
set yrange [0:]\n''')

it = iter(ckptlist)
for start, stop in zip(it, it):
	of.write('set object rectangle from first \'' + start +\
	    '\', graph 0 ' + ' to first \'' + stop +\
	    '\', graph 1 fc rgb "gray" back\n')

of.write('''
set output 'monitor.png'
plot "monitor" using 1:($2/1000) title "Reads", "monitor" using 1:($3/1000) title "Updates", "monitor" using 1:($4/1000) title "Inserts"\n''')

of.close()
call(["gnuplot", "gnuplot.cmd"])
os.remove("gnuplot.cmd")
