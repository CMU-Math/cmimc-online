# framework for running the graders on our machines locally

import json
import typing as T
from contextlib import ExitStack
import random

REPLAY_DIR = "replays" # relative to here, will be mkdired

# interfaces

CodeboxClass = []

class AbstractCodebox:
    class HistoryEntry(T.NamedTuple):
        event: T.Literal['read', 'write', 'exit', 'restart']
        kind: T.Literal['ok', 'skipped', 'error']
        details: T.Optional[str]
    
    def __init__(self):
        self.hist = []
        self.keep_log = True
        self.alive = False

    def log(self, **kwargs):
        if self.keep_log: self.hist.append(self.HistoryEntry(**kwargs))

    def interaction_log(self):
        return self.hist
    
    def kill(self):
        if self.alive:
            self.alive = False
            self.destroy_box()
            err = self.get_stderr().strip()
            if err:
                self.log(event='exit', kind='error', details=str(err))
    
    def restart(self):
        self.kill()
        self.initialize_box()
        self.alive = True
        self.log(event='restart', kind='ok', details=None)
    
    def write(self, data):
        if not self.alive:
            self.log(event='write', kind='skipped', details=None)
            return
        dumped = json.dumps(data)
        try:
            self.write_raw(dumped.encode() + b"\n")
            self.log(event='write', kind='ok', details=dumped)
        except Exception as e:
            self.log(event='write', kind='error', details=str(e))
            self.kill()
        
    def read(self):
        if not self.alive:
            self.log(event='read', kind='skipped', details=None)
            return
        try:
            line = self.read_raw().strip()
            self.log(event='read', kind='ok', details=str(line))
            data = json.loads(line)
            return data
        except Exception as e:
            self.log(event='read', kind='error', details=str(e))
            self.kill()

    def __enter__(self):
        self.initialize_box()
        self.alive = True
        return self

    def __exit__(self, *args):
        self.kill()
        return False

def do_save_replay(game_name, replay_name, score, data):
    import os, time
    file_name = os.path.join(REPLAY_DIR, f"{game_name}_{int(time.time())}_{score}_{replay_name}.json")
    with open(file_name, "w") as f:
        f.write(json.dumps(data))

class OptGrader:
    def grade(self, inp, codebox):
        if inp['seed'] is None:
            inp['seed'] = random.randrange(1 << 30)

        with codebox.of_player_config(code=inp['code'], config=self.config) as cb:
            random.seed(inp['seed'])
            return self.optgrade(inp['gen'], cb)

    def test(self, source, gen, name="", save_replay=False, seed=None, record_logs=False):
        player = {'code': open(source).read(), 'src_loc': source}

        if seed is None: seed = random.randrange(1 << 30)
        result = self.grade({'gen': gen, 'code': player, 'seed': seed}, Codebox)
        if not record_logs: del result['playerlogs']

        if save_replay:
            do_save_replay(self.name.lower(), name, result['summary'], result)
        else:
            print(result)
    
    def run(self):
        data = json.loads(input())
        task = json.loads(data['task'])
        gens = self.get_batch(task['gen'])
        res = [self.grade({ 'gen': gen, 'seed': seed, 'code': { 'code': data['code'] }}, CodeboxClass[0]) for gen,seed in gens]

        print(json.dumps({
            'summary': sum(r['summary'] for r in res) / len(res),
            'history': [r['history'] for r in res],
            'playerlogs': [r['playerlogs'] for r in res],
        }))

class AIGrader:
    def grade(self, inp, codebox_cls):
        with ExitStack() as stack:
            players = [
                stack.enter_context(codebox_cls.of_player_config(
                    code=player,
                    config=self.config))
                for player in inp]
            result = self.aigrade(players)
        return result

    def test(self, sources, name="", save_replay=True, record_logs=False):
        players = [{'code': open(src_loc).read(), 'src_loc': src_loc} for src_loc in sources]
        result = self.grade(players, Codebox)
        if not record_logs: del result['playerlogs']
        if save_replay:
            do_save_replay(self.name.lower(), name, max(x for x in result['summary']), result)
        else:
            print(result)
        
    def run(self):
        print(json.dumps(self.grade(json.loads(input()), CodeboxClass[0])))

# sample competitor implementation, just runs file in place

import subprocess
import sys
from threading import Timer

class Codebox(AbstractCodebox):
    def __init__(self, src_loc, config):
        super().__init__()
        self.config = config
        self.src_loc = src_loc
        self.timer_killed = False

    @classmethod
    def of_player_config(cls, code, config):
        return cls(code['src_loc'], config)

    def timer_kill(self):
        self.proc.kill()
        self.timer_killed = True

    def write_raw(self, data):
        try:
            t = Timer(self.config['timeout'], lambda: self.timer_kill())
            t.start()
            self.proc.stdin.write(data)
            self.proc.stdin.flush()
        finally:
            t.cancel()
            if self.timer_killed: raise Exception("timed out")
    def read_raw(self):
        try:
            t = Timer(self.config['timeout'], lambda: self.timer_kill())
            t.start()
            return self.proc.stdout.readline()
        finally:
            t.cancel()
            if self.timer_killed: raise Exception("timed out")
    def get_stderr(self):
        return self.proc.stderr.read()
    def initialize_box(self):
        self.proc = subprocess.Popen(
            [sys.executable, self.src_loc],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            )
    def destroy_box(self):
        self.proc.kill()
