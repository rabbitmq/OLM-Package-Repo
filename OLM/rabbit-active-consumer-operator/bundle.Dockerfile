FROM scratch

LABEL operators.operatorframework.io.bundle.mediatype.v1=plain
LABEL operators.operatorframework.io.bundle.manifests.v1=manifests/
LABEL operators.operatorframework.io.bundle.metadata.v1=metadata/
LABEL operators.operatorframework.io.bundle.package.v1=rabbitmq-single-active-consumer-operator
LABEL operators.operatorframework.io.bundle.channels.v1=stable
COPY 0.2.2/manifests /manifests/
COPY 0.2.2/metadata /metadata/
