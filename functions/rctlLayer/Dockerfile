FROM lambci/lambda:build-python3.7

COPY . .

RUN mkdir -p bin/ && \
    curl -o bin/rctl.tar.bz2 https://s3-us-west-2.amazonaws.com/rafay-prod-cli/publish/rctl-linux-amd64.tar.bz2 && \
    tar -C bin -xf bin/rctl.tar.bz2 && \
    rm -f bin/rctl.tar.bz2 Dockerfile && \
    chmod +x bin/rctl && \
    zip -X -r lambda.zip ./

CMD mkdir -p /output/ && mv lambda.zip /output/