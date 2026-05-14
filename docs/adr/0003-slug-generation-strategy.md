# 0003: Slug Generation Strategy

Project slugs are generated in `Project.save()` when no manual slug is supplied. The generated slug is based on the title and appends `-2`, `-3`, and so on when collisions occur. Manual slugs are preserved so admin edits remain explicit.

