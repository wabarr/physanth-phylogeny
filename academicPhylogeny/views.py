from django.http import HttpResponse,HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import Context, loader,RequestContext
from django.shortcuts import render_to_response,render
from academicPhylogeny.models import connection,userSubmission,person,ContactForm,school,frequently_asked_question, userSubmissionInValidation,userContact, specialization, PhDPredictonParameters
from adverts.models import Ad
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
import json
from django.contrib import messages
from django.forms.models import modelform_factory,model_to_dict
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.core.mail import send_mail
import datetime
from django.utils.timezone import utc
from django.db.models import Count,Min,Max
from collections import Counter
import operator

def schoolSearch(searchstring):
    query = None
    searchTerms=searchstring.split(" ")
    excludedTerms=["University","university","UNIVERSITY","The","the","THE","at","AT","OF","of","State","STATE","state"]

    try:
        uniqueMatch = school.objects.filter(name__exact=searchstring)
        uniqueMatch_count = uniqueMatch.count()
    except IndexError:
        uniqueMatch_count=0

    if uniqueMatch_count == 1:
        return uniqueMatch
    else:
        for term in searchTerms:
            if not term in excludedTerms:
                if query is None:
                    query=Q(name__contains=term)
                else:
                    query = query | Q(name__contains=term)
        matches=school.objects.filter(query)
        return matches

def connections_JSON(request):
    #first get text data
    allConnections = connection.objects.order_by('advisor__lastName')

    out = ""
    counter=0
    n=connection.objects.count()

    out += "["
    for each in connection.objects.all():
        if counter < n-1:
            out += each.connectionJSON() + ","
            counter += 1
        else:
            out += each.connectionJSON()
    out += "]"
    return render_to_response('viz_connections.html',
                             {"links":out,"allConnections":allConnections},
                          context_instance=RequestContext(request))

def peopleSearch(searchstring):
    searchTerms=searchstring.split(" ")
    searchTerms = [term for term in searchTerms if term]

    try:
        uniqueMatch = person.objects.filter(firstName__exact=searchTerms[0],lastName__exact=searchTerms[1])
        if uniqueMatch.count() == 0:
            try:
                uniqueMatch = person.objects.filter(firstName__contains=searchTerms[0],lastName__contains=searchTerms[1])
            except:
                pass
        uniqueMatch_count = uniqueMatch.count()
    except IndexError:
        uniqueMatch_count=0

    if uniqueMatch_count == 1:
        return uniqueMatch
    else:
        query = None
        for term in searchTerms:
            if query is None:
                query = Q(firstName__contains=term) | Q(lastName__contains=term)
            else:
                query = query | Q(firstName__contains=term) | Q(lastName__contains=term)

        matches=person.objects.filter(query)

    return matches

def whats_new(request):
    return render_to_response('whatsnew.html',
                             {},
                          context_instance=RequestContext(request))


def renderFAQs(request):
    validation_count = userSubmission.objects.filter(admin_added_to_db=False,admin_problem=False).count()
    FAQs = frequently_asked_question.objects.filter(published=True)
    return render_to_response('FAQ.html',
                             {"FAQs":FAQs, "validation_count":validation_count},
                          context_instance=RequestContext(request))


def academicPhyloRedirect(request):
    return HttpResponseRedirect("/tree/")

def support(request):
    return render_to_response('support.html',
                             {},
                          context_instance=RequestContext(request))
def home(request):
    validation_count = userSubmission.objects.filter(admin_added_to_db=False,admin_problem=False).count()
    return render_to_response('home.html',
                             {"validation_count":validation_count},
                          context_instance=RequestContext(request))

def people_ajax(request):
    if request.is_ajax():
        filterArgs = {}
        for key,value in request.GET.iteritems():
            if value:
                if value <> "":
                    filterArgs[key] = value
        theConnections = connection.objects.filter(** filterArgs).order_by('student__yearOfPhD')
        if not theConnections:
            return HttpResponse("<h3>Nobody in the database matches your query.</h3>")

        #decide how many matches to figure out singular vs plural
        if theConnections.count() == 1:
            peoplematch = " person matches"
        else:
            peoplematch = " people match"

        response = "<h3>" + str(theConnections.count()) + peoplematch + " your query.</h3>"
        response += "<table>"
        response += "<tr style='font-weight:bold;'><td>Student Name</td><td>School</td><td>Year</td></tr>"
        for each in theConnections:
            response += "<tr>"
            response += "<td>" + each.student.firstName + " " + each.student.lastName + "</td>"
            response += "<td>" + each.student.school.name + "</td>"
            response += "<td>" + str(each.student.yearOfPhD) + "</td>"
            response += "<td><a href='/detail/" + each.student.URL_for_detail + "/'>Detail</a></td>"
            response += "<td><a href='/tree/" + str(each.student.id) + "'>Tree</a></td>"
            response += "</tr>"
        response += "</table>"
        return HttpResponse(response)
    else:
        raise Http404

def people(request):
    #if not request.user.is_authenticated():
    #    return render_to_response("anonymous_user.html",
    #                                {"referringPageURL":"/people/"},
    #                                context_instance=RequestContext(request))

    #if request.user.has_perm("academicPhylogeny.change_connection"):
    filterArgs = {}
    SearchParameters = None
    for key,value in request.GET.iteritems():
        if value:
            if value <> "":
                filterArgs[key] = value
    theConnections = connection.objects.filter(** filterArgs).order_by('student__yearOfPhD')

    schools = school.objects.all()
    specializations = specialization.objects.all()
    minyear = connection.objects.filter(student__yearOfPhD__gt=0).aggregate(Min('student__yearOfPhD')).values()[0]
    maxyear = connection.objects.all().aggregate(Max('student__yearOfPhD')).values()[0] + 1
    years = range(minyear,maxyear,1)

    if theConnections.count() < connection.objects.count():
        SearchParameters = "thereAreSearchParameters"

    return render_to_response('people.html',
                             {'theConnections':theConnections,"SearchParameters":SearchParameters,"schools":schools,"filterArgs":filterArgs,"years":years,"specializations":specializations},
                          context_instance=RequestContext(request))
    #else:
    #    return HttpResponseRedirect("/nopermission/")

def about(request):
    numConnections = connection.objects.all().count
    return render_to_response('about.html',
                             {"nConnections":numConnections},
                          context_instance=RequestContext(request))

def collapseTree(request,selectedNameID=None):
        validation_count = userSubmission.objects.filter(admin_added_to_db=False,admin_problem=False).count()
        selectedPersonHasNoConnections = False
        nSchools = school.objects.all().count
        if selectedNameID:

            try:
                selectedPerson = person.objects.get(pk=selectedNameID)
                if connection.objects.filter(student = selectedPerson).count() == 0 and connection.objects.filter(advisor = selectedPerson).count() == 0:
                    selectedPersonHasNoConnections = True

            except ObjectDoesNotExist:
                messages.add_message(request, messages.INFO, "Sorry, I can't find that person. Showing the whole tree instead")
                selectedPerson = None
                selectedNameID = None


        else:
            selectedNameID = None
            selectedPerson = None


        return render_to_response('collapseTree.html',
                             {"nConnections":connection.objects.all().count,"selectedNameID":selectedNameID,"selectedPersonHasNoConnections":selectedPersonHasNoConnections,"selectedPerson":selectedPerson, "validation_count":validation_count,"nSchools":nSchools},
                            context_instance=RequestContext(request))

def JSONstream(request,selectedNameID=None):
    response = HttpResponse(mimetype='application/json')
    if selectedNameID != None:
        selectedNameID = int(selectedNameID)
        if connection.objects.filter(student = selectedNameID).count() == 0 and connection.objects.filter(advisor = selectedNameID).count() == 0:
            return HttpResponse("This person has no matching connections")
    advisors=[]
    students=[]
    studentIDs=[]
    advisorIDs=[]
    urlsForLink=[]
    for each in connection.objects.all():
        for advisor in each.advisor.all():
            advisors.append(advisor.firstName + " " + advisor.lastName)
            students.append(each.student.firstName + " " + each.student.lastName)
            studentIDs.append(each.student.id)
            advisorIDs.append(advisor.id)
            urlsForLink.append("/detail/" + each.student.URL_for_detail)
    links=zip(advisorIDs,studentIDs)
    parents, children = zip(*links)
    root_nodes = {x for x in parents if x not in children}
    for node in root_nodes:
        links.append(("", node))

    def get_nodes(node,selectedNameID=None):
        d = {}

        if node=="":
            d['name'] = ""
        else:
            try:
                d['name'] = students[studentIDs.index(node)]
            except:
                d['name'] = advisors[advisorIDs.index(node)]


        if node=="":
            d["link"] = "/search/"
        else:
            try:
                d["link"] = urlsForLink[studentIDs.index(node)]
            except:
                d['link'] = "/detail/" + advisors[advisorIDs.index(node)].replace(" ","_")


        try:
            if(get_parent(node)== ""):
                d["nodeType"] = "localRoot"
            else:
                temp=[each == node for each in children]
                if sum(temp) > 1:
                    d["nodeType"] = "coAdvisee"
                if sum(temp) == 1:
                    d["nodeType"] = "normal"
        except:
            if node == "root":
                d["nodeType"] = "root"

            else:
                d["nodeType"] = "none"


        if d["name"] != "":
            if selectedNameID:
                try:
                    if d['name'] == students[studentIDs.index(selectedNameID)]:
                        d["selected"] = "y"
                        d["xOffset"] = 17
                except:
                    if d['name'] == advisors[advisorIDs.index(selectedNameID)]:
                        d["selected"] = "y"
                        d["xOffset"] = 17
                    else:
                        d["selected"] = "n"
                        d["xOffset"] = 10
            else:
                d["selected"] = "n"
                d["xOffset"] = 10
        else:
            d["selected"] = "n"
            d["xOffset"] = 10


        if get_children(node):
            d['children'] = [get_nodes(child,selectedNameID) for child in get_children(node)]
        return d

    def get_children(node):
        return [x[1] for x in links if x[0] == node]

    def get_parent(node):
        return [x[0] for x in links if x[1] == node][0]

    originalSelection = selectedNameID

    matches = [selectedNameID == child for child in children]
    nAdvisors = sum(matches)

    if selectedNameID != None:
        if nAdvisors > 1:
            tree = get_nodes("",selectedNameID)
        else:
            while get_parent(selectedNameID) != "":
                selectedNameID = get_parent(selectedNameID)
            tree = get_nodes(selectedNameID,selectedNameID = originalSelection)
    else:
        tree=get_nodes("")

    response.write(json.dumps(tree, indent=4))

    return response

def search(request):
    matches=None
    success=None
    threeAds = Ad.objects.all().order_by('?')[0:3]

    if request.method == "POST":
        searchstring=request.POST["searchbox"]
        if not searchstring:
            return HttpResponseRedirect("/search/")
        matches=peopleSearch(searchstring)
        if matches.count()==0:
            success=False
            messages.add_message(request, messages.INFO,"Nobody with that name was found.")
        else:
            messages.add_message(request, messages.INFO,"Possible matches:")
            success=True

    return render_to_response('search.html',
                             {"matches":matches,"success":success,"threeAds":threeAds},
                          context_instance=RequestContext(request))

def userSubmitData(request):
    validation_count = userSubmission.objects.filter(admin_added_to_db=False,admin_problem=False).count()
    userSubmitForm = modelform_factory(userSubmission,
                                       exclude=("admin_added_to_db","admin_problem","admin_notes"))
    if request.method == "POST":
        form = userSubmitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Success! Data usually get added to the tree within 24 hours.')
            return HttpResponseRedirect("")
        else:
            messages.add_message(request, messages.INFO, 'Please correct the errors below.')

    else:
        form = userSubmitForm()
    return render_to_response('submit_data.html',
                          {"form":form, "validation_count":validation_count},
                          context_instance=RequestContext(request))

def validateUserSubmission(request):


    if not request.user.is_authenticated():
        return render_to_response("anonymous_user.html",
                                    {"referringPageURL":"/validate/"},
                                    context_instance=RequestContext(request))

    if request.user.has_perm("academicPhylogeny.change_connection"):
        #first, go through and delete any stale user checkouts older than 1 hour (3600 seconds)
        for each in userSubmissionInValidation.objects.all():
            age = datetime.datetime.utcnow().replace(tzinfo=utc) - each.timeCheckedOut
            if age.total_seconds() > 3600:
                each.delete()

        try:
            inProgress = userSubmissionInValidation.objects.all()
            inProgressIds = [each.checkedOutSubmission.id for each in inProgress]
            submissionToValidate = None

            #loop through each in progress...if there is one in progress for current user, then that's the submission to validate
            for each in inProgress:
                if each.theUser == request.user:
                    submissionToValidate = each.checkedOutSubmission
            #if not, then return the next one, excluding any that are checked out for other users
            if not submissionToValidate:
                submissionToValidate = userSubmission.objects.filter(admin_added_to_db=False,admin_problem=False).exclude(id__in=inProgressIds)[0]

            #delete any currently checked out for the current user, just a precaution
            currentUserCheckouts = userSubmissionInValidation.objects.filter(theUser=request.user)
            for each in currentUserCheckouts:
                each.delete()

            #checkout the current submission to validate
            newCheckout = userSubmissionInValidation(theUser = request.user, checkedOutSubmission=submissionToValidate)
            newCheckout.save()

            studentMatches = peopleSearch(submissionToValidate.student_first_name + " " +  submissionToValidate.student_last_name)
            advisorMatches = peopleSearch(submissionToValidate.advisor_first_name + " " +  submissionToValidate.advisor_last_name)
            schoolMatches = schoolSearch(submissionToValidate.school)

        except IndexError: #if there are no results
            submissionToValidate = []
            studentMatches=[]
            advisorMatches=[]
            schoolMatches=[]

        return render_to_response('validate_user_submissions.html',
                          {
                              "studentMatches":studentMatches,
                              "submissionToValidate":submissionToValidate,
                              "advisorMatches":advisorMatches,
                              "schoolMatches":schoolMatches,
                              "allSchools":school.objects.all(),
                              "allPeople":person.objects.all()
                          },
                          context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/nopermission/")

def anonymousUser(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(request.POST["referringPageURL"])
            else:
                return HttpResponse("This user account is not active.")
        else:
            messages.add_message(request, messages.INFO, 'Invalid username or password.')
            return render_to_response('anonymous_user.html',
                          {"referringPageURL":request.POST["referringPageURL"]},
                          context_instance=RequestContext(request))
    else:
        return render_to_response('anonymous_user.html',
                          {},
                          context_instance=RequestContext(request))

def noPermission(request):
    return render_to_response('inadequate_permissions.html',
                          {},
                          context_instance=RequestContext(request))

def saveData(request):
    if request.method=="POST":
        model=request.POST["model"]

        args={}
        for parameter in request.POST.iteritems():
            if parameter[0] not in ["model","csrfmiddlewaretoken","school"]:
                if parameter[1] == "":
                    pass
                else:
                    args[parameter[0]] = parameter[1]
            if parameter[0] == "school":
                try:
                    args[parameter[0]] = school.objects.get(name__exact=parameter[1])
                except:
                    args[parameter[0]]= None


            if parameter[0] == "advisor":
                try:
                    args[parameter[0]] = person.objects.get(pk=parameter[1])
                except:
                     args[parameter[0]]= None

            if parameter[0] == "student":
                try:
                    args[parameter[0]] = person.objects.get(pk=parameter[1])
                except:
                    args[parameter[0]]= None

        if model == "school":
            try:
                school.objects.get(name__exact=args["newSchoolName"])
                messages.add_message(request, messages.INFO, "This school is already in the database.")
                return HttpResponseRedirect("/validate/")
            except ObjectDoesNotExist:
                modelArgs = {k: args[k] for k in ["newSchoolName"] if k in args}

                #rename dictionary argument to match school model
                modelArgs["name"] = modelArgs["newSchoolName"]
                del modelArgs["newSchoolName"]

                newSchool = school(** modelArgs)
                newSchool.save()
                referringUserSubmission = userSubmission.objects.get(pk=args["referringUserSubmission"])
                referringUserSubmission.school = args["newSchoolName"]
                referringUserSubmission.save()
                messages.add_message(request, messages.INFO, "Added the new school to the database and updated user submission.")
                return HttpResponseRedirect("/validate/")

        if model == "student":
            if args["yearOfPhD"] == "None":
                args["yearOfPhD"] = None
            try:
                person.objects.get(firstName__exact=args["firstName"],lastName__exact=args["lastName"])
                messages.add_message(request, messages.INFO, "This person is already in the database")
                return HttpResponseRedirect("/validate/")

            except ObjectDoesNotExist:
                modelArgs = {k: args[k] for k in ["firstName","lastName","yearOfPhD","school"] if k in args}
                newPerson = person(** modelArgs)
                newPerson.save()
                messages.add_message(request, messages.INFO, "Successfully saved data for: %(first)s %(last)s" %{"first":request.POST["firstName"],"last":request.POST["lastName"]})
                referringUserSubmission = userSubmission.objects.get(pk=args["referringUserSubmission"])
                referringUserSubmission.student_first_name = newPerson.firstName
                referringUserSubmission.student_last_name = newPerson.lastName
                referringUserSubmission.save()
                return HttpResponseRedirect("/validate/")

        if model == "advisor":
            try:
                person.objects.get(firstName__exact=args["firstName"],lastName__exact=args["lastName"])
                messages.add_message(request, messages.INFO, "This person is already in the database")
                return HttpResponseRedirect("/validate/")
            except ObjectDoesNotExist:
                modelArgs = {k: args[k] for k in ["firstName","lastName"] if k in args}
                modelArgs["school"] = school.objects.get(name__exact="Unknown")
                newPerson = person(** modelArgs)
                newPerson.save()
                messages.add_message(request, messages.INFO, "Successfully saved data for: %(first)s %(last)s" %{"first":request.POST["firstName"],"last":request.POST["lastName"]})
                referringUserSubmission = userSubmission.objects.get(pk=args["referringUserSubmission"])
                referringUserSubmission.advisor_first_name = newPerson.firstName
                referringUserSubmission.advisor_last_name = newPerson.lastName
                referringUserSubmission.save()
                return HttpResponseRedirect("/validate/")


        elif model == "updateStudentInUserSubmission":
            if not "selectedStudent" in args.keys():
                messages.add_message(request, messages.INFO, "Please select a student or add a new one.")
                return HttpResponseRedirect("/validate/")
            referringUserSubmission = userSubmission.objects.get(pk=args["referringUserSubmission"])
            theStudent = person.objects.get(pk=args["selectedStudent"])
            referringUserSubmission.student_first_name = theStudent.firstName
            referringUserSubmission.student_last_name = theStudent.lastName
            referringUserSubmission.save()
            messages.add_message(request, messages.INFO, "User submitted student was changed to match database")
            return HttpResponseRedirect("/validate/")

        elif model == "updateAdvisorInUserSubmission":
            if not "selectedAdvisor" in args.keys():
                messages.add_message(request, messages.INFO, "Please select an advisor or add a new one.")
                return HttpResponseRedirect("/validate/")
            referringUserSubmission = userSubmission.objects.get(pk=args["referringUserSubmission"])
            theAdvisor = person.objects.get(pk=args["selectedAdvisor"])
            referringUserSubmission.advisor_first_name = theAdvisor.firstName
            referringUserSubmission.advisor_last_name = theAdvisor.lastName
            referringUserSubmission.save()
            messages.add_message(request, messages.INFO, "User submitted advisor was changed to match database")
            return HttpResponseRedirect("/validate/")

        elif model == "updateSchoolInUserSubmission":
            if not "schoolID" in args.keys():
                messages.add_message(request, messages.INFO, "Please select a school or add a new one.")
                return HttpResponseRedirect("/validate/")
            referringUserSubmission = userSubmission.objects.get(pk=args["referringUserSubmission"])
            theSchool = school.objects.get(pk=args["schoolID"])
            referringUserSubmission.school = theSchool.name
            referringUserSubmission.save()
            messages.add_message(request, messages.INFO, "User submitted school was changed to match database")
            return HttpResponseRedirect("/validate/")

        elif model == "flagAsProblem":
            referringUserSubmission = userSubmission.objects.get(pk=args["referringUserSubmission"])
            referringUserSubmission.admin_problem=True
            referringUserSubmission.admin_notes=args["problem_notes"]
            referringUserSubmission.save()
            messages.add_message(request, messages.INFO, "Marked that last submission as a problem.")
            currentUserCheckouts = userSubmissionInValidation.objects.filter(theUser=request.user)
            for each in currentUserCheckouts:
                each.delete()
            return HttpResponseRedirect("/validate/")

        elif model == "connection":
            if not args["student"]:
                messages.add_message(request, messages.INFO, "You haven't validated the student for this connection.")
                return HttpResponseRedirect("/validate/")
            if not args["advisor"]:
                messages.add_message(request, messages.INFO, "You haven't validated the advisor for this connection.")
                return HttpResponseRedirect("/validate/")


            modelArgs = {k: args[k] for k in ["student"] if k in args}
            newConnection = connection (** modelArgs)

            try:#try to save and add advisor
                newConnection.save()
                newConnection.advisor.add(args["advisor"])
                referringUserSubmission = userSubmission.objects.get(pk=args["referringUserSubmission"])
                referringUserSubmission.admin_added_to_db=True
                referringUserSubmission.save()
                thePerson=args["student"]
                for specialty in referringUserSubmission.specialization.all():
                    thePerson.specialization.add(specialty)
                if referringUserSubmission.sendEmailConfirmation:
                    subject = "Your submission is live on www.physanthphylogeny.org"
                    message = "****Please don't reply to this email. You can contact us at www.physanthphylogeny.org/contact/ \n\nHello,\n\nThanks for submitting data to the Academic Phylogeny of Physical Anthropology. We just added the following connection from the data you sent.\n\nStudent:%(student)s\nAdvisor:%(advisor)s\n\nYou can see the new entry at http://www.physanthphylogeny.org/detail/%(URL_for_detail)s.\n\nThanks again,\n\nAndrew Barr, Brett Nachman, and Liza Shapiro"%{"student":referringUserSubmission.student_first_name + " " + referringUserSubmission.student_last_name,"advisor":referringUserSubmission.advisor_first_name + " " + referringUserSubmission.advisor_last_name, "URL_for_detail":newConnection.student.URL_for_detail}
                    recipients = []
                    recipients.append(referringUserSubmission.Your_Email)
                    send_mail(subject, message, "do-not-reply@physanthphylogeny.org", recipients,fail_silently=False)
                messages.add_message(request, messages.INFO, "Successfully saved connection.")

                currentUserCheckouts = userSubmissionInValidation.objects.filter(theUser=request.user)
                for each in currentUserCheckouts:
                    each.delete()

                return HttpResponseRedirect("/validate/")

            except Exception: #or
                messages.add_message(request, messages.INFO, "We already had a connection for that student in the database. Moving on to the next one....")
                referringUserSubmission = userSubmission.objects.get(pk=args["referringUserSubmission"])
                referringUserSubmission.admin_problem=True
                referringUserSubmission.admin_notes="Already in the database"
                referringUserSubmission.save()

                currentUserCheckouts = userSubmissionInValidation.objects.filter(theUser=request.user)
                for each in currentUserCheckouts:
                    each.delete()

                return HttpResponseRedirect("/validate/")



        else:
            return HttpResponse("I don't know how to save this type of object")

def contact_to_db(request):
    validation_count = userSubmission.objects.filter(admin_added_to_db=False,admin_problem=False).count()
    theContactForm = modelform_factory(userContact,exclude=("dealt_with","admin_notes","date_sent","date_last_modified"))
    if request.method == 'POST': # If the form has been submitted...
        form = theContactForm(request.POST)# A form bound to the POST data
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, 'Thanks! Your message has been sent.')
            return HttpResponseRedirect('/contact/') # Redirect after POST
        else:
            messages.add_message(request, messages.INFO, 'Please correct the errors below.')
    else:
        form = theContactForm() # An unbound form

    return render_to_response('newContact.html',
                             {"form":form, "validation_count":validation_count},
                          context_instance=RequestContext(request))


def emailUser(request):
    if not request.user.is_authenticated():
        return render_to_response("anonymous_user.html",
                                    {"referringPageURL":"/email_user/"},
                                    context_instance=RequestContext(request))

    if request.user.has_perm("academicPhylogeny.change_connection"):
        if request.method == 'POST': # If the form has been submitted...
            form = ContactForm(request.POST) # A form bound to the POST data
            if form.is_valid():
                subject = "Message from physanthphylogeny.org"
                to_first = form.cleaned_data['to_first']
                to_last = form.cleaned_data['to_last']
                sender = 'do-not-reply@physanthphylogeny.org'
                message = form.cleaned_data['message']
                message_formatted = "****Please do not reply to this message.  You can contact us at www.physanthphylogeny.org/contact/\n\nDear %(first)s %(last)s,\n\nThanks so much for participating in our project.  We rely on users like you to help get the tree right. %(message)s\n\nThanks again,\nAndrew Barr, Brett Nachman, and Liza Shapiro at physanthphylogeny.org"%{'first':to_first,'last':to_last,'message':message}
                recipients = [form.cleaned_data['email']]

                send_mail(subject, message_formatted, sender, recipients,fail_silently=False)
                messages.add_message(request, messages.INFO, 'Successfully sent message')
                return HttpResponseRedirect('/email_user/') # Redirect after POST
            else:
                messages.add_message(request, messages.INFO, 'Please correct the errors below.')
        else:
            form = ContactForm() # An unbound form

        return render_to_response('contact.html',
                             {"form":form},
                          context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/nopermission/")

def detail(request,URL_for_detail):
    try:
        thePerson = person.objects.get(URL_for_detail__exact=URL_for_detail)
    except ObjectDoesNotExist:
        thePerson = None

    try:
        advisorConnection = connection.objects.get(student__id=thePerson.id)
    except:
        advisorConnection = None

    try:
        studentConnections = connection.objects.filter(advisor__id=thePerson.id).order_by("student__yearOfPhD")
    except:
        studentConnections = None


    return render_to_response('detail.html',
                             {"thePerson":thePerson,"advisorConnection":advisorConnection,"studentConnections":studentConnections},
                          context_instance=RequestContext(request))

def summarizeSchools(request):
    response = HttpResponse(mimetype='application/json')
    school_count = school.objects.annotate(num_phds=Count('person')).filter(num_phds__gt=3).exclude(name="Unknown",num_phds=0).order_by("-num_phds")
    response_list = []
    for indx, item in enumerate(school_count):
        item_dict={}
        item_dict["school"] = item.name
        item_dict["phd_count"] = item.num_phds
        item_dict["id"] = item.id
        response_list.append(item_dict)


    response.write(json.dumps(response_list))
    return response

def summarizeSpecializations(request):
    response = HttpResponse(mimetype='application/json')
    specialization_count = specialization.objects.all().annotate(count=Count("person")).order_by("-count")
    response_list = []
    for indx, item in enumerate(specialization_count):
        item_dict={}
        item_dict["specialization"] = item.name
        item_dict["count"] = item.count
        item_dict["id"] = item.id

        response_list.append(item_dict)


    response.write(json.dumps(response_list))
    return response

def summarizeSubmissions(request):
    response = HttpResponse(mimetype='application/json')
    submittedDates = userSubmission.objects.filter(admin_added_to_db=True).order_by("date_submitted").values("date_submitted")
    tempDates = []
    for each in submittedDates:
        temp = each["date_submitted"].strftime('%Y-%m-%d')
        tempDates.append(temp)
    tempDates = Counter(tempDates)
    tempDates = dict(sorted(tempDates.items()))

    response.write(json.dumps(tempDates, indent=4))
    return response

def phdYears(request):
    response = HttpResponse(mimetype='application/json')
    phd_years = person.objects.filter(yearOfPhD__gt=1000).values("yearOfPhD").annotate(count=Count("yearOfPhD")).order_by()
    response_list = []
    for indx, item in enumerate(phd_years):
        item_dict={}
        item_dict["year"] = item["yearOfPhD"]
        item_dict["count"] = item["count"]
        response_list.append(item_dict)


    response.write(json.dumps(response_list))
    return response



def explore(request):
    preds = PhDPredictonParameters.objects.get(pk=1)
    return render_to_response('explore.html',
                             {"preds":preds},
                          context_instance=RequestContext(request))

def ajax_login(request):
    if request.is_ajax():
        if request.POST:
            username = request.POST['username']
            password = request.POST['password']
            nextURL = request.POST['nextURL']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse(nextURL)# return 200 with the url to redirect
                else:
                    return "Your user account is not active" #I don't do anything with this yet in template or jquery
            else:
                return HttpResponseForbidden() #return 403 to indicate failed login

        else:
            return HttpResponseForbidden() #return 403
    else:
        return HttpResponseForbidden() #return 403

def data_table_search(request):
    filterArgs = {}
    for key,value in request.GET.iteritems():
        if key <> "_":
            if value <> "":
                filterArgs[key] = value

    return render_to_response("data_table_search.html",
        {"filterArgs":filterArgs},
          context_instance=RequestContext(request)
    )

def search_table_json(request):
    filterArgs = {}
    for key,value in request.GET.iteritems():
        if key <> "_":
            if value <> "":
                filterArgs[key] = value
    fieldsToGet = ["student__URL_for_detail","student__lastName","student__firstName", "advisor__lastName","advisor__firstName", "student__yearOfPhD","student__school__name"]
    if filterArgs:
        connections = connection.objects.filter(** filterArgs).values_list(* fieldsToGet)
    else:
        connections = connection.objects.all().values_list(* fieldsToGet)

    response = HttpResponse(mimetype='application/json')

    responsedict = {"data":[]}
    for conn in connections:
        responsedict["data"].append(conn)
    response.write(json.dumps(responsedict))
    return response