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
    #TODO remplacer par la bonne chaine de caractères
    aRgS = args
    return re.sub("(?i)"+args, "<b>"+aRgS+"</b>", string)


