# syntax=docker/dockerfile:1

FROM ubuntu:24.04 AS base
RUN echo base

FROM base
USER app
HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost/ || exit 1
