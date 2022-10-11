# pull official base image
FROM python:3.9.6-alpine

# set work directory
WORKDIR /usr/src/merge_contacts

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk add --no-cache gcc musl-dev linux-headers
COPY ./requirements.txt .
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . .

ENTRYPOINT ["/usr/src/merge_contacts/entrypoint.sh"]
