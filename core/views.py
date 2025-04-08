from django.shortcuts import render

from .forms import RatingForm, RestaurantForm


def index(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST or None)

        if form.is_valid():
            print(form.cleaned_data)
        else:
            return render(request, 'core/index.html', {'form': form})
    context = {
        'form': RestaurantForm()
    }

    return render(request, 'core/index.html', context)
