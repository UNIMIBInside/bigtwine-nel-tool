FROM openjdk:8-stretch

RUN mkdir /tool \
  && cd /tool \
  && mkdir /data \
  && mkdir /kb
WORKDIR /tool

COPY kb/* /kb/
COPY tool/ /tool

CMD [ "python2", "/tool/main.py", "/data", "/kb" ]