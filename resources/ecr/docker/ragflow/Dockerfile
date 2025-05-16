FROM infiniflow/ragflow:v0.18.0

# Set default environment variables (can be overridden at runtime)
ENV RAGFLOW_WORKERS=5
ENV RAGFLOW_ENABLE_WEBSERVER=1
ENV RAGFLOW_ENABLE_TASKEXECUTOR=1

# Override the service configuration
COPY service_conf.yaml.template /ragflow/conf/service_conf.yaml.template

# Override the entrypoint script
COPY entrypoint.sh /ragflow/entrypoint.sh
RUN chmod +x /ragflow/entrypoint.sh

# Keep the same entrypoint command
ENTRYPOINT ["./entrypoint.sh"]
