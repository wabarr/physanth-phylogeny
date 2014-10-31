from ajax_select import LookupChannel
from academicPhylogeny.models import person
from django.db.models import Q

class personLookup(LookupChannel):

    model = person

    def get_query(self,q,request):
        query = Q(firstName__icontains=q) | Q(middleName__icontains=q) | Q(lastName__icontains=q)
        return person.objects.filter(query)