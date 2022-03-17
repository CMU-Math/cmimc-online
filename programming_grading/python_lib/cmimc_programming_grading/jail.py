# nsjail-based jail impl

import typing as T
import subprocess
import tempfile
import os
import signal
from pathlib import Path

base_config_loc = Path(__file__).parent / "base_nsjail_config.cfg"
nsjail_loc = "nsjail"
cgroup_mount = Path("/sys/fs/cgroup")
wrapper_loc = "/bin/wait_on_cork"

class JailProc:
    def __init__(self, p, cork_fd, cputime):
        self.p = p
        cgroup_path = None
        with open(f"/proc/{p.pid}/cgroup") as f:
            cg_prefix = "0::"
            for line in f:
                line = line.strip()
                if line.startswith(cg_prefix):
                    #cgroup_path = line.stripprefix(cg_prefix)
                    pass
        #assert(cgroup_path is not None)
        #self.cgroup = cgroup_mount / cgroup_path
        #self.freeze()
        #os.eventfd_write(cork_fd, 1)
        #os.close(cork_fd)
    def freeze(self):
        return
        with open(self.cgroup / "cgroup.freeze", 'w') as f:
            f.write("1")
    def unfreeze(self):
        return
        with open(self.cgroup / "cgroup.freeze", 'w') as f:
            f.write("0")

class Jail:
    def __init__(self):
        self.procs = []
        self.dir = tempfile.TemporaryDirectory()
        self.dir.__enter__()
    def destroy(self):
        for proc in self.procs: proc.kill()
        self.dir.__exit__()
    def start_process(self, argv, cputime=0, walltime=0, memlimit=0):
        #cork_fd = os.eventfd(0, flags=0) # we want the cork fd to be inheirited
        cork_fd = 0
        proc = subprocess.Popen(
            args=[nsjail_loc,
                "-x", str(base_config_loc),
                "-B", str(self.dir.name) + ":/app",
                "--cgroup_mem_max", str(memlimit),
                "--rlimit_cpu_time", str(memlimit),
                "-t", str(int(walltime)),
                # "--pass_fd", str(cork_fd),
                "--"] + argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.procs.append(proc)
        return JailProc(proc, cork_fd=cork_fd, cputime=cputime)
    def write_file(self, name, contents):
        with open(Path(self.dir.name) / name, 'w') as f:
            f.write(contents)

# implement a codebox on top of the jail

from threading import Timer
from .local_test_framework import *

default_config = {
    "timeout": 1, # wall-time timeout for a given query in seconds
    "cputime": 10, # total cpu time given to the program
    "walltime": 60, # total wall time the program is allowed to run
    "memlimit": 256 << 20, # memory limit in bytes
}

class Codebox(AbstractCodebox):
    def __init__(self, player, config):
        super().__init__()
        self.config = {**config, **default_config}
        self.player = player
        self.timer_killed = False
    @classmethod
    def of_player_config(cls, code, config):
        return cls(code['code'], config)
    def initialize_box(self):
        self.jail = Jail()
        self.jail.write_file("me.py", self.player)
        self.proc = self.jail.start_process(
            argv=["python3", Path(self.jail.dir.name) / "me.py"],
            cputime = self.config["cputime"],
            walltime = self.config["walltime"],
            memlimit = self.config["memlimit"])
    def destroy_box(self):
        self.jail.destroy()
    def write_raw(self, data):
        # TODO: cgroup timeouts?
        self.proc.unfreeze()
        self.proc.p.stdin.write(data)
        self.proc.p.stdin.flush()
        self.proc.freeze()
    def read_raw(self):
        self.proc.unfreeze()
        line = self.proc.p.stdout.readline()
        self.proc.freeze()
        return line

CodeboxClass.append(Codebox)