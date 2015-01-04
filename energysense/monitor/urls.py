from django.conf.urls import patterns, url
from monitor import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^home_iframe/', views.home_iframe, name = 'home_iframe'),
    url(r'^data$', views.data, name='data'),
    url(r'^linewithfocuschart/', views.linewithfocuschart, name='linewithfocuschart'),
)