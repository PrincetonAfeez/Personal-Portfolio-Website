# 0004: SQLite Dev, Postgres Prod

SQLite keeps local setup fast and low-friction. Production reads `DATABASE_URL` through django-environ, so Railway can provide Postgres without changing application code.

