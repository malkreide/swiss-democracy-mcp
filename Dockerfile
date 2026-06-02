# Hardened container for cloud/HTTP deployment (audit SEC-007).
FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir --user .

FROM python:3.12-slim AS runtime
# Non-root user with high UID (audit SEC-007).
RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin mcp
COPY --from=builder /root/.local /home/mcp/.local
USER 10001
ENV PATH=/home/mcp/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    MCP_TRANSPORT=streamable_http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000
EXPOSE 8000
# Run read-only: `docker run --read-only --tmpfs /tmp --cap-drop ALL ...`
CMD ["python", "-m", "swiss_democracy_mcp.server"]
