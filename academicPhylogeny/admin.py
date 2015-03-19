from academicPhylogeny.models import *
from django.contrib import admin



class connectionAdmin(admin.ModelAdmin):
    search_fields = ("student__lastName","student__firstName","advisor__lastName")
    filter_horizontal = ("advisor",)
    raw_id_fields = ("student",)
    fieldsets = (
        (None, {
            'fields': (('advisor',),('student',))
            }),
        )

class personAdmin(admin.ModelAdmin):
    list_display = ('id','firstName','lastName','yearOfPhD','school','shareImageURL','isFeatured')
    list_editable = ('firstName','lastName','yearOfPhD','school', 'shareImageURL', 'isFeatured')
    list_filter = ['school','specialization','isFeatured']
    search_fields = ("lastName","firstName")
    filter_horizontal = ("specialization",)
    fieldsets = (
        (None, {
            'fields': (('firstName', 'middleName', 'lastName'),('yearOfPhD','school'),('specialization'),('isFeatured','shareImageURL',"featureBlurb"))
            }),
        )

class userSubmissionAdmin(admin.ModelAdmin):
    list_display = ("connection","school","admin_added_to_db","admin_problem","Your_Email","date_submitted","date_last_modified")
    list_filter = ["Your_Email","admin_added_to_db","admin_problem","source"]
    search_fields = ("advisor_first_name","advisor_last_name","student_first_name","student_last_name")

class issuesAdmin(admin.ModelAdmin):
    list_display = ("shortName","page","person_adding","date_added","date_resolved","priority")
    list_filter = ("priority",)

class userSubmissionInValidationAdmin(admin.ModelAdmin):
    list_display = ("theUser","timeCheckedOut","checkedOutSubmission")

class userContactAdmin(admin.ModelAdmin):
    list_display = ("first_name","last_name","affiliation","dealt_with","date_sent","date_last_modified")
    search_fields = ("first_name","last_name","message")

class FAQadmin(admin.ModelAdmin):
    list_display = ("heading","published","displayOrder")
    list_filter = ("published",)
    list_editable = ("published","displayOrder")

admin.site.register(connection,connectionAdmin)
admin.site.register(person,personAdmin)
admin.site.register(school)
admin.site.register(frequently_asked_question,FAQadmin)
admin.site.register(specialization)
admin.site.register(userSubmission,userSubmissionAdmin)
admin.site.register(known_issues,issuesAdmin)
admin.site.register(userSubmissionInValidation,userSubmissionInValidationAdmin)
admin.site.register(userContact,userContactAdmin)
admin.site.register(PhDPredictonParameters)

