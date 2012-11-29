from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #(r'^djadmin/', include(admin.site.urls)),
    #(r'^djadmin/doc/', include('django.contrib.admindocs.urls')),
    #(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'django/login.html'}),
    (r'^admin/', include('billy.web.admin.urls')),
    (r'^api/', include('billy.web.api.urls')),
    (r'^', include('billy.web.public.urls')),
)
