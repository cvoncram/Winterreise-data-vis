# Debian-based rather than Alpine: SciPy publishes prebuilt wheels for glibc,
# so the image builds in seconds. On Alpine (musl) pip would fall back to
# compiling it from source, pulling in a Fortran toolchain.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies before source, so that editing code does not invalidate the
# layer that installs them.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The private key is mounted at run time and must never be part of the image;
# .dockerignore excludes it from the build context so it cannot arrive here by
# accident. This check makes that guarantee visible rather than implicit.
RUN test ! -e winterreise-database-test.2026-02-09.private-key.pem \
    || (echo "FEHLER: privater Schlüssel liegt im Abbild" && exit 1)

RUN useradd --create-home --uid 1000 app && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
