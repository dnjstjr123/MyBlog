import os
import cv2
import pathlib
import requests
import sys
import json
from datetime import datetime
inform =""
class ChangeDetection:
    result_prev = []
    HOST = 'http://127.0.0.1:8000'
    username = 'admin'
    password = 'cdt3486@'
    token = ''
    title = ''
    text = ''

    def __init__(self, names):
        self.result_prev = [0 for i in range(len(names))]
        res = requests.post(self.HOST + '/api-token-auth/', {
            'username': self.username,
            'password': self.password,
        })
        res.raise_for_status()
        self.token = res.json()['token'] #토큰 저장
        print(self.token)

    def add(self, names, detected_current, save_dir, image):
        self.title = ''
        self.text = ''
        change_flag = 0 #변화 감지 플레그
        i=0
        global inform
        while i < len(self.result_prev):
            if self.result_prev[i]==0 and detected_current[i]==1 :
                change_flag = 1
                self.title = names[i]
                self.text += inform
            i += 1

        self.result_prev = detected_current[:] # 객체 검출 상태 저장
        
        if change_flag==1:
            self.send(save_dir, image)
        inform = ''
    def send(self, save_dir, image):
  

        now = datetime.now()
        now.isoformat()

        today = datetime.now()
        save_path = os.getcwd() / save_dir / 'detected' / str(today.year) / str(today.month) / str(today.day)
        pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)
        
        full_path = save_path / '{0}-{1}-{2}-{3}.jpg'.format(today.hour,today.minute,today.second,today.microsecond)
        
        dst = cv2.resize(image, dsize=(320, 240), interpolation=cv2.INTER_AREA)
        cv2.imwrite(full_path, dst)
        client_id = "A5i0JfgJKzYhnGOZ2PVy"
        client_secret = "qqp8SWJhrL"
        url = "https://openapi.naver.com/v1/vision/face" 
        files = {'image': open(full_path, 'rb')}
        headers = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret }
        response = requests.post(url,  files=files, headers=headers)
        rescode = response.status_code
        data = json.loads(response.text)

        global inform
        if "faces" in data and data["faces"]:
            inform += "성별: " + data["faces"][0]["gender"]["value"] +", 나이: "+data["faces"][0]["age"]["value"]+", 감정: "+data["faces"][0]["emotion"]["value"]
        else:
            inform += "얼굴 데이터를 찾을 수 없습니다."
        # 인증이 필요한 요청에 아래의 headers를 붙임
        headers = {'Authorization' : 'JWT ' + self.token, 'Accept' : 'application/json'}
        
        # Post Create
        data = {
        'title' : self.title,
        'text' : inform,
        'created_date' : now,
        'published_date' : now,
        }
        file = {'image' : open(full_path, 'rb')}
        res = requests.post(self.HOST + '/api_root/Post/', data=data, files=file, headers=headers)
        print(res)