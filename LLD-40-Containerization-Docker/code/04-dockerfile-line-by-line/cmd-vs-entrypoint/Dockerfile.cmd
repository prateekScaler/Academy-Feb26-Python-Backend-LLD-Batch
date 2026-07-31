# CMD = the DEFAULT command. Anything you type after `docker run <image>`
# REPLACES it entirely.
#
#   docker build -f Dockerfile.cmd -t democmd .
#   docker run --rm democmd                  -> python received argv: ['args.py']
#   docker run --rm democmd echo hijacked    -> hijacked          (CMD fully ignored!)
FROM python:3.12-slim
WORKDIR /app
COPY args.py .
CMD ["python", "args.py"]
