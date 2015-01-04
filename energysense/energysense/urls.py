from django.conf.urls import patterns, include, url
# from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'energysense.views.home', name='home'),
    url(r'^login/$', 'accounts.views.login_user', name='login'),
    url(r'^logout/$', 'accounts.views.logout_user', name='logout'),
    url(r'^register/$', 'accounts.views.register', name='register'),
    url(r'^monitor/', include('monitor.urls', namespace='monitor')),
)
