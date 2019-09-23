# pull official base image
FROM python:3.7.4-alpine

# set work directory
WORKDIR /usr/src/app

# set system-wide environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system-wide dependencies
RUN apk update
RUN apk add --virtual build-deps gcc python3-dev musl-dev
RUN apk add postgresql-dev


# copy project
COPY . /usr/src/app/

# install project dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Remove unnecessary dependencies
RUN apk del build-deps

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]