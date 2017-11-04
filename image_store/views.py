from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.files.storage import FileSystemStorage
import os
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
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
            return Response({'message': 'image successfully deleted'},status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'requested image already deleted/unavailable'},status=status.HTTP_404_NOT_FOUND)

    def patch(self,request, img_name):
        '''This method will replaces the image with image contained in the body of the request'''
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


def optimize(request):
    '''Code to optimize images'''
    user = request.user.username
    if 'img-file' in request.FILES:
        img_file = request.FILES['img-file']
        ext = img_file.name.split('.')[1]
        if ext == 'png' or ext == 'bmp' or ext == 'gif':
            os.chdir(os.path.join(settings.MEDIA_ROOT, user, 'photos'))
            com = "optipng -o2 -strip all " + img_file.name
            os.system(com)
        elif ext == 'jpg' or ext == 'jpeg':
            os.chdir(os.path.join(settings.MEDIA_ROOT, user, 'photos'))
            com = "jpegoptim -f --m=70 "+ img_file.name
            os.system(com)
