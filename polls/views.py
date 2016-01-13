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
        context = {'stat_result': athleteprofile.get_stat_value(POST_data.get('id'))}
        html = 'polls/results.html'

    return render(request, html, context)

def SeasonLadderView(request):
    context = {}
    html = 'polls/seasonladder.html'
    return render(request, html, context)

def WodEntryLadderView(request):
    POST_data = request.POST.dict()

    if ('warmup' in POST_data and POST_data.get('warmup') != ''):
        new_wod1 = WOD_list(wod_type='warmup', description=POST_data.get('warmup'), date=datetime.datetime.now())
        new_wod1.save()

    if ('strength' in POST_data and POST_data.get('warmup') != ''):
        new_wod2 = WOD_list(wod_type='strength', description=POST_data.get('strength'), date=datetime.datetime.now())
        new_wod2.save()

    if ('wod' in POST_data and POST_data.get('warmup') != ''):
        new_wod3 = WOD_list(wod_type='wod', description=POST_data.get('wod'), date=datetime.datetime.now())
        new_wod3.save()

    context = {}
    html = 'polls/wodentry.html'
    return render(request, html, context)