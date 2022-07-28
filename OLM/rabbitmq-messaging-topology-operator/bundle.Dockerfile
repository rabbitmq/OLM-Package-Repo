FROM scratch

LABEL operators.operatorframework.io.bundle.mediatype.v1=registry+v1
LABEL operators.operatorframework.io.bundle.manifests.v1=manifests/
LABEL operators.operatorframework.io.bundle.metadata.v1=metadata/
LABEL operators.operatorframework.io.bundle.package.v1=rabbitmq-messaging-topology-operator
LABEL operators.operatorframework.io.bundle.channels.v1=stable
COPY 1.7.1/manifests /manifests/
COPY 1.7.1/metadata /metadata/
