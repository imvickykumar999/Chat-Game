# `Call GPT`

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
````

![image](https://github.com/user-attachments/assets/5bc9831c-ac38-4f8f-a3a8-d761b66a5ce2)


| Action | Command | Purpose |
| :--- | :--- | :--- |
| **Download Image** | `docker pull imvickykumar999/myadk-django:latest` | Downloads the application image from Docker Hub to your local machine. |
| **Initial Run** | `docker run -d -p 8000:8000 --name myadk-web-production imvickykumar999/myadk-django:latest` | Creates and starts a **new** container from the image in detached mode, naming it `myadk-web-production` and mapping the ports. |
| **Stop Container** | `docker stop myadk-web-production` | **Gracefully stops** the running container. |
| **Start Container** | `docker start myadk-web-production` | **Restarts** the previously stopped container. |
| **View Running** | `docker ps` | Lists all currently **running** containers. |
| **View All** | `docker ps -a` | Lists **all** containers (running, stopped, etc.). |
| **Remove Container** | `docker rm myadk-web-production` | **Deletes** the container from your system (must be stopped first). |
| **Force Stop** | `docker kill myadk-web-production` | Immediately **forces** the container to stop (less graceful than `docker stop`). |
