from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from .models import AthleteProfile, WOD_list
from mysite.settings import VERSION
import datetime

def AthleteView(request):
    # Handle text input, as needed
    athletename = ''
    newathletename = ''
    POST_data = request.POST.dict()
    GET_data = request.GET.dict()
    context = {}

    if request.method == 'POST':
        if POST_data.get('id') is None:

            if request.method == 'POST':
                athletename = POST_data.get('athletename')
                newathletename = POST_data.get('newathletename')

            # Create new profile as needed
            if newathletename is not None:
                if (AthleteProfile.objects.filter(name__iexact=newathletename).count() == 0):
                    new_athlete_profile = AthleteProfile(name=newathletename)
                    new_athlete_profile.save()
                    athletename = newathletename
                else:
                    athletename = newathletename

            # Preparation of rendering screen
            if athletename == '':
                athleteprofile = AthleteProfile.objects.get(name__iexact='')
            else:
                try:
                    athleteprofile = AthleteProfile.objects.get(name__icontains=athletename)
                except MultipleObjectsReturned:
                    athleteprofile = AthleteProfile.objects.filter(name__icontains=athletename)[0]
                except ObjectDoesNotExist:
                    athleteprofile = AthleteProfile.objects.get(name__iexact='')

            # keep track of analytics
            athleteprofile.cumulative_reads += 1
            athleteprofile.save(update_fields=['cumulative_reads'])

            day_criteria = datetime.date.today()
            context = {'athleteprofile': athleteprofile, 'version': VERSION}
            html = 'polls/index.html'

        elif POST_data.get('id') is not None:
            #retrieve profile
            athletename = POST_data.get('athletename')

            try:
                athleteprofile = AthleteProfile.objects.get(name__icontains=athletename)
            except MultipleObjectsReturned:
                athleteprofile = AthleteProfile.objects.filter(name__icontains=athletename)[0]

            athleteprofile.setup_stats()

            #save data in DB
            if POST_data.get('value').isdigit():
                athleteprofile.set_stat_value(POST_data.get('id'), int(POST_data.get('value')))
            else:
                athleteprofile.set_stat_value(POST_data.get('id'), POST_data.get('value'))

            athleteprofile.presave_stats()
            # keep track of analytics
            athleteprofile.cumulative_writes += 1
            athleteprofile.save()

            #now return new value to page (perhaps DB call is not required? future optimization)
            day_criteria = datetime.date.today()
            context = {'stat_result': athleteprofile.get_stat_value(POST_data.get('id'))}
            html = 'polls/results.html'

    elif request.method == 'GET':
        if GET_data.get('date') == None:
            day_criteria = datetime.date.today()
        else:
            day_criteria = datetime.datetime.strptime(GET_data.get('date'), "%Y-%m-%d").date()

        html = 'polls/index.html'

    context = load_wod_in_context(context, WOD_list, day_criteria)
    context['date_text'] = day_criteria.strftime('%Y-%m-%d')

    return render(request, html, context)

def SeasonLadderView(request):
    context = {}
    html = 'polls/seasonladder.html'
    return render(request, html, context)

def WodEntryLadderView(request):

    context = {'warmup_text': '', 'strength_text': '', 'wod_text' : '', 'date_text': ''}

    if (request.method == 'GET'):
        GET_data = request.GET.dict()

        if GET_data.get('date') == None:
            day_criteria = datetime.date.today()
        else:
            day_criteria = datetime.datetime.strptime(GET_data.get('date'), "%Y-%m-%d").date()

    elif (request.method == 'POST'):
        POST_data = request.POST.dict()

        wods_on_that_day = WOD_list.objects.filter(date__range=(POST_data.get('date'), POST_data.get('date')))

        if wods_on_that_day.count() == 0:
            if ('warmup' in POST_data and POST_data.get('warmup') != ''):
                new_wod1 = WOD_list(wod_type='warmup', description=POST_data.get('warmup'), date=POST_data.get('date'))
                new_wod1.save()

            if ('strength' in POST_data and POST_data.get('strength') != ''):
                new_wod2 = WOD_list(wod_type='strength', description=POST_data.get('strength'), date=POST_data.get('date'))
                new_wod2.save()

            if ('wod' in POST_data and POST_data.get('wod') != ''):
                new_wod3 = WOD_list(wod_type='wod', description=POST_data.get('wod'), date=POST_data.get('date'))
                new_wod3.save()
        else:
            for wod in wods_on_that_day:
                if (wod.wod_type == 'warmup') and POST_data.get('warmup') != '' and POST_data.get('warmup') is not None:
                    wod.description = POST_data.get('warmup')
                elif (wod.wod_type == 'strength') and POST_data.get('strength') != '' and POST_data.get('strength') is not None:
                    wod.description = POST_data.get('strength')
                elif (wod.wod_type == 'wod') and POST_data.get('wod') != '' and POST_data.get('wod') is not None:
                    wod.description = POST_data.get('wod')
                wod.save()

        day_criteria = datetime.datetime.strptime(POST_data.get('date'), "%Y-%m-%d").date()

    context = load_wod_in_context(context, WOD_list, day_criteria, show_present_and_future_trainings=True)

    context['date_text'] = day_criteria.strftime('%Y-%m-%d')
    html = 'polls/wodentry.html'

    return render(request, html, context)


def load_wod_in_context(context, WOD_list, day_criteria, show_present_and_future_trainings=False):
    if WOD_list.objects.filter(date__range=(day_criteria, day_criteria)).count() > 0:
        if day_criteria < datetime.date.today() or show_present_and_future_trainings:
            for wod in WOD_list.objects.filter(date__range=(day_criteria, day_criteria)):
                if wod.wod_type == 'warmup':
                    context['warmup_text'] = wod.description
                elif wod.wod_type == 'strength':
                    context['strength_text'] = wod.description
                elif wod.wod_type == 'wod':
                    context['wod_text'] = wod.description
        else:
            context['warmup_text'] = 'Hidden'
            context['strength_text'] = 'Hidden'
            context['wod_text'] = 'Hidden'

    return context
