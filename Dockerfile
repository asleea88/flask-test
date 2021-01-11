FROM amazonlinux:2
LABEL maintainer="asleea88@gmail.com"

COPY ./requirements.txt /
RUN yum install -y python3.7 \
    && python3 -m pip install -U pip \
    && python3 -m pip install -r /requirements.txt \
    && yum clean all

COPY ./wanted /app
WORKDIR /app

CMD ["flask", "run", "--host", "0.0.0.0"]
