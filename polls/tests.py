from django.test import TestCase, Client
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
import unittest
from datetime import date, datetime

from .models import AthleteProfile, WOD_list

class AthleteProfileTest(TestCase):
    def setUp(self):
        new_athlete_profile = AthleteProfile(name='Hoang Ngo')
        new_athlete_profile.snatch_1rm = 145
        new_athlete_profile.backsquat_1rm = 0
        new_athlete_profile.save()
        new_athlete_profile = AthleteProfile(name='Louis-Philippe Merlini')
        new_athlete_profile.snatch_1rm = 225
        new_athlete_profile.save()
        new_athlete_profile = AthleteProfile(name='')
        new_athlete_profile.save()

        new_wod1 = WOD_list(wod_type='warmup', description='warmup1', date=date.today())
        new_wod1.save()
        new_wod2 = WOD_list(wod_type='strength', description='strength1', date=date.today())
        new_wod2.save()
        new_wod3 = WOD_list(wod_type='wod', description='wod1', date=date.today())
        new_wod3.save()

        new_wod4 = WOD_list(wod_type='warmup', description='new year warmup', date=date(2016, 1, 1))
        new_wod4.save()
        new_wod5 = WOD_list(wod_type='strength', description='new year strength', date=date(2016, 1, 1))
        new_wod5.save()
        new_wod6 = WOD_list(wod_type='wod', description='new year wod', date=date(2016, 1, 1))
        new_wod6.save()

    def test_search_and_find_valid_full_name_model_only(self):
        try:
            athleteprofile = AthleteProfile.objects.get(name__icontains='Hoang Ngo')
        except ObjectDoesNotExist:
            assert(False)

        assert(athleteprofile.name == 'Hoang Ngo')

    def test_search_and_find_valid_full_name_case_sensitive_model_only(self):
        try:
            athleteprofile = AthleteProfile.objects.get(name__icontains='hoang')
        except ObjectDoesNotExist:
            assert(False)

        assert(athleteprofile.name == 'Hoang Ngo')

    def test_search_and_find_partial_name_model_only(self):
        try:
            athleteprofile = AthleteProfile.objects.get(name__icontains='Hoan')
        except ObjectDoesNotExist:
            assert(False)

        assert(athleteprofile.name == 'Hoang Ngo')

    def test_search_and_find_success_using_POST(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/', {'athletename': 'Hoang'})
        assert(response.context['athleteprofile'].name == 'Hoang Ngo')

    def test_search_and_find_fail_using_POST(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/', {'athletename': 'Roger'})
        assert(response.context['athleteprofile'].name == '')

    def test_first_page_load_no_profile(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/', {'athletename': ''})
        assert(response.context['athleteprofile'].name == '')

    def test_changing_stats_value_success_using_POST(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/', {'athletename': 'Hoang Ngo', 'id': 'backsquat_1rm', 'value': '999'})
        assert(response.context['stat_result'] == 999)

    def test_changing_stats_text_in_int_field_fail_using_POST(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/', {'athletename': 'Hoang Ngo', 'id': 'backsquat_1rm', 'value': 'zzz'})
        assert(response.context['stat_result'] == 0)

    def test_version_is_present_in_page_using_POST(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/', {'athletename': 'Hoang'})
        assert(response.context['version'] != None)
        html_response_in_string = response.getvalue().decode("utf-8")
        assert(html_response_in_string.find('Currently using BattleWOD v') >= 0)

    def test_add_new_profile_happy_path_using_POST(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/', {'newathletename': 'Roger Bazinet New Client'})
        assert(response.context['athleteprofile'].name == 'Roger Bazinet New Client')

    def test_add_new_profile_duplicate_record_using_POST(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/', {'newathletename': 'mr.duplicate'})
        response = myClient.post('/battlewodapp/', {'newathletename': 'mr.duplicate'})

        try:
            athleteprofile = AthleteProfile.objects.get(name__contains='mr.duplicate')
        except MultipleObjectsReturned:
            assert(False)

    def test_cumulative_reads_using_POST(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/', {'athletename': 'Hoang Ngo'})
        response = myClient.post('/battlewodapp/', {'athletename': 'Hoang Ngo'})
        response = myClient.post('/battlewodapp/', {'athletename': 'Hoang Ngo'})
        assert(AthleteProfile.objects.get(name__contains='Hoang Ngo').cumulative_reads == 3)

    def test_cumulative_writes_using_POST(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/', {'athletename': 'Hoang Ngo', 'id': 'backsquat_1rm', 'value': '999'})
        response = myClient.post('/battlewodapp/', {'athletename': 'Hoang Ngo', 'id': 'backsquat_1rm', 'value': '999'})
        response = myClient.post('/battlewodapp/', {'athletename': 'Hoang Ngo', 'id': 'backsquat_1rm', 'value': '999'})
        assert(AthleteProfile.objects.get(name__contains='Hoang Ngo').cumulative_writes == 3)

    def test_wodentry_enter_good_wods_and_nothing_in_db(self):
        WOD_list.objects.filter(date__range=(date.today(), date.today())).delete()

        myClient = Client()
        response = myClient.post('/battlewodapp/wodentry', {'warmup': 'warmup1', 'strength': 'strength1', 'wod': 'wod1', 'date': date.today()})
        try:
            result = WOD_list.objects.filter(wod_type__icontains='warmup', date__range=(date.today(), date.today()))
            assert (result.count() == 1)

            result = WOD_list.objects.filter(wod_type__icontains='strength', date__range=(date.today(), date.today()))
            assert (result.count() == 1)

            result = WOD_list.objects.filter(wod_type__icontains='wod', date__range=(date.today(), date.today()))
            assert (result.count() == 1)

        except ObjectDoesNotExist:
            assert(False)

    def test_wodentry_invalid_payload(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/wodentry', {'warmup_bad': 'warmup1', 'strength': 'strength1', 'wod': 'wod1', 'date': date.today()})
        try:
            WOD_list.objects.filter(wod_type__icontains='warmup', date__range=(date.today(), date.today()))
        except MultipleObjectsReturned:
            assert(False)

        try:
            WOD_list.objects.filter(wod_type__icontains='strength')
            WOD_list.objects.filter(wod_type__icontains='wod')
        except ObjectDoesNotExist:
            assert(False)

    def test_wodentry_post_empty_textfields(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/wodentry', {'warmup': '', 'strength': '', 'wod': '', 'date': date.today()})

        wod_type_list = {'warmup', 'strength', 'wod'}

        for wod_type in wod_type_list:
            try:
                WOD_list.objects.filter(wod_type__icontains=wod_type, date__range=(date.today(), date.today()))
            except MultipleObjectsReturned:
                assert(False)

    def test_wodentry_enter_only_warmup(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/wodentry', {'warmup': 'warmup1', 'strength': '', 'wod': '', 'date': date.today()})
        try:
            WOD_list.objects.filter(wod_type__icontains='warmup')
        except ObjectDoesNotExist:
            assert(False)

    def test_wodentry_enter_only_strength(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/wodentry', {'warmup': '', 'strength': 'strength1', 'wod': '', 'date': date.today()})
        try:
            WOD_list.objects.filter(wod_type__icontains='strength')
        except ObjectDoesNotExist:
            assert(False)

    def test_wodentry_enter_only_wod(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/wodentry', {'warmup': '', 'strength': '', 'wod': 'wod1', 'date': date.today()})
        try:
            WOD_list.objects.filter(wod_type__icontains='wod')
        except ObjectDoesNotExist:
            assert(False)

    def test_wodentry_get_today_wod(self):
        myClient = Client()
        response = myClient.get('/battlewodapp/wodentry')
        assert(response.context['warmup_text'] == 'warmup1')
        assert(response.context['strength_text'] == 'strength1')
        assert(response.context['wod_text'] == 'wod1')

    def test_wodentry_get_today_wod_but_not_in_db(self):
        WOD_list.objects.filter(date__range=(date.today(), date.today())).delete()

        myClient = Client()
        response = myClient.get('/battlewodapp/wodentry')
        assert(response.context['warmup_text'] == '')
        assert(response.context['strength_text'] == '')
        assert(response.context['wod_text'] == '')

    def test_wodentry_get_particular_day_wod(self):
        myClient = Client()
        response = myClient.get('/battlewodapp/wodentry', {'date': date(2016, 1, 1)})
        assert(response.context['warmup_text'] == 'new year warmup')
        assert(response.context['strength_text'] == 'new year strength')
        assert(response.context['wod_text'] == 'new year wod')

    def test_wodentry_update_particular_day_wod(self):
        myClient = Client()
        response = myClient.post('/battlewodapp/wodentry', {'warmup': 'new warmup', 'strength': 'new strength', 'wod': 'new wod', 'date': date.today()})
        response = myClient.get('/battlewodapp/wodentry')
        assert(response.context['warmup_text'] == 'new warmup')
        assert(response.context['strength_text'] == 'new strength')
        assert(response.context['wod_text'] == 'new wod')

        result = WOD_list.objects.filter(date__range=(date.today(), date.today()), wod_type__exact='warmup')
        assert(result.count() == 1)

        result = WOD_list.objects.filter(date__range=(date.today(), date.today()), wod_type__exact='strength')
        assert(result.count() == 1)

        result = WOD_list.objects.filter(date__range=(date.today(), date.today()), wod_type__exact='wod')
        assert(result.count() == 1)
