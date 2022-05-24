# pull official base image
FROM python:3.10.4-alpine3.15


# set working directory

WORKDIR /usr/src/app


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# install system dependencies
RUN apk -U upgrade --no-cache \
    && apk add --no-cache netcat-openbsd build-base postgresql trivy


# install python dependencies
RUN pip install --upgrade pip --no-cache-dir
COPY ./requirements.txt .
COPY ./requirements-dev.txt .
RUN pip install -r requirements-dev.txt --no-cache-dir

# clean build-base
RUN apk del build-base

# add app
COPY . .

# add entrypoint.sh
COPY ./entrypoint.sh .
RUN chmod +x /usr/src/app/entrypoint.sh


#run entrypoint.sh
ENTRYPOINT [ "/usr/src/app/entrypoint.sh" ]