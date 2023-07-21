from celery import shared_task
from django.core import management
from django.db import transaction
from .models import SVDRecommendations, KNNRecommendations, HybridRecommendations, TFRSRecommendations

@shared_task
def generate_SVD_recommendations_task():
    with transaction.atomic():
        SVDRecommendations.objects.all().delete()
        management.call_command('generate_svd_recommendations')

@shared_task
def generate_KNN_recommendations_task():
    with transaction.atomic():
        KNNRecommendations.objects.all().delete()
        management.call_command('generate_KNN_recommendations')

@shared_task
def generate_Hybrid_recommendations_task():
    with transaction.atomic():
        HybridRecommendations.objects.all().delete()
        management.call_command('generate_hybrid_recommendations')

@shared_task
def generate_TFRS_recommendations_task():
    with transaction.atomic():
        TFRSRecommendations.objects.all().delete()
        management.call_command('generate_TFRS_recommendations')