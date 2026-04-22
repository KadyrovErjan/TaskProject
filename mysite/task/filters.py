from django_filters import FilterSet
from .models import *

class TopicFilter(FilterSet):
    class Meta:
        model = Topic
        fields = {
        'title':['exact'],
        # 'price':['gt','lt']

        }