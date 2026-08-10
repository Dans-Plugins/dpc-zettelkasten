# The explorer is two generated-but-committed files, site/index.html and
# site/dataset.json. Both are self-contained — no external requests, no build
# step, no server-side logic — so this image is a static server and a copy.
#
# The committed artifacts are served as they are, rather than rebuilt during
# docker build. CI already fails when site/ does not match the notes (see
# .github/workflows/build.yml), so an image cannot be built from drifted
# artifacts, and rebuilding here would put Python into a container that
# otherwise has no use for it. Please do not "fix" this by adding a build stage.
FROM nginxinc/nginx-unprivileged:1.27-alpine

# The base image already runs as uid 101 and already listens on 8080. Both are
# wanted here, so neither is overridden below.

COPY site/ /usr/share/nginx/html/

# The GraphQL engine is published alongside the dataset so another origin can
# run the same queries against the same data with no build step. It is a UMD
# module, so a browser gets it as window.ZKGraphQL from a plain script tag.
COPY lib/zk-graphql.js /usr/share/nginx/html/lib/zk-graphql.js

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

# The check itself answers in well under 100 ms; the timeout is loose because
# it is competing with whatever else the host is doing, and a busy box briefly
# starving one wget is not the container being unwell.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
