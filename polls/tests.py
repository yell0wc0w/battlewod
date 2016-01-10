from django.test import TestCase, Client
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
import unittest

from .models import AthleteProfile

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
