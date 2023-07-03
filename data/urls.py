from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
# router.register()

urlpatterns = [
    path('', include(router.urls)),
    path('check-bing-api/', views.checkBingApi.as_view(), name='check-bing-api'),
    path('check-twitter-api/', views.checkTwitterApi.as_view(), name='check-twitter-api'),
    path('popular-twitter-accounts/', views.PopularTwitterAccounts.as_view(), name='popular-twitter-accounts'),
    path('specific-twitter-accounts/', views.SpecificTwitterAccountTweets.as_view(), name='specific-twitter-accounts'),
]