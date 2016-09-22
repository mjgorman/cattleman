FROM python:3.5.2-alpine
MAINTAINER Michael Gorman "michael@michaeljgorman.com"
RUN mkdir -p /app/
ADD cattleman.py /app/
WORKDIR /app/
CMD [ "python3", "cattleman.py" ]
