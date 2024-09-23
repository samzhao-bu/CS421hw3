from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import time
import random
quotes = ["You can't connect the dots looking forward; you can only connect them looking backwards. So you have to trust that the dots will somehow connect in your future. You have to trust in something - your gut, destiny, life, karma, whatever. This approach has never let me down, and it has made all the difference in my life.", "Great things in business are never done by one person. They're done by a team of people.", "Be a yardstick of quality. Some people aren't used to an environment where excellence is expected."]
images = [
    "quotes/images/1.png",
    "quotes/images/2.png",
    "quotes/images/3.png"
]

def home(request):
    '''
    A function to respond to the /hw URL.
    This function will delegate work to an HTML template.
    '''
    selected_quote = random.choice(quotes)
    selected_image = random.choice(images)
    context = {'quote': selected_quote, 'image': selected_image}
    return render(request, 'quotes/quote.html', context)

def quote(request):
    selected_quote = random.choice(quotes)
    selected_image = random.choice(images)
    context = {'quote': selected_quote, 'image': selected_image}
    return render(request, 'quotes/quote.html', context)

def show_all(request):
    context = {
        'quote': quotes,
        'image': images
    }
    return render(request, 'quotes/show_all.html', context)

def about(request):
    context = {
        'creator': 'Songwen Zhao', 
        'famous_person': 'Steve Jobs'  
    }
    return render(request, 'quotes/about.html', context)