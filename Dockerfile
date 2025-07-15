FROM python:3.8.1

# Create docker user
RUN addgroup --gid 1000 docker \
 && adduser --uid 1000 --gid 1000 --disabled-password --gecos "Docker User" docker \
 && usermod -L docker

# Fix sources for old Buster
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list \
 && sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list'

ENV DEBIAN_FRONTEND=noninteractive

# Use update ignoring validity
RUN apt-get update -o Acquire::Check-Valid-Until=false \
 && apt-get upgrade -y \
 && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    locales \
    postgresql-client \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/

# Set locale
ENV LANG       en_US.UTF-8
ENV LC_ALL     en_US.UTF-8
ENV LANGUAGE   en_US.UTF-8
RUN echo "LC_ALL=en_US.UTF-8" >> /etc/environment \
 && echo "en_US.UTF-8 UTF-8"  >> /etc/locale.gen  \
 && echo "LANG=en_US.UTF-8"   > /etc/locale.conf
RUN locale-gen en_US.UTF-8
RUN dpkg-reconfigure locales

RUN pip install pipenv

RUN mkdir /app \
 && chown -R docker:docker /app

WORKDIR /app
USER docker

COPY --chown=docker:docker Pipfile /app/Pipfile
COPY --chown=docker:docker Pipfile.lock /app/Pipfile.lock

RUN pipenv install

COPY --chown=docker:docker . /app

CMD ./scripts/start_app.sh