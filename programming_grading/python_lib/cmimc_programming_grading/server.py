import argparse
import time
import queue
import traceback
import grpc
import os
import sys
import json

import cmimc_programming_grading.protos.coordinator_pb2 as coordinator_pb2
import cmimc_programming_grading.protos.coordinator_pb2_grpc as coordinator_pb2_grpc
import subprocess
from tempfile import TemporaryDirectory
from pathlib import Path

def grade(request):
    print("grading", request)
    response = coordinator_pb2.GradeResponse(id=request.id)
    try:
        with TemporaryDirectory() as tempd:
            d = Path(tempd)
            pygrader = d / "grader.py"
            with open(pygrader, "wb") as f:
                f.write(request.op.python_code)

            proc = subprocess.run(
                args=[sys.executable, pygrader],
                capture_output=True,
                input=request.op.input)
            
            print(proc.stderr.decode())
            data = json.loads(proc.stdout)
            response.output = json.dumps(data['history']).encode()
            response.summary = json.dumps(data['summary']).encode()
            #response.playerlogs = json.dumps(data['playerlogs']).encode()
            print("got", response)
    except Exception as e:
        #print(traceback.format_exc(e))
        print(e)
    return response

import multiprocessing as mp

def server_thread(args, result_queue, request_queue):
    while 1:
        print("Connecting...")
        try:
            channel = grpc.insecure_channel(args.host)
            stub = coordinator_pb2_grpc.CoordinatorStub(channel)

            def get_next_res():
                res = coordinator_pb2.GradeResponse()
                res.ParseFromString(result_queue.get())
                print('sent', res)
                return res

            print('Sending password...')
            stub.SetPassword(coordinator_pb2.Password(password=os.environ["CMIMC_GRPC_PASSWORD"]))

            print('Successfully connected...')
            for grade_request in stub.Serve(iter(get_next_res, None)):
                request_queue.put(grade_request.SerializeToString())
        except Exception as e:
            #print(traceback.format_exc(e))
            print(e)
        print("Sleeping...")
        time.sleep(30)


def main():
    parser = argparse.ArgumentParser(description='CMIMC programming grading client')
    parser.add_argument('host', type=str, help='CMIMC server host')
    args = parser.parse_args()

    result_queue = mp.SimpleQueue()
    request_queue = mp.SimpleQueue()
    serverthread = mp.Process(target=server_thread,args=(args,result_queue,request_queue))
    serverthread.start()

    def get_next_req():
        req = coordinator_pb2.GradeRequest()
        req.ParseFromString(request_queue.get())
        return req

    for req in iter(get_next_req, None):
        result_queue.put(grade(req).SerializeToString())

if __name__ == "__main__":
    main()
