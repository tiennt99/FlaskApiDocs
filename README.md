# BACKEND-MANGER-USER

## mockaroo

[user table](https://www.mockaroo.com/schemas/371785)

## Diagram

![Mô hình quan hệ](/diagram.png "Diagram")

## Link APIs

[Link postman](https://www.getpostman.com/collections/42e2eaac580593a9294a)

## run project

### Cài đặt môi trường

  ```sh
  pip install -r requirements 
  ```

### Khởi tạo database ứng với db trong settings.py

Tạo database *doan* trong mysql

  ```sh
CREATE DATABASE IF NOT EXISTS doan CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
  ```

Trong thư mục migrate

  ```sh
 python init_db.py
  ```

### run project

  ```sh
 python manage.py
  ```