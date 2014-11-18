#  Copyright 2014 Anthony Tonns
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# This plugin reads data from /sys/block/<device>/stat
#
# It will only work on Linux 2.6
#
# To configure the plugin, you must specify the devices to monitor.
# The plugin takes a param 'Disk' whose string value is the exact
# device name. This param can be defined multiple times.
#
# e.g.
#
#<Plugin python>
#    ModulePath "/path/to/modules"
#    Import "blockstat"
#
#    <Module blockstat>
#        Device sda
#        Device sda1
#    </Module>
#</Plugin>
#
# The fields in /sys/block/<device>/stat are documented in
# the Linux kernel source code.
# https://www.kernel.org/doc/Documentation/block/stat.txt
#
# code borrows heavily from Gregory Szorc's diskstats collectd plugin
# https://github.com/indygreg/collectd-diskstats
#

import collectd
import os.path

field_map = {
    0: 'read_ios',
    1: 'read_merges',
    2: 'read_sectors',
    3: 'read_ticks',
    4: 'write_ios',
    5: 'write_merges',
    6: 'write_sectors',
    7: 'write_ticks',
    8: 'in_flight',
    9: 'io_ticks',
    10: 'time_in_queue'
}
devices = []
previous_values = {}


def blockstat_config(c):
    if c.values[0] != 'blockstat':
        return
    for child in c.children:
        if child.key == 'Device':
            for v in child.values:
                if v not in devices:
                    devices.append(v)
                    if v not in previous_values:
                        previous_values[v] = {}


def blockstat_read(data=None):
    # if no devices to monitor, do nothing
    if not len(devices):
        return
    for device in devices:
        statspath = "/sys/block/{0}/stat".format(device)
        # skip devices that don't exist
        if not os.path.exists(statspath):
            collectd.warning(
                'path %s not found' % (statspath)
            )
            continue
        fh = open(statspath, 'r')
        values = collectd.Values(type='gauge', plugin='blockstat')
        for line in fh:
            line = line.lstrip()
            fields = line.split()
            if len(fields) != 11:
                collectd.warning(
                    'format of %s not recognized: %s' % (statspath, line)
                )
                continue
            for i in range(0, 10):
                value = int(fields[i])
                # if this is the first value, simply record
                # and move on to next field
                if i not in previous_values[device]:
                    previous_values[device][i] = value
                    continue
                # else we have a previous value
                previous_value = previous_values[device][i]
                delta = None
                # we have wrapped around
                if previous_value > value:
                    delta = 4294967296 - previous_value + value
                else:
                    delta = value - previous_value
                # field 9 is not a counter
                if i == 9:
                    delta = value
                # record the new previous value
                previous_values[device][i] = value
                values.dispatch(
                    plugin_instance=device,
                    type_instance=field_map[i],
                    values=[delta],
                )
        fh.close()

collectd.register_read(blockstat_read)
collectd.register_config(blockstat_config)
