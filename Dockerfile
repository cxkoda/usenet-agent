FROM rackspacedot/python37:latest
ADD https://api.github.com/repos/cxkoda/usenet-agent/git/refs/heads/master version.json
RUN git clone https://github.com/cxkoda/usenet-agent.git; \
  cd usenet-agent; \
  pip3 install --upgrade pip; \
  pip3 install -r requirements.txt

CMD python3 usenet-agent/watchdog.py
