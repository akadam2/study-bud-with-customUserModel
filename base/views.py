from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room, Topic, Message, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate , login, logout
from .forms import RoomForm, UserForm, MyUserCreationForm
# Create your views here.

# rooms = [
    # {'id':1 , 'name': 'Lets learn python!'},
    # {'id':2 , 'name': 'Join my frontend developers' },
    # {'id':3 , 'name': 'Design with me'}
# ]

def loginPage(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect("base:home")

    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request,"User does not exist.")  

        user = authenticate(request,email=email,password=password)
        if user is not None:
            login(request,user)
            return redirect("base:home")
        else:
            messages.error(request,"Incorrect Email or Password")  


    context = {"page":page}
    return render(request, 'base/login_register.html', context)

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request,f"Account created for {user.username}!")
            return redirect("base:home")
    else:
        form = UserForm()
        
    context = {"form":form}
    return render(request, "base/login_register.html",context)    

def logoutUser(request):
    logout(request) #this deletes the session token which in turn logs the user out
    return redirect("base:home")

def userProfile(request, pk):
    user = User.objects.get(id = pk)
    topics = Topic.objects.all()
    rooms = user.room_set.all().order_by('-created')
    activity_messages = user.message_set.all().order_by('-created')
 
    context = {"user":user, "topics":topics,"rooms":rooms,"activity_messages":activity_messages}
    return render(request, "base/profile.html", context)

@login_required(login_url='base:login-register')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid:
            form.save()
            return redirect('base:user-profile', pk=request.user.id)
    return render(request, 'base/update-user.html',{"form":form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    total_rooms = Room.objects.all()
    total_rooms = total_rooms.count()
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()[:3]
    activity_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    room_count = rooms.count()
    context = {'rooms':rooms, 'topics':topics,'room_count':room_count, 'activity_messages':activity_messages, "total_rooms":total_rooms}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method == "POST":
        Message.objects.create(
            user= request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect("base:room", pk=room.id)

    context = {"room":room,"room_messages":room_messages, "participants":participants}        
    return render(request, 'base/room.html', context ) 

@login_required(login_url="base:login-register")
def createRoom(request):
    topics = Topic.objects.all()
    form = RoomForm()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )

        return redirect('base:home')


    context = {"form":form, "topics":topics}
    return render(request,'base/room_form.html',context)    

@login_required(login_url="base:login-register")
def updateRoom(request,pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()


    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('base:home')
    
    context={'form':form, "topics":topics}
    return render(request,'base/room_form.html',context)    

@login_required(login_url="base:login-register")
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Your are not allowed to do this!')

    if request.method == "POST":
        room.delete()
        return redirect('base:home')
    return render(request,'base/delete-room.html',{'obj':room})
    
@login_required(login_url="base:login-register")
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed to do this!')

    if request.method == "POST":
        message.delete()
        return redirect('base:room',pk=message.room.id)
    return render(request,'base/delete-room.html',{'obj':message})      

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {"topics":topics}
    return render(request, "base/topics.html", context)

def activityPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context={"room_messages":room_messages}
    return render(request , "base/activity.html", context)    