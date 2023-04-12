FROM python:3-alpine

WORKDIR /action_app
COPY . .

RUN apk add git
RUN pip install -r requirements.txt

# gitpython needs uname under this path
RUN ln -s /bin/uname /usr/bin/uname

ENV PYTHONPATH /action_app
CMD ["python3", "/action_app/manage_package/manage_package.py"]
