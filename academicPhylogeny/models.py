from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.utils.html import escape
from django.core.urlresolvers import reverse

class specialization(models.Model):
    name=models.CharField(max_length=100)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']


class school(models.Model):
    name = models.CharField(max_length = 100, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
            db_table = 'school'
            ordering = ['name']


class person(models.Model):
    firstName = models.CharField(max_length = 100,blank=True,null=True)
    middleName = models.CharField(max_length = 100,blank=True,null=True)
    lastName = models.CharField(max_length = 100,blank=True,null=True)
    yearOfPhD = models.IntegerField(max_length= 4, blank=True,null=True)
    school = models.ForeignKey(school)
    specialization = models.ManyToManyField(specialization,null=True,blank=True)
    URL_for_detail = models.CharField(max_length = 200,null=True)
    shareImageURL = models.URLField(max_length=200, null=True, blank=True)
    featureBlurb = models.TextField(max_length=2000, null=True, blank=True, help_text="formatted with with <\p> tags")
    isFeatured = models.NullBooleanField()
    dateFeatured = models.DateField(null=True, blank=True)
    def get_absolute_url(self):
        return reverse('academicPhylogeny.views.detail', args=[self.URL_for_detail])

    def __unicode__(self):
            name = self.firstName + " " + self.lastName
            return name

    def save(self):#custom save method for person to update detail URL
        self.URL_for_detail = (self.firstName + "_" + self.lastName).replace(" ","_")

        #call the normal person save method
        super(person, self).save()

    class Meta:
            db_table = 'person'
            unique_together = (("firstName", "lastName"),)
            ordering = ['lastName']
            verbose_name_plural = 'people'

class frequently_asked_question(models.Model):
    heading = models.CharField(max_length = 50)
    displayOrder = models.IntegerField()
    text = models.TextField(max_length = 2000,verbose_name ="HTML text", help_text="<span style='color:black; font-size:10pt;'>HTML Cheat Sheet:<br></span>" +
                                                        "<span style='color:black; font-size:10pt;'>" +
                                                        escape("Paragraph Formatting: <p>This is the first paragraph.</p> <p>This is the next paragraph</p>") +
                                                        "<br>" +
                                                        escape("Link Formatting: <a href='http://www.google.com'>Click me to Go to Google</a>") +
                                                        "</span>")
    published = models.BooleanField(default=False)
    def __unicode__(self):
        return self.heading
    class Meta:
        ordering=["displayOrder"]
        verbose_name ="Frequently Asked Question"


class connection(models.Model):
    advisor = models.ManyToManyField(person,related_name="a+")
    student = models.ForeignKey(person)

    def student_First_Name(self):
        return(self.student.firstName)
    student_First_Name.admin_order_field = 'student__firstName'

    def student_Last_Name(self):
        return(unicode(self.student.lastName))
    student_Last_Name.admin_order_field = 'student__lastName'

    def student_Year_Of_PhD(self):
        return(str(self.student.yearOfPhD))
    student_Year_Of_PhD.admin_order_field = 'student__yearOfPhD'

    def advisor_name(self):
        allAdvisors = []
        for each in self.advisor.all():
            allAdvisors.append(unicode(each.lastName))

        advisorNames = "/".join(allAdvisors)
        return(unicode(advisorNames))
    advisor_name.admin_order_field = 'advisor__lastName'

    #
    # def Advisor_to_Student_Connection(self):
    #
    #     allAdvisors = []
    #     for each in self.advisor.all():
    #         allAdvisors.append(str(each.firstName + " " + each.lastName))
    #
    #     advisorNames = "/".join(allAdvisors)
    #     to_be_formatted = advisorNames + " --->> " + str(self.student.firstName) + " " + str(self.student.lastName)
    #
    #     return to_be_formatted.replace("None","Unknown")
    #
    def connectionJSON(self):
        allAdvisors = []
        try:
            for each in self.advisor.all():
                allAdvisors.append(unicode(each.firstName) + " " +  unicode(each.lastName))
            to_be_formatted = '{"source":"' + allAdvisors[0] + '", "target":"' + unicode(self.student.firstName) + " " + unicode(self.student.lastName) + '"}'
        except IndexError:
            to_be_formatted = '{"source":"' + "Unknown" + '", "target":"' + unicode(self.student.firstName) + " " + unicode(self.student.lastName) + '"}'
        return to_be_formatted.replace("None","Unknown")
    def __unicode__(self):
        return self.advisor_name() + "-->>" + self.student.firstName + " " + self.student.lastName + " (" + str(self.student.yearOfPhD) + ")"

    class Meta:
        db_table = "connection"
        unique_together = ('student',)
        ordering = ('student',)


CHOICES_source = (("student","I am the student."),("advisor","I am the advisor."),("memory","My memory."),("ref","I looked it up. (please provide source in the notes)"))

class userSubmission(models.Model):
    Your_Email = models.EmailField("Your Email Address")
    advisor_first_name = models.CharField(max_length = 100)
    advisor_last_name = models.CharField(max_length = 100,)
    student_first_name = models.CharField(max_length = 100,)
    student_last_name = models.CharField(max_length = 100,)
    year_of_PhD = models.IntegerField("Student's Year of PhD",max_length= 4, blank=True,null=True,help_text="Leave blank if unknown.")
    school = models.CharField(max_length = 100,help_text="Enter 'Unknown' if you aren't sure.",verbose_name="School Awarding Student's PhD")
    specialization = models.ManyToManyField(specialization,null=True,blank=True,verbose_name="Specialization")
    source = models.CharField("Source of Information",max_length=100,choices=(CHOICES_source))
    notes = models.TextField(max_length=500,blank=True,null=True)
    sendEmailConfirmation = models.BooleanField(default=False,verbose_name="Confirmation Email",help_text="If you check this box, we will email you when the data appear on the tree (usually within 24 hours).")
    admin_added_to_db = models.BooleanField(default=False)
    admin_problem = models.BooleanField(default=False)
    admin_notes = models.CharField(max_length = 500,blank=True,null=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('admin_added_to_db',)
        db_table = "academicPhylogeny_userSubmission_table"

    def connection(self):
        return self.advisor_first_name + " " + self.advisor_last_name + "-->" + self.student_first_name + " " + self.student_last_name + " (" + str(self.year_of_PhD) + ")"
    def __unicode__(self):
        return self.advisor_last_name + "-->" + self.student_last_name


class known_issues(models.Model):
    shortName = models.CharField(max_length = 75,verbose_name="Very Short Description of Issue")
    page = models.CharField(max_length = 50,verbose_name="Which Page is Affected?")
    description = models.TextField(max_length = 1000,verbose_name="Thorough Description of Issue")
    date_added = models.DateTimeField(auto_now_add=True)
    person_adding = models.ForeignKey(User)
    date_resolved = models.DateTimeField(null=True,blank=True)
    priority = models.CharField(max_length=100,choices=(("1-Highest","1-Highest"),("2-Medium","2-Medium"),("3-Low","3-Low")))

    def __unicode__(self):
            return self.shortName

    class Meta:
        verbose_name = "Known Issue"
        verbose_name_plural = "Known Issues"
        ordering = ('date_resolved',)

class userContact(models.Model):
    email = models.EmailField(verbose_name="Your Email Address")
    first_name = models.CharField(max_length=100,verbose_name="Your First Name")
    last_name = models.CharField(max_length=100,verbose_name="Your Last Name")
    affiliation = models.CharField(max_length=100,verbose_name="Your Institutional Affiliation")
    message = models.TextField(max_length=2000,verbose_name="Your message")
    dealt_with = models.BooleanField(default=False)
    admin_notes = models.TextField(max_length=1000)
    date_sent = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('dealt_with','date_sent')


class ContactForm(forms.Form):
    #subject = forms.CharField(max_length=100)
    email = forms.EmailField(label="Email of Recipient")
    to_first = forms.CharField(label="Recipient First Name")
    to_last = forms.CharField(label="Recipient Last Name")
    #Affiliation = forms.CharField(label="Your Institutional Affiliation")
    #cc_myself = forms.BooleanField(required=False)
    message = forms.CharField(widget=forms.Textarea,label="Your message")


class SearchForm(forms.Form):
    name = forms.ChoiceField()

class userSubmissionInValidation(models.Model):
    theUser = models.ForeignKey(User)
    timeCheckedOut = models.DateTimeField(auto_now_add=True)
    checkedOutSubmission = models.ForeignKey(userSubmission)
    def __unicode__(self):
            return self.checkedOutSubmission.advisor_last_name + "-->" + self.checkedOutSubmission.student_last_name


class PhDPredictonParameters(models.Model):
    OLS_2050_prediction = models.IntegerField()
    EXP_2050_prediction = models.IntegerField()
