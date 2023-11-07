FROM python:3

COPY favaghost/__init__.py ./version.py
RUN pip install --no-cache-dir fava-ghost==`python version.py`

ENTRYPOINT ["fava-ghost"]
CMD ["--repo-path", "", "--repo-url", "", "--repo-credentials", ""]