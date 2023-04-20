vk_token =
ya_token = 
vk_ask = 
vk_count = int(input("Сколько фотографий сохранить: "))

import json
import requests
from pprint import pprint
import time
from tqdm import tqdm


class VK_photo:
    def __init__(self, token: str):
        self.token = token 
                        
    def get_id(self, name):
        URL = 'https://api.vk.com/method/utils.resolveScreenName'
        params = {
                "screen_name" : name,
                'access_token': vk_token, #нужен токен
                'v':'5.131'
                }
        res = requests.get(URL, params=params).json()
        return res['response']['object_id']

    def photo_upload (self, ID):
        URL = 'https://api.vk.com/method/photos.get'
        params = {
            "owner_id" : ID,
            'album_id' : 'profile',
            'access_token': vk_token, #нужен токен
            'extended' : 'likes',
            'photo_sizes': '1',
            'v':'5.131',
            'count': vk_count
        }
        res = requests.get(URL, params=params).json()
        photos = res['response']['items']
        return photos

    def get_all_photos(self, photoy):
        photo_list = {}
        for i in photoy:
            for j in i['sizes']:
                for k, f in j.items():
                    if k == 'type' and f == 'w' or "z" or "y": 
                        url_photo = (j['url'])
                        date = str(i['date'])
                        likes = str(i['likes']['count'])
                        ld = likes + '_' + date + '.jpg'
                        info = {'file_name':ld,'size':j['type']}
                        url_info = {url_photo:info}
                        photo_list[ld] = url_info
        return photo_list 
            

class YaUploader:
    def __init__(self, token: str):
        self.token = token 
        self.url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        self.headers = {
                    'Content-type':'application/json',
                    'Authorization':'OAuth {}'.format(self.token),
                    
                    }
                    
    def get_upload_link(self, file_path, vk_url):
        params = {"path": file_path, "url": vk_url}
        response = requests.get(self.url, self.headers , params = params)
        data = response.json()
        href = data.get('href')
        return href
        
    def new_folder (self, file_path):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {
                    'Content-type':'application/json',
                    'Authorization':'OAuth {}'.format(self.token),
                }
        params = {"path": f'/{file_path}'}
        response = requests.get(url, headers= headers, params=params)
        new_fold = requests.put(url, headers= headers, params=params)
        return file_path
    
    def upload(self, file_path, name):
        params = {"path": file_path, "url": vk_url, "name" : name}
        response = requests.post(self.url, headers = self.headers, params=params)
        if response.status_code == 202:
            for i in tqdm(range(2), desc = 'Photo',leave=False, ncols= 100):
                time.sleep(.5)
            print ('Фото загружено:',counter,"/",vk_count)
        else:
            print("Код ошибки:",response.status_code)
    
    def get_upload_link_json(self, file_path):
        params = {"path": file_path, "overwrite":"true"}
        response = requests.get(self.url, headers = self.headers, params = params)
        data = response.json()
        href = data.get('href')
        return href
    
    def upload_json(self, file_path, name):
        href = self.get_upload_link_json(file_path=file_path)
        response = requests.put(href, data=open(name, 'rb'))
        if response.status_code == 201:
            for i in tqdm(range(2), desc = 'Info_file', leave=False, ncols= 100):
                time.sleep(.5)
            print ('Информационный файл загружен.')
        else:
            print("Код ошибки:",response.status_code)
            
if any(c.isalpha() for c in vk_ask) == True:
    vk_id = VK_photo.get_id(vk_token, vk_ask)
else:
    vk_id = vk_ask

if __name__ == '__main__': 
    downloader = VK_photo(vk_token)
    uploader = YaUploader(ya_token)
    new_fold = uploader.new_folder(vk_id)
    counter = 1
    infoa = {}
    for name, vk_url in downloader.get_all_photos(downloader.photo_upload(vk_id)).items():
        path_to_file = (f"{new_fold}/{name}")
        for url, info in vk_url.items():
            uploader.upload(path_to_file, name)
            infoa[("Файл №:"+ str(counter+1))] = info
        counter += 1


with open('info.json', 'w', encoding = 'utf-8') as y:
    json.dump(infoa, y, sort_keys=False, ensure_ascii=False)
    y.close()

with open('info.json',encoding = 'utf-8') as f:  
    data = json.load(f)
    path_json = (f"{new_fold}/info.json") 
    result = uploader.upload_json(path_json, 'info.json')    
