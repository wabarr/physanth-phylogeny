from django.core.management.base import BaseCommand
from academicPhylogeny.models import userSubmission
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'emails andrew with update on new submissions'

    def handle(self, *args, **options):
        message = "There are no new submissions."
        submissionsToDo = userSubmission.objects.filter(admin_added_to_db=False,admin_problem=False)
        if submissionsToDo.count() > 0:
            message = "There are %(submissionCount)s new submissions on physanthphylogeny.org\n"%{"submissionCount": submissionsToDo.count()}
            message += "\nhttp://www.physanthphylogeny.org/validate"
        else:
            pass

        send_mail("Submissions report physanthphylogeny.org", message, "do-not-reply@physanthphylogeny.org", ["wabarr@gmail.com"],fail_silently=False)
