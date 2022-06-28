from email.policy import default
from tkinter import CASCADE, Widget
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=50, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50,)
    bio = models.TextField(max_length=100, null=True, blank=True)
    avatar = models.ImageField(null=True, default = "avatar.svg")

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS= []
    pass

class Topic(models.Model):
    name = models.TextField(max_length=200)

    def __str__(self):
        return self.name[:25]

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete= models.SET_NULL, null = True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User,related_name= "participants", blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-updated','-created']   
       

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()      
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated','-created'] 

    def __str__(self):
        return self.body[:50]


