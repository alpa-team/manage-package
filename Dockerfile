FROM python:3-alpine

WORKDIR /action_app
COPY . .

RUN apk add git
RUN pip install -r requirements.txt

ENV PYTHONPATH /action_app
CMD ["python", "/action_app/manage_package/manage_package.py"]
