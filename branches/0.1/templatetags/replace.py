#coding: utf-8
from django import template
register = template.Library()

import re 

@register.filter
def replace(string, args):
    search = args.split(args[0])[1]
    replace = args.split(args[0])[2]
    return re.sub( search, replace, string )

@register.filter
def boldify(string, args):
    #TODO remplacer par la chaine de caractères matchée mais qui respecte la casse
    aRgS = args
    return re.sub("(?i)"+args, "<b>"+aRgS+"</b>", string)

@register.filter
def formatduration(args):
    return re.sub('day,','jour',str(args))

@register.filter
def formattime(args):
    try:
        tm = int(args)
        hours = tm/3600
        tm = tm -hours*3600
        min = tm/60
        tm = tm -60*min
        sec = tm
        if hours >0:
            result = "%02d:" % hours
        else:
            result = ''
        return result+"%02d:" % min +"%02d" % sec
    except:
        pass