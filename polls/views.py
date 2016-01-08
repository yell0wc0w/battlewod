from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from .models import AthleteProfile
from mysite.settings import VERSION

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
        try:
            athleteprofile = AthleteProfile.objects.get(name__icontains=athletename)
        except MultipleObjectsReturned:
            athleteprofile = AthleteProfile.objects.filter(name__icontains=athletename)[0]
        except ObjectDoesNotExist:
            athleteprofile = AthleteProfile.objects.filter(name__icontains='')[0]
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
        athleteprofile.save()

        #now return new value to page (perhaps DB call is not required? future optimization)
        context = {'stat_result': athleteprofile.get_stat_value(POST_data.get('id'))}
        html = 'polls/results.html'

    return render(request, html, context)