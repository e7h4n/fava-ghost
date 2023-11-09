FROM python:3

COPY favaghost/ ./fava-ghost/favaghost
COPY setup.py ./fava-ghost/
COPY README.md ./fava-ghost/
RUN cd fava-ghost && pip install --no-cache-dir -e .

ENTRYPOINT ["fava-ghost"]
CMD ["--repo-path", "/tmp/beancount", "--repo-url", "", "--repo-credentials", ""]