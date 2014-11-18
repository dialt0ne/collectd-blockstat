## collectd-blockstat

### Overview:

collectd-blockstat is a collectd plugin (written in Python) that reads the
Linux 2.6 /sys/block/&lt;device&gt;/stat "file" and records detailed device
statistics.

It is a superset of the "disk" plugin that ships with collectd. The main
difference is it records additional fields present in /sys/block/&lt;device&gt;/stat.

This plugin requires the collectd Python plugin, which was introduced in
collectd 4.9. To configure, drop the blockstat.py file into a directory
where collectd is configured to find Python modules (ModulePath param).

The plugin must be explicitly told which devices to monitor. This is done
by defining "Device" parameters inside the &lt;Module&gt; block for blockstat.
One "Device" parameter per device. To see which devices are available, just
`ls -1 /sys/block/*/stat`.

The plugin produces data for the "blockstat" plugin. The plugin instance
will be the device name. The plugin will write gauge data for 11 types.

The Linux kernel source code tree documentation 
[Documentation/block/stat.txt](https://www.kernel.org/doc/Documentation/block/stat.txt)
describes the fields in /sys/block/&lt;device&gt;/stat and can help you make sense
of the data.

### Example configuration:

```
  <Plugin python>
      ModulePath "/path/to/modules"
      Import "blockstat"

      <Module blockstat>
          Disk "sda"
          Disk "sda1"
      </Module>
  </Plugin>
```

### Thanks:

Many thanks to Gregory Szorc for his
[collectd-diskstats](https://github.com/indygreg/collectd-diskstats)
plugin for which this is based

### License:

Copyright 2014 Anthony Tonns

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

