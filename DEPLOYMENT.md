# Deploy to Render

This project uses SQLite and local files for development. A production Render
deployment should use PostgreSQL, WhiteNoise for static assets, and an
S3-compatible bucket for uploaded event images, profile photos, and ticket QR
codes. Render provides `RENDER_EXTERNAL_HOSTNAME` automatically; Django uses it
for allowed hosts and HTTPS CSRF origins.

## 1. Create persistent services

1. In Render, create a managed PostgreSQL database. Choose a region and a plan
   suitable for your traffic and data-retention needs.
2. Create a private S3-compatible bucket in AWS S3 or Cloudflare R2.
3. Create bucket credentials with permission to list, read, write, and delete
   objects in that bucket. Keep the bucket private; Django generates signed
   media URLs.

For AWS S3, use the bucket's region and leave the endpoint URL unset. For
Cloudflare R2, use region `auto` and set the endpoint to
`https://<account-id>.r2.cloudflarestorage.com`.

## 2. Create the Render web service

Create a Web Service from this repository and select the `main` branch.
Configure:

**Build Command**

```sh
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command**

```sh
python manage.py migrate --noinput && gunicorn EventRegistration.wsgi:application --bind 0.0.0.0:$PORT
```

Gunicorn binds to Render's assigned port. The start command applies any pending
database migrations before serving requests.

## 3. Set environment variables

In the web service's **Environment** settings, add:

| Variable | Value |
|---|---|
| `DEBUG` | `False` |
| `SECRET_KEY` | Generate a new secret in Render; do not reuse the development key |
| `DATABASE_URL` | The PostgreSQL database's **internal** connection URL |
| `GEMINI_API_KEY` | Your Gemini API key |
| `AWS_STORAGE_BUCKET_NAME` | Your private bucket name |
| `AWS_ACCESS_KEY_ID` | The bucket access key |
| `AWS_SECRET_ACCESS_KEY` | The bucket secret key |
| `AWS_S3_REGION_NAME` | The bucket region (`auto` for R2) |
| `AWS_S3_ENDPOINT_URL` | R2 endpoint; omit for AWS S3 |

Render automatically supplies `RENDER_EXTERNAL_HOSTNAME`. For a custom domain,
also set `ALLOWED_HOSTS` to a comma-separated list of hostnames and
`CSRF_TRUSTED_ORIGINS` to a comma-separated list of full HTTPS origins, such as
`https://events.example.com`.

Do not commit these values or put production credentials in a repository `.env`
file.

## 4. Deploy and create an administrator

Trigger a deploy and review the build and runtime logs. The build should finish
`collectstatic`; the start command should finish migrations and report Gunicorn
listening on `0.0.0.0` and Render's port.

Use the Render service Shell to create the first administrator:

```sh
python manage.py createsuperuser
```

Then visit the service URL and check the home page, `/admin/`, static styling,
an image upload, QR ticket generation, and the Gemini chatbot.

## Notes

- PostgreSQL and the object-storage bucket retain data across web-service
  deploys. Do not use SQLite or Render's temporary service filesystem for
  production data or uploads.
- The start command runs migrations whenever the service starts. For multiple
  web instances, move migrations to a single pre-deploy or one-off command to
  avoid concurrent migration runs.
- `collectstatic` runs at build time and WhiteNoise serves the collected static
  files from the web service.
- Django's deployment check may recommend HSTS subdomain coverage or preload.
  Do not enable either automatically for a Render-managed hostname; enable them
  only after confirming the entire domain and all its subdomains support HTTPS.
- If deployment logs say no open ports were detected, confirm the Start Command
  uses Gunicorn with `--bind 0.0.0.0:$PORT`.
