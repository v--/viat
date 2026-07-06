# Usage

```python exec="on"
import io

from helpers.docs import write_usage_md

buffer = io.StringIO()
write_usage_md(buffer)
print(buffer.getvalue())
```
