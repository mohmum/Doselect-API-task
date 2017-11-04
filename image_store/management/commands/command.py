from django.core.management import BaseCommand
from getpass import getpass
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.authtoken.models import Token
import os


class Command(BaseCommand):
    help = "Create a username and get a access key for Image_store API"

    def handle(self, *args, **options):
        '''Creates a user in User class and assign a unique token via Token class'''
        try:
            username = raw_input("Enter the username: ")
            password = getpass("Enter the password: ")
            try:
                user = User.objects.get(username=username)
                print "User already exists"
            except User.DoesNotExist:
                user = User.objects.create_user(username=username,password=password)
                user.save()
                print "username '"+username + "' created successfully"
                os.makedirs(os.path.join(settings.MEDIA_ROOT, username, 'photos'))
                access_key =  Token.objects.create(user=user)
                print "Your access key for API services are: ",access_key.key
        except KeyboardInterrupt:
            print "\nRegistration Cancelled"
