from django.http import HttpResponse
from django.template import loader

# Create your views here.

def basic(request):
    template = loader.get_template("public/basic.html")
    return HttpResponse(template.render())