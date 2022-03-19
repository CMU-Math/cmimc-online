import queue
import concurrent.futures as futures
import grpc
import threading
import random
import os
import traceback
import json

from programming_grading.protos import coordinator_pb2_grpc, coordinator_pb2
from website.models import AIGame, Submission

class AIJob:
    def __init__(self, game):
        self.game = game
    def to_pb(self):
        game = AIGame.objects.get(pk=self.game)
        seats = sorted(game.aisubmissions.all(), key=lambda x: x.seat)
        return coordinator_pb2.GradeRequest(
            id=random.randrange(1000),
            timeout_seconds=600,
            op=coordinator_pb2.GradeOperation(
                python_code=game.aiproblem.code.encode(),
                input=json.dumps([
                    { 'code': seat.submission.text }
                    for seat in seats
                ]).encode()
            )
        )
    def on_graded(self, resp):
        game = AIGame.objects.get(pk=self.game)
        seats = sorted(game.aisubmissions.all(), key=lambda x: x.seat)
        if not resp.summary:
            game.status = 3
            game.save()
            return
        summary = json.loads(resp.summary)
        for i,seat in enumerate(seats):
            seat.score = summary[i]
            seat.save()
        game.status = 2
        game.history = json.loads(resp.output)
        game.save()
    @classmethod
    def find_games(cls, on_startup=False):
        base = []
        if on_startup:
            base += AIGame.objects.filter(status=1).all()
        base += AIGame.objects.filter(status=0).all()
        for x in base:
            x.status = 1
            x.save()
        return [cls(i.pk) for i in base]

class OptJob:
    def __init__(self, jid):
        self.id = jid
    def to_pb(self):
        sub = Submission.objects.get(pk=self.id)
        return coordinator_pb2.GradeRequest(
            id=random.randrange(1000),
            timeout_seconds=600,
            op=coordinator_pb2.GradeOperation(
                python_code=sub.problem.grader_code.encode(),
                input=json.dumps({
                    'code': sub.text,
                    'task': sub.task.raw_grader_data
                }).encode()
            )
        )
    def on_graded(self, resp):
        sub = Submission.objects.get(pk=self.id)
        sub.status = 2
        if not resp.summary:
            sub.status = 3
            sub.save()
            return
        sub.points = json.loads(resp.summary)
        sub.save()
    @classmethod
    def find_games(cls, on_startup=False):
        base = []
        if on_startup:
            base += Submission.objects.filter(status=1,task_id__isnull=False).all()
        base += Submission.objects.filter(status=0,task_id__isnull=False).all()
        for x in base:
            x.status = 1
            x.save()
        return [cls(i.pk) for i in base]

class GradeServer(coordinator_pb2_grpc.Coordinator):
    def __init__(self):
        super().__init__()
        self.request_queue = queue.SimpleQueue()
        self.authed = set()
    def SetPassword(self, pw, context):
        print('got connection from', context.peer())
        if pw.password == os.environ["CMIMC_GRPC_PASSWORD"]:
            self.authed.add(context.peer())
        return coordinator_pb2.Empty()
    def Serve(self, grade_response_iterator, context):
        if context.peer() not in self.authed:
            return
        current_request = None
        try:
            while True:
                current_request = self.request_queue.get()
                req_pb = current_request.to_pb()
                print('sending to', context.peer())
                yield req_pb
                grade_response = next(grade_response_iterator)
                print('recieved from', context.peer())
                assert req_pb.id == grade_response.id

                current_request.on_graded(grade_response)
                current_request = None
        except Exception as e:
            print(e)
        finally:
            if current_request is not None:
                self.request_queue.put(current_request)

def find_games_to_grade(startup=False):
    return AIJob.find_games(startup) + OptJob.find_games(startup)

def run_coordinator(port, ivl):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=200))
    coordinator = GradeServer()
    coordinator_pb2_grpc.add_CoordinatorServicer_to_server(coordinator, server)
    server.add_insecure_port(port)
    server.start()

    for item in find_games_to_grade(True):
        coordinator.request_queue.put(item)

    cancel = threading.Event()
    while not cancel.wait(ivl):
        for item in find_games_to_grade():
            coordinator.request_queue.put(item)
    
    threading.ThreadJob(target=repeatedly_query).start()

from django.core.management.base import BaseCommand, no_translations

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('grpc_port', type=str)
        parser.add_argument('refresh_ivl', type=float)
    @no_translations
    def handle(self, *args, **options):
        run_coordinator(options['grpc_port'], options['refresh_ivl'])
