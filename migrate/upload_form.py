# Import Module
import os

import json
import requests

access_token = ''


class Worker:
    """
    Drop all tables. Load default data from user.json and insert into new database
    """

    def __init__(self):
        self.path = "forms"
        # Change the directory
        os.chdir(self.path)
        self.url_upload_file = 'http://localhost:5000/api/v1/admin/upload?prefix=forms'
        self.url_create_form = 'http://localhost:5000/api/v1/admin/forms'
        self.url_sign_in = 'http://localhost:5000/api/v1/admin/auth/login'

    def login_with_admin_user(self):
        """Login with admin user
        Return:
            access_token: string
        """
        # get access token
        response = requests.post(
            self.url_sign_in,
            json={
                "username": "tiennguyenhuu1999@gmail.com",
                "password": "123456"
            }
        )
        json_response = json.loads(response.content.decode())
        data = json_response['data']
        global access_token
        access_token = data['access_token']

    def upload_file(self, file_name):
        file = {'file': open(file_name, 'rb')}
        data_upload = requests.post(
            self.url_upload_file,
            headers={
                'Authorization': 'Bearer {}'.format(access_token)},
            files=file
        )
        response = json.loads(data_upload.content.decode())
        file_url = response.get("data").get("file_url")
        return file_url

    def create_form(self, file_name):
        file_url = self.upload_file(file_name)
        name = file_name.replace(".doc", "")
        body = {'name': name, 'description': name, 'link': file_url}
        data_upload = requests.post(
            self.url_create_form,
            headers={'Content-Type': 'application/json',
                     'Authorization': 'Bearer {}'.format(access_token)},
            json=body
        )
        response = json.loads(data_upload.content.decode())
        print(response)


if __name__ == '__main__':
    worker = Worker()
    worker.login_with_admin_user()
    for title in os.listdir():
        worker.create_form(title)
