
# set base image (host OS)
FROM python:3.9
ARG GITHUB_TOKEN
ARG LOGSIGHT_LIB_VERSION

RUN apt-get update && \
    apt-get -y install --no-install-recommends libc-bin openssh-client git-lfs && \
    rm -r /var/lib/apt/lists/*

# set the working directory in the container
WORKDIR /code

COPY ./requirements.txt .
# install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install "git+https://$GITHUB_TOKEN@github.com/aiops/logsight.git@$LOGSIGHT_LIB_VERSION"
RUN pip install "git+https://github.com/aiops/logsight-sdk-py.git@develop"



# copy code
COPY ./logsight_pipeline logsight_pipeline
# copy entrypoint.sh
COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh

# Set logsight home dir
ENV LOGSIGHT_HOME="/code/logsight_pipeline"
ENV PYTHONPATH="/code"

ENTRYPOINT [ "./entrypoint.sh" ]
