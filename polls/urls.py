from django.conf.urls import url
from . import views

app_name = 'polls'

urlpatterns = [
    url(r'^main', views.AthleteView, name='index'),
    url(r'^seasonladder', views.SeasonLadderView, name='seasonladder'),
    url(r'^wodentry', views.WodEntryLadderView, name='wodentry'),
    url(r'^', views.AthleteView, name='index'),

]