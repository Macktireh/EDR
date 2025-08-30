ARG PYTHON_BASE=3.13.5-slim-bookworm

# base image for Python
FROM docker.io/python:$PYTHON_BASE AS python_image

#############################################################################################
# -------------------------------------- build stage -------------------------------------- #
#############################################################################################
FROM python_image AS builder

# set work directory
WORKDIR /project

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg dependencies
  libpq-dev \
  # weasyprint dependencies
  libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 && \
  # install PDM
  pip install -U pdm && \
  # cleam
  rm -rf /var/lib/apt/lists/*

ENV PDM_CHECK_UPDATE=false

COPY pyproject.toml pyproject.toml
COPY pdm.lock pdm.lock

# install dependencies and project into the local packages directory
RUN pdm install

#############################################################################################
# -------------------------------------- final stage -------------------------------------- #
#############################################################################################
FROM python_image AS final

WORKDIR /project

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install --no-install-recommends -y \
  # weasyprint dependencies
  libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 && \
  rm -rf /var/lib/apt/lists/*

COPY --from=builder /project/.venv /.venv
ENV PATH=/.venv/bin:$PATH
ENV PYTHONPATH=/project/src

COPY ./docker/local/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./docker/local/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

ENTRYPOINT ["/entrypoint"]
