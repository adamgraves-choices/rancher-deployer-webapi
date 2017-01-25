FROM python:alpine

ENV RANCHER_CLI_VERSION='v0.4.1'

RUN apk --no-cache add openssl && \
    wget -qO- https://github.com/rancher/cli/releases/download/${RANCHER_CLI_VERSION}/rancher-linux-amd64-${RANCHER_CLI_VERSION}.tar.gz | tar xvz -C /tmp && \
    mv /tmp/rancher-${RANCHER_CLI_VERSION}/rancher /usr/local/bin/rancher && \
    chmod +x /usr/local/bin/rancher && \
    rm -r /tmp/rancher-${RANCHER_CLI_VERSION}

RUN pip install flask

COPY deployer_listener.py /deployer_listener.py

EXPOSE 5000

CMD python /deployer_listener.py
