FROM python:3-alpine

WORKDIR /action_app
COPY . .

RUN pip install -r requirements.txt
RUN apk add git

# set the working directory to the checked out repo
WORKDIR /github/workspace

ENV PYTHONPATH /action_app
CMD ["python", "/action_app/manage_package/manage_package.py"]
