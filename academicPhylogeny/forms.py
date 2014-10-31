from django.forms import Form
from academicPhylogeny.models import connection
from ajax_select import make_ajax_field

class GetPersonForm(Form):
    person = make_ajax_field(connection, "student", "personLookup")
