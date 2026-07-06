# Man page

```python exec="on"
import io

from helpers.docs import write_man_md

buffer = io.StringIO()
write_man_md(buffer)
print(buffer.getvalue())
```
