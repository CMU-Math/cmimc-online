from django.shortcuts import render
from background_task import background
import datetime
from .faq import general_faq, math_faq, programming_faq
from .mini_events import math_events
from django.template import Template, Context

def home(request):
    return render(request, 'general/home.html')

def math_info(request):
    return render(request, 'general/math_info.html')

def math_rules(request):
    return render(request, 'general/math_rules.html')

def math_sample_problems(request):
    return render(request, 'general/math_sample_problems.html')

def math_schedule(request):
    return render(request, 'general/math_schedule.html')

def math_mini_events(request):
    context = {
        'math_events': math_events,
    }
    return render(request, 'general/math_mini_events.html', context)

def prog_info(request):
    return render(request, 'general/prog_info.html')

def prog_sample_problems(request):
    return render(request, 'general/prog_sample_problems.html')

def prog_schedule(request):
    return render(request, 'general/prog_schedule.html')

def cmwmc_info(request):
    return render(request, 'general/cmwmc_info.html')

def cmwmc_format(request):
    return render(request, 'general/cmwmc_format.html')

def cmwmc_schedule(request):
    return render(request, 'general/cmwmc_schedule.html')

def cmwmc_sample_problems(request):
    return render(request, 'general/cmwmc_sample_problems.html')

def cmwmc_mini_events(request):
    return render(request, 'general/cmwmc_mini_events.html')


def reg_info(request):
    return render(request, 'general/reg_info.html')


def faq_entry(i, d, s):
    return {
        'id': f'{s}-{i}',
        'question': d['question'],
        'answer': Template(d['answer']).render(Context()),
    }

def faq(request):
    glist = [faq_entry(i,d,'general') for i,d in enumerate(general_faq)]
    mlist = [faq_entry(i,d,'math') for i,d in enumerate(math_faq)]
    plist = [faq_entry(i,d,'programming') for i,d in enumerate(programming_faq)]

    context = {
        'glist': glist,
        'mlist': mlist,
        'plist': plist,
    }
    return render(request, 'general/faq.html', context)

def prog_mini_events(request):
    return render(request, 'general/prog_mini_events.html')

def resources(request):
    return render(request, 'general/resources.html')

def updates(request):
    return render(request, 'general/updates.html')
