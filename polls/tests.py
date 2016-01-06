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

    def test_search_and_find_valid_full_name_model_only(self):
        try:
            athleteprofile = AthleteProfile.objects.get(name__contains='Hoang Ngo')
        except ObjectDoesNotExist:
            assert(False)

        assert(athleteprofile.name == 'Hoang Ngo')

    @unittest.expectedFailure
    def test_search_and_find_valid_full_name_case_sensitive_model_only(self):
        try:
            athleteprofile = AthleteProfile.objects.get(name__contains='hoang ngo')
        except ObjectDoesNotExist:
            assert(False)

        assert(athleteprofile.name == 'Hoang Ngo')

    def test_search_and_find_partial_name_model_only(self):
        try:
            athleteprofile = AthleteProfile.objects.get(name__contains='Hoan')
        except ObjectDoesNotExist:
            assert(False)

        assert(athleteprofile.name == 'Hoang Ngo')

    def test_search_and_find_success_using_POST(self):
        myClient = Client()
        response = myClient.post('/polls/', {'athletename': 'Hoang'})
        assert(response.context['athleteprofile'].name == 'Hoang Ngo')

    @unittest.expectedFailure
    def test_search_and_find_fail_using_POST(self):
        myClient = Client()
        response = myClient.post('/polls/', {'athletename': 'Roger'})
        assert(response.context['athleteprofile'].name == '')

    def test_changing_stats_value_success_using_POST(self):
        myClient = Client()
        response = myClient.post('/polls/', {'athletename': 'Hoang Ngo', 'id': 'backsquat_1rm', 'value': '999'})
        assert(response.context['stat_result'] == 999)

    def test_changing_stats_text_in_int_field_fail_using_POST(self):
        myClient = Client()
        response = myClient.post('/polls/', {'athletename': 'Hoang Ngo', 'id': 'backsquat_1rm', 'value': 'zzz'})
        assert(response.context['stat_result'] == 0)

