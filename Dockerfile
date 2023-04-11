FROM python:3-alpine

WORKDIR /action_app
COPY . .

RUN pip install -r requirements.txt

ENV PYTHONPATH /action_app
CMD ["/action_app/manage_package/manage_package.py"]
