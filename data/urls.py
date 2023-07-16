from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
# router.register()
router.register('profile', views.ProfileViewSet)
router.register('tweets', views.TweetViewSet)
router.register('ratings', views.RatingViewSet, basename='ratings')
router.register('recommendations', views.RecommendationsViewSet, basename='recommendations')


tweets_router = routers.NestedDefaultRouter(router, 'tweets', lookup='tweet')
tweets_router.register('ratings', views.RatingViewSet, basename='tweet-ratings')

# router.register('all-tweets', views.AllTweetsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(tweets_router.urls)),
    path('recommendations_page/', views.recommendations_page, name='recommendations_page'),
    # path('check-bing-api/', views.checkBingApi.as_view(), name='check-bing-api'),
    # path('check-twitter-api/', views.checkTwitterApi.as_view(), name='check-twitter-api'),
    # path('popular-twitter-accounts/', views.PopularTwitterAccounts.as_view(), name='popular-twitter-accounts'),
    # path('specific-twitter-accounts/', views.SpecificTwitterAccountTweets.as_view(), name='specific-twitter-accounts'),
    # path('view-all-tweets/', views.ViewAllTweets.as_view(), name='view-all-tweets'),
]