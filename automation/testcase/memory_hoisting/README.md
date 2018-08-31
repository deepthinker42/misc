# Memory Hoisting Automated test

## Tests

### Free

    The following tests are run against the output of "free":
    1) Make sure the amount of memory reported by free matches what is calculated with that of
       the -n and -g parameters

### BIOS-e820

    The following tests are run against the BIOS-e820 section of the dmesg output:
    1) Make sure address range 0x0 - 0x9ffff is marked usable
    2) Make sure address range 0xa0000 - 0xfffff is marked reserved
    3) Make sure address range starting with 0x100000 is marked usable

### SRAT

    The following tests are run against the SRAT section of the dmesg output:
    1) Make sure address ranges less than 0x100000000 are contiguous (no holes)
    2) Make sure the hole before address 0x100000000 (4GB) is hoisted above 4GB
    3) Make sure the hole before address 0x10000000000 (1TB) is hoisted above 1TB
    4) Make sure that all NUMA nodes are the same size
    
## Launching from the command line

    ./memory_hoisting.py -h

    usage: memory_hoisting.py [-h] [-c {1,2}] [-d {1,2}] [-n {1,2,4,8,16,32}]
                              [-g {4,8,16,32,64}] [-i {None,chipset,channel}]
                              [-f DMESG] [-F FREE] [-u USERNAME] [-s SUT]

    Memory Hoisting Test

    optional arguments:
      -h, --help            show this help message and exit
      -c {1,2}, --cpus {1,2}
                            Number of CPUs (default: 1)
      -d {1,2}, --dpcs {1,2}
                            Number of DPCs (default: 1)
      -n {1,2,4,8,16,32}, --chips {1,2,4,8,16,32}
                            Number of memory chips installed (default: 2)
      -g {4,8,16,32,64}, --gb {4,8,16,32,64}
                            Size in GB of each memory chip (default: 8)
      -i {None,chipset,channel}, --interleave {None,chipset,channel}
                            Interleave (default: None)
      -f DMESG, --dmesg DMESG
                            Path to output of dmesg
      -F FREE, --free FREE  Path to output of free
      -u USERNAME, --username USERNAME
                            Username for ssh to SUT (only valid with -s)
      -s SUT, --sut SUT     SUT from which to get dmesg outut (only valid with -u)


    If "-s SUT" is used, then it is assume that ssh keys have been exchanged with <username>@<sut> since this
    program will automatically get the output of "free" and "dmesg" from the sut.
