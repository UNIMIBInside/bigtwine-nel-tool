FROM openjdk:8-stretch

RUN mkdir /tool
WORKDIR /tool
COPY . /tool

CMD [ "java", "-jar", "NEEL_Linking.jar" ]