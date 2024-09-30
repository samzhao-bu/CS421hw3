from django.shortcuts import render, redirect
from django.http import HttpResponse
import random
import time

def main(request):
    return render(request, 'restaurant/main.html')


def order(request):
    specials = ['Buffalo Sauce Extra $1', 'Cheese Topping $0.50', 'Garlic Sauce $0.75']
    daily_special = random.choice(specials)
    
    context = {'daily_special': daily_special}
    return render(request, 'restaurant/order.html', context)

def confirmation(request):
    if request.method == 'POST':
        items = request.POST.getlist('item')
        instructions = request.POST.get('instructions', 'No special instructions')
        name = request.POST.get('name', 'Anonymous')
        phone = request.POST.get('phone', 'No phone provided')
        email = request.POST.get('email', 'No email provided')

        total_price = sum([float(item.split('$')[-1]) for item in items])
        current_time = time.localtime()
        ready_minutes = random.randint(30, 60)
        ready_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.mktime(current_time) + ready_minutes * 60))

        context = {
            'items': items,
            'total_price': total_price,
            'ready_time': ready_time,
            'instructions': instructions,
            'name': name,
            'phone': phone,
            'email': email
        }

        return render(request, 'restaurant/confirmation.html', context)
    else:
        return redirect('order')
