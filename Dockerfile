FROM python:3-alpine

WORKDIR /action_app
COPY . .

RUN pip install -r requirements.txt
RUN apk add git

ENV PYTHONPATH /action_app
CMD ["python", "/action_app/manage_package/manage_package.py"]
