from django.views import View
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import os
import base64
from datetime import date
import cv2
import uuid
from .utils import generate_mosaics
from django.views.decorators.csrf import csrf_exempt
import json


class ImageUploadView(View):

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        image_data = self._get_image_data(request)

        if not image_data:
            return JsonResponse({'status': 'No image'}, status=400)
        try:
            image_path = self._save_base64_image(image_data)
        except Exception as e:
            return HttpResponse(str(e), status=400)

        mosaic_paths = self._generate_and_save_mosaics(image_path, request)
        return JsonResponse(mosaic_paths)

    def _get_image_data(self, request):
        request_data = json.loads(request.body.decode('utf-8'))
        return request_data.get('image')

    def _save_base64_image(self, image_data):
        if not isinstance(image_data, str):
            raise ValueError('Only base64')

        if ';base64,' not in image_data:
            raise ValueError('Invalid base64 format')

        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return default_storage.save('tmp/original.' + ext, data)

    def _generate_and_save_mosaics(self, image_path, request):
        today = date.today()
        subfolder_name = today.strftime("%Y-%m-%d")
        subfolder_path = self._get_or_create_subfolder_path(subfolder_name)
        mosaics = generate_mosaics(image_path, ['sample/blocks', 'sample/blocks1', 'sample/blocks2'], 8, (704, 936))
        os.remove(os.path.join(settings.MEDIA_ROOT, image_path))

        return self._save_mosaics_to_folder(mosaics, subfolder_path, subfolder_name, request)

    def _get_or_create_subfolder_path(self, subfolder_name):
        subfolder_path = os.path.join('media', 'example', subfolder_name)
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
        return subfolder_path

    def _save_mosaics_to_folder(self, mosaics, subfolder_path, subfolder_name, request):
        mosaic_paths = {}
        for i, mosaic in enumerate(mosaics, 1):
            uuid_str = str(uuid.uuid4())
            mosaic_image_path = os.path.join(subfolder_path, f'mosaic_{uuid_str}.jpg')
            cv2.imwrite(mosaic_image_path, mosaic)
            mosaic_url = os.path.join(settings.MEDIA_URL, 'example', subfolder_name, f'mosaic_{uuid_str}.jpg')
            mosaic_paths[f'mosaic{i}'] = request.build_absolute_uri(mosaic_url)
        return mosaic_paths
