from django.shortcuts import render,redirect
from django.db.models import Q
from .models import Room,Topic,Message
from .forms import RoomForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
def loginpage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home') 
    
    if request.method=='POST':
        k=0
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username = username)
        except:
            k=1
            messages.error(request, "Couldn't find username...")
        user = authenticate(request,username=username,password=password)
        
        if user is not None:
            login(request,user)
            return redirect('home')    
        else:
            if k==0:
                messages.error(request,"user name and password not maching...")
    context={'loginpage':False,'page':page}
    return render(request,"base/login_register.html",context)

def logoutpage(request):
    logout(request)
    return  redirect('home')

def registerpage(request):
    page = 'register'
    form = UserCreationForm()
    if request.method=='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,"Please enter the valid data..")
    context = {'page':page,'form':form}
    return render(request,"base/login_register.html",context)
    

def home(request):
    topics = Topic.objects.all()
    q = request.GET.get('q') if request.GET.get('q')!=None else ""
    data = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) 
        )
    roomcount = data.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-created')
    context = {'data':data,'topic':topics,'search':q,'roomcount':roomcount,'loginpage':True,'room_message':room_messages}
    return render(request,"base/home.html",context)

def room(request,pk):
    data = Room.objects.get(id=pk)
    participance = data.participants.all()
    message = data.message_set.all().order_by('-created')
    if request.method == 'POST':
        Message.objects.create(
            user = request.user,
            room = data,
            body = request.POST.get('body')       
        )
        data.participants.add(request.user)
        return redirect('room',pk=data.id)
        
    context = {'room':data,'loginpage':True,'message':message,'participances':participance}
    return render(request,"base/room.html",context)

def profile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context={'user':user,'data':rooms,'room_message':room_messages,'topic':topics,'loginpage':True}
    return  render(request,"base/profile.html",context)

@login_required(login_url='login')
def createroom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            form.save()     
            return redirect('home')         
    context = {'form':form,'loginpage':True}
    return render(request,"base/room_form.html",context)

@login_required(login_url='login')
def updateroom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse("you are not alloud here....")
    if request.method == 'POST':
        form = RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')  
    context = {'form':form,'loginpage':True}
    return render(request,"base/room_form.html",context)

@login_required(login_url='login')
def deleteroom(request,pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {"obj":room,'loginpage':True}
    return render(request,'base/delete.html',context)

@login_required(login_url='login')
def deletemessage(request,pk):
    messages = Message.objects.get(id=pk)
    if request.user != messages.user:
        return HttpResponse('You are not allowed here')
    if request.method == 'POST':
        messages.delete()
        return redirect('home')
    context = {"obj":messages,'loginpage':True}
    return render(request,'base/delete.html',context)

