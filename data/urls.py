from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
# router.register()
router.register('profile', views.ProfileViewSet, basename='profile')
router.register('register', views.ProfileRegistrationViewSet, basename='register')
router.register('tweets', views.TweetViewSet)
router.register('ratings', views.RatingViewSet, basename='ratings')
router.register('svd_recommendations', views.SVDRecommendationsViewSet, basename='svd_recommendations')
router.register('hybrid_recommendations', views.HybridRecommendationsViewSet, basename='hybrid_recommendations')
router.register('knn_recommendations', views.KNNRecommendationsViewSet, basename='knn_recommendations')
router.register('tfrs_recommendations', views.TFRSRecommendationsViewSet, basename='tfrs_recommendations')


tweets_router = routers.NestedDefaultRouter(router, 'tweets', lookup='tweet')
tweets_router.register('ratings', views.RatingViewSet, basename='tweet-ratings')

# router.register('all-tweets', views.AllTweetsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(tweets_router.urls)),
]