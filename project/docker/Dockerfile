FROM python:3.6
LABEL maintainer "devdatta khoche"
RUN apt-get update
RUN mkdir /loan
WORKDIR /loan
COPY . /loan
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["sh","project/docker/docker_script.sh"]
EXPOSE 5000
EXPOSE 5432
RUN chmod +x project/docker/docker_script.sh
CMD ["/bin/bash", "project/docker/docker_script.sh"]
