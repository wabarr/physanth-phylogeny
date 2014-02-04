from django import template

register = template.Library()

def replaceNone(input):
    if input is None:
        return "Unknown"
    else:
        return input

register.filter('replaceNone', replaceNone)