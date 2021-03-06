# Use an official Python runtime as a parent image
FROM python:2.7-alpine
# Set the working directory
WORKDIR /usr/src/app
# Copy the current directory contents into the container at /app
ADD . /usr/src/app

RUN apk update && apk add --virtual build-dependencies build-base gcc libxml2 libxml2-dev  libxslt-dev

# Update timezone
RUN apk add tzdata \
  && ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime \
  && echo "America/New_York" > /etc/timezone
# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
# Define environment variable
ENV NAME World
# Run app.py when the container launches
CMD ["python", "./scraper.py"]
