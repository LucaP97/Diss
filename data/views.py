from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter 
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
import requests
import tweepy
import json
import boto3
import os
from .serializers import *
from .models import *
from config import *

class ProfileViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        profile = Profile.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = ProfileSerializer(profile, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        
class ProfileRegistrationViewSet(CreateModelMixin, GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileRegistrationSerializer

        

class RatingViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'put']

    def get_queryset(self):
        return Rating.objects.filter(tweet_id=self.kwargs['tweet_pk'])

    def get_permissions(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return RatingSimpleSerializer
        return RatingSerializer
    
    def get_serializer_context(self):
        return {'tweet_id': self.kwargs['tweet_pk'], 'user_id': self.request.user.id}
    


class TweetViewSet(ModelViewSet):
    http_method_names = ['get', 'post']
    
    queryset = Tweets.objects.all().prefetch_related('ratings')
    serializer_class = TweetSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['created_at', 'sentiment']
    search_fields = ['text', 'key_phrases', 'entities']
    
    pagination_class = PageNumberPagination



###################
# Recommendations
###################


## SVD
class SVDRecommendationsViewSet(ModelViewSet):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
            return SVDRecommendations.objects.filter(user=self.request.user).prefetch_related('tweet__ratings')

    serializer_class = SVDRecommendationSerializer


## Hybrid
class HybridRecommendationsViewSet(ModelViewSet):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return HybridRecommendations.objects.filter(user=self.request.user).prefetch_related('tweet__ratings')

    serializer_class = HybridRecommendationSerializer


## KNN
class KNNRecommendationsViewSet(ModelViewSet):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return KNNRecommendations.objects.filter(user=self.request.user).prefetch_related('tweet__ratings')

    serializer_class = KNNRecommendationSerializer


## TFRS
class TFRSRecommendationsViewSet(ModelViewSet):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TFRSRecommendations.objects.filter(user=self.request.user).prefetch_related('tweet__ratings')

    serializer_class = TFRSRecommendationSerializer