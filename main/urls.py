from django.urls import path
from . import views
#app_name='main'
urlpatterns = [
path('report/',views.report,name='report'),
path('api/',views.sherlock_api,name='shelock_api'),
path('', views.index, name='main'),
]
