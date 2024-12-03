import os
from tensorflow.compat.v1 import Session
from tensorflow import Graph
import numpy as np
from keras.preprocessing import image
#from keras.preprocessing import image
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
model_graph = Graph()

from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import CreateUserForm

# Create your views here.
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)
                return redirect('login')

        context = {'form': form}
        return render(request, 'register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    customers = Customer.objects.all()
    total_customers = customers.count()
    return render(request, 'index.html')

with model_graph.as_default():
	tf_session = Session()
	with tf_session.as_default():
		pass
		model = load_model("webapp/trained_model.h5")
IMG_WIDTH = 224
IMG_HEIGHT = 224

@login_required(login_url='login')
def predictImage(request):
    fileObj = request.FILES["document"]
    fs = FileSystemStorage()
    print(fs, "this is fs")
    filePathName = fs.save(fileObj.name, fileObj)
    print(filePathName)
    def remove(string):
        return "".join(string.split())
    # Driver Program
    string = filePathName
    string1= remove(string)
    print(string1)
    filePathName = fs.url(string1)
    print(filePathName,"This is above test")
    test_image = "." + filePathName
    print(test_image)
    img = image.load_img(test_image,target_size=(IMG_WIDTH,IMG_HEIGHT,3))
    img = img_to_array(img)
    img = img/255
    x = img.reshape(1,IMG_WIDTH,IMG_HEIGHT,3)

    with model_graph.as_default():
        with tf_session.as_default():
            result = np.argmax(model.predict(x))
            if result== 0:
                return render(request, "Glioma.html", {'filePathName': filePathName})
            elif result== 1:
                return render(request, "Meningioma.html", {'filePathName': filePathName})
            elif result== 2:
                return render(request, "NoTumor.html", {'filePathName': filePathName})
            elif result== 3:
                return render(request, "Pituitary.html", {'filePathName': filePathName})
