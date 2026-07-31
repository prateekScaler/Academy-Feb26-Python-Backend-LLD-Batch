# ============================================================================
# LLD-40, Tier 1: the smallest useful Dockerfile.
#
# A Dockerfile is a RECIPE. `docker build` runs it top to bottom and each
# instruction bakes ONE LAYER into the image. Layers are cached: if a line
# (and every line above it) has not changed, Docker reuses the cached layer
# instead of rebuilding it. That is why ORDER matters: put the things that
# change rarely (base image) at the top, the things that change often
# (your code) near the bottom.
# ============================================================================

# LAYER 1 - the base image. This is the "starting filesystem": a tiny Debian
# Linux with Python 3.12 already installed. We PIN the version (3.12-slim,
# never `latest`) so the build is reproducible next month too.
# "slim" = no compilers/docs, ~120 MB instead of ~1 GB for the full image.
FROM python:3.12-slim

# LAYER 2 - set the working directory INSIDE the image. Every later COPY/RUN/
# CMD happens here. Also creates /app if it does not exist ("mkdir -p" + "cd").
WORKDIR /app

# LAYER 3 - copy app.py from the build context (the folder you run `docker
# build` in, on your machine) into /app inside the image. This is the layer
# that changes every time you edit your code -- so it sits LAST, and the
# expensive layers above it stay cached.
COPY app.py .

# NOT a layer -- metadata. CMD records the default command a container runs
# on `docker run`. Exec form (JSON array) means "run python directly", with
# no shell wrapper in between (signals like Ctrl+C reach python cleanly).
CMD ["python", "app.py"]
