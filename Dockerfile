FROM node:24-slim AS frontend
WORKDIR /build
RUN corepack enable && corepack prepare pnpm@11.25.0 --activate
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build
FROM python:3.12-slim
WORKDIR /app
COPY requirements-lock.txt ./
RUN pip install --no-cache-dir -r requirements-lock.txt
COPY backend/ backend/
COPY src/ src/
COPY scripts/ scripts/
COPY app.py alembic.ini ./
COPY --from=frontend /build/dist frontend/dist/
RUN mkdir -p data artifacts && useradd -u 10001 orion && chown -R orion:orion /app
USER orion
EXPOSE 8000
CMD ["sh","-c","python -m alembic upgrade head && python scripts/seed.py && uvicorn app:app --host 0.0.0.0 --port 8000"]
