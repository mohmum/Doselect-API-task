from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render,redirect
import os
from .forms import Loginform
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate,login,logout
from django.views.generic import View
from django.conf import settings

class Oneimage(APIView):

    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request,img_name):
        '''Gets a single image when image name given in the url, otherwise a error message'''
        user = request.user.username
        path = os.listdir(os.path.join(settings.MEDIA_ROOT, user,'photos'))
        if img_name in path:
            return Response({"img-name": img_name},status=status.HTTP_200_OK)
        else:
            return Response({'message':'image by name '+img_name+' does not exists'},status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, img_name):
        '''Deletes the image from the user file'''
        user = request.user.username
        path = os.listdir(os.path.join(settings.MEDIA_ROOT,user, 'photos'))
        if img_name in path:
            os.chdir(os.path.join(settings.MEDIA_ROOT,user,'photos'))
            os.remove(img_name)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def patch(self,request, img_name):
        '''This method will replaces teh image with image contained in the body of the request'''
        user = request.user.username
        image_exists = 'img-file' in request.FILES
        path = os.listdir(os.path.join(settings.MEDIA_ROOT,user, 'photos'))
        if img_name in path and image_exists:
            os.chdir(os.path.join(settings.MEDIA_ROOT,user, 'photos'))
            os.remove(img_name)
        else:
            return Response({'message':'Image not found'},status=status.HTTP_404_NOT_FOUND)


        if image_exists:
            img_file = request.FILES['img-file']
            storage_path = os.path.join(settings.MEDIA_ROOT,user, 'photos')
            fs = FileSystemStorage(storage_path)
            fs.save(img_file.name, img_file)
            optimize(request)
            return Response({'img-name': 'Changes applied to image'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Image not present in request body'}, status=status.HTTP_400_BAD_REQUEST)


class Imagesall(APIView):

    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user.username
        path = os.listdir(os.path.join(settings.MEDIA_ROOT,user,'photos'))
        store = []
        for image in path:
            store.append({
                "img-name": image
            })
        if len(store):
            return Response(store,status=status.HTTP_200_OK)
        else:
            return Response({'message':'No images stored'})

    def post(self,request):
        user = request.user.username
        if 'img-file' in request.FILES:
            img_file = request.FILES['img-file']
            storage_path = os.path.join(settings.MEDIA_ROOT,user,'photos')
            fs = FileSystemStorage(storage_path)
            fs.save(img_file.name,img_file)
            optimize(request)
            return Response({'message':'Image successfully uploaded'},status= status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Image not present in request body'}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(View):
    form_class = Loginform
    template_name = 'login.html'

    def get(self,request):
        form = self.form_class(None)
        return render(request,self.template_name,{'form':form})

    def post(self,request):
        form = self.form_class(request.POST)
        user = authenticate(username=request.POST['username'],password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request,user)
                return redirect('image_store:list')
        return render(request, self.template_name, {'form': form})



def optimize(request):
    '''Code to optimze png images'''
    user = request.user.username
    if 'img-file' in request.FILES:
        img_file = request.FILES['img-file']
        ext = img_file.name.split('.')[1]
        if ext == 'png':
            os.chdir(os.path.join(settings.MEDIA_ROOT, user, 'photos'))
            com = "optipng -o2 -strip all " + img_file.name
            os.system(com)
