## HOW TO USE
1º - Start the application
Build and run the containers using Docker:
```bash
docker compose --profile full --profile tools up
```
### 2º - In your browser, go to: ```http://localhost:8000/docs```;
### 3º - In Swagger, find the /upload/ endpoint.
You must provide the following files:
- 1. Energy_losses - put this file: ![alt text](../image/md/image-4.png)
- 2. gdb - ![alt text](../image/md/image-1.png)
- 3. indicadores_continuidade - ![alt text](../image/md/image-2.png)
- 4. indicadores_continuidade_limite - ![alt text](../image/md/image-3.png)

And after execute

#### OBS: Look with calm the files extension
### 4º After execution, gonna show the files id.
![alt text](../image/md/image-5.png)

So, will be necessary each id and put on /upload/status/{load_id} API. For example:
<br>
![alt text](../image/md/image-6.png)
<br>
Will to return to you this message:
<br>
![alt text](../image/md/image-7.png)