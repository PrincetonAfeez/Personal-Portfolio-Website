# Schema Folder

Schema files for `PrincetonAfeez/Personal-Portfolio-Website`.

This repository is a Django + HTMX portfolio site. These files document the main data structures used by the Django apps:

- `projects`: portfolio projects, tags, and technology stack items
- `about`: skills and timeline entries
- `contact`: saved contact form submissions

## Files

| File | Purpose |
| --- | --- |
| `projects.schema.json` | JSON Schema for `Project`, `Tag`, and `TechStack` records. |
| `about.schema.json` | JSON Schema for `Skill` and `TimelineEntry` records. |
| `contact.schema.json` | JSON Schema for `ContactSubmission` and contact form input. |
| `database_schema.sql` | Simple relational database schema reference based on the Django models. |
| `schema_index.json` | Machine-readable index of the schema files. |

## Notes

- The SQL file is documentation/reference, not a replacement for Django migrations.
- The JSON Schema files are useful for validation, API documentation, seed data, exports, or frontend contracts.
- Generated on 2026-05-14.
