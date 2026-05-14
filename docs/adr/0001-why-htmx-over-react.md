# 0001: Why HTMX Over React

The portfolio uses HTMX because the interaction model is mostly server-owned: project filters, contact validation, and pagination can be rendered as partial templates. This keeps the stack aligned with Django, avoids a duplicate API surface, and demonstrates progressive enhancement instead of client-side application state.

