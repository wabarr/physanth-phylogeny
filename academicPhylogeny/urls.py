from django.conf.urls import patterns, include, url
from academicPhylogeny.views import *
from academicPhylogeny.sitemap.sitemap import sitemaps
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(r'^$', home, name='home'),
    url(r'^featured/$', featured, name='featured'),
    url(r'^about/$', about, name='about'),
    #url(r'^connections/', connections_JSON, name="connections"),
    url(r'^email_user/$', emailUser),
    url(r'^contact/$', contact_to_db),
    url(r'^submit/$', userSubmitData, name='submit'),
    url(r'^people/$', people, name='people'),
    url(r'^people_ajax/$', people_ajax, name='people_ajax'),
    url(r'^viz/$', connections_JSON, name='viz'),
    url(r'^connections_JSON/$', JSONstream, name='connections_JSON'),
    url(r'^tree/$',collapseTree,name="collapseTree"),
    url(r'^tree/(?P<selectedNameID>\d+)$',collapseTree),
    url(r'^getJSONconnections/(?P<selectedNameID>\d+)/$',JSONstream,name="JSONstream"),
    url(r'^getJSONconnections/$',JSONstream,name="JSONstream"),
    url(r'^search/$',data_table_search,name="search"),
    #url(r'^newsearch/$',data_table_search,name="data_table_search"),
    url(r'^search_table_json',search_table_json,name="search_table_json"),
    url(r'^validate/$',validateUserSubmission,name="validate"),
    url(r'^anonymous/$',anonymousUser,name="anonymous"),
     url(r'^nopermission/$',noPermission,name="noPermission"),
     url(r'^save_data/$',saveData,name="saveData"),
     url(r'^FAQ/$',renderFAQs,name="FAQ"),
     url(r'^detail/(?P<URL_for_detail>.+)/$', detail),
     url(r'^summarize_schools/$', summarizeSchools),
     url(r'^summarize_submissions/$',summarizeSubmissions),
     url(r'^explore/$', explore),
     url(r'^new/$', whats_new),
     url(r'^phdYears/$', phdYears),
     url(r'^summarize_specializations/$', summarizeSpecializations),
     url(r'^detail/$', search),
     url(r'^support/$',support),
     url(r'^ajax_login/',ajax_login),
     url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),



    )