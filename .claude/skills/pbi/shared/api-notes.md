# DAX Formatter API Notes

**Verified:** 2026-03-12
**Status:** Legacy form-POST endpoint confirmed working; JSON endpoint returns 404

---

## Endpoint Verification Results

### Probe A — JSON endpoint (FAILED)

```
POST https://www.daxformatter.com/api/daxformatter/dax
Content-Type: application/json
Body: {"Dax":"Sales = SUM(Sales[Amount])","ListSeparator":",","DecimalSeparator":".","MaxLineLength":120}
```

**Result:** HTTP 301 → HTTP 404 (not found after redirect)
**Conclusion:** JSON endpoint does not exist at this path. Do NOT use.

### Probe B — Legacy form-POST endpoint (CONFIRMED WORKING)

```
POST https://www.daxformatter.com
Content-Type: application/x-www-form-urlencoded
Body: fx=<URL-encoded DAX>&r=US&embed=1
```

**Result:** HTTP 200 — returns HTML page fragment containing `<div class="formatted">` with the formatted DAX
**Conclusion:** This is the endpoint to use. The `embed=1` parameter suppresses most of the page HTML but the result still requires HTML tag stripping.

---

## Confirmed Endpoint

**URL:** `https://www.daxformatter.com`
**Method:** POST (form-encoded)
**Parameters:**

| Parameter | Value | Notes |
|-----------|-------|-------|
| `fx` | URL-encoded DAX measure text | Required — the DAX to format |
| `r` | `US` | Region — controls list/decimal separator conventions |
| `embed` | `1` | Returns page fragment instead of full HTML; still contains HTML tags |

**Example request:**
```bash
curl -s -L -X POST "https://www.daxformatter.com" \
  --data-urlencode "fx=Sales = SUM(Sales[Amount])" \
  -d "r=US&embed=1" \
  --max-time 10
```

---

## Response Format

The response is HTML containing a `<div class="formatted">` element.

**Raw response example** (for `Sales = SUM(Sales[Amount])`):
```html
<div class="formatted" >Sales&nbsp;=<br><span class="Keyword" style="color:#035aca">SUM</span><span class="Parenthesis" style="color:#808080">&nbsp;(</span>&nbsp;Sales[Amount]&nbsp;<span class="Parenthesis" style="color:#808080">)</span></div>
```

**After HTML stripping:**
```
Sales =
SUM ( Sales[Amount] )
```

---

## HTML Stripping — canonical parser

The canonical parser is `detect.py html-parse`:

```bash
python ".claude/skills/pbi/scripts/detect.py" html-parse "<tmpfile-with-response>"
```

Save the raw HTTP response to a temp file, then pass it to `html-parse`. It extracts the `<div class="formatted">` content, converts `<br>` to newlines, strips span/div tags, converts `&nbsp;` to spaces, **unescapes HTML entities** (`&lt;` `&gt;` `&amp;` etc. — so DAX operators like `<`, `>`, `&&` come back as real characters, not escaped text), normalises non-breaking spaces, and prints clean UTF-8 DAX. Do NOT use grep/sed pipelines for this — they miss entity-unescaping and break on accented characters.

---

## Probe Date and Validity

- **Probed:** 2026-03-12
- **Valid until:** Re-verify if endpoint stops working (monitor via API_FAIL fallback in skill)
- **Fallback:** If this endpoint breaks, the skill falls back to Claude inline SQLBI formatting with a one-line acknowledgement

---

## Notes

- The SQLBI blog post from 2014 documented this form-POST endpoint (https://www.sqlbi.com/blog/marco/2014/02/24/how-to-pass-a-dax-query-to-dax-formatter/) — it has remained stable for 12+ years
- The JSON endpoint used by the .NET NuGet package (`Dax.Formatter`) is not publicly accessible via the web domain; it may be restricted to the library or require different auth
- The `embed=1` parameter was confirmed to limit the response to just the formatted output div, avoiding full page HTML
