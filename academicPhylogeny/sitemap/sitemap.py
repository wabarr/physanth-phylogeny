from django.contrib.sitemaps import Sitemap
 
# import your own data structures here
from academicPhylogeny.models import person

class BasicSitemap(Sitemap):
    priority = 0.5
    lastmod = None

    def items(self):
        return [
                "/",
                "/about",
                "/contact",
                "/submit",
                "/tree",
                "/FAQ",
            ]

    def location(self, obj):
        return obj

    def changefreq(self, obj):
        return "weekly"



class GenericDynamicSiteMap(Sitemap):
    priority = 0.5
    changefreq = "weekly"
    lastmod = None

    def location(self, obj):
        return obj.get_absolute_url()



class PeopleSiteMap(GenericDynamicSiteMap):

    def items(self):
        return person.objects.all()


sitemaps = dict(
        people = PeopleSiteMap,
        base = BasicSitemap,
        # ...
    )