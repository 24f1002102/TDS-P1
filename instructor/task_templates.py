"""
Task templates for different rounds.
"""
import json
import hashlib
from datetime import datetime


TASK_TEMPLATES = [
    {
        "id": "sum-of-sales",
        "brief": "Publish a single-page site that fetches data.csv from attachments, sums its sales column, sets the title to \"Sales Summary {seed}\", displays the total inside #total-sales, and loads Bootstrap 5 from jsdelivr.",
        "attachments": [
            {
                "name": "data.csv",
                "generator": "generate_sales_csv"
            }
        ],
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page title equals 'Sales Summary {seed}'",
            "Page loads Bootstrap from CDN",
            "Element #total-sales displays correct sum"
        ],
        "round2": [
            {
                "brief": "Add a Bootstrap table #product-sales that lists each product with its total sales and keeps #total-sales accurate after render.",
                "checks": [
                    "Table #product-sales has at least one row",
                    "Sum of product sales matches #total-sales"
                ]
            },
            {
                "brief": "Introduce a currency select #currency-picker that converts the computed total using rates.json from attachments and mirrors the active currency inside #total-currency.",
                "attachments": [
                    {
                        "name": "rates.json",
                        "generator": "generate_exchange_rates"
                    }
                ],
                "checks": [
                    "Select #currency-picker has USD option",
                    "Element #total-currency exists"
                ]
            },
            {
                "brief": "Allow filtering by region via #region-filter, update #total-sales with the filtered sum, and set data-region on that element to the active choice.",
                "checks": [
                    "Element #region-filter is a SELECT",
                    "Element #total-sales has data-region attribute"
                ]
            }
        ]
    },
    {
        "id": "markdown-to-html",
        "brief": "Publish a static page that converts input.md from attachments to HTML with marked, renders it inside #markdown-output, and loads highlight.js for code blocks.",
        "attachments": [
            {
                "name": "input.md",
                "generator": "generate_markdown"
            }
        ],
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Page loads marked library",
            "Page loads highlight.js",
            "Element #markdown-output contains HTML headings"
        ],
        "round2": [
            {
                "brief": "Add tabs #markdown-tabs that switch between rendered HTML in #markdown-output and the original Markdown in #markdown-source while keeping content in sync.",
                "checks": [
                    "Element #markdown-tabs has at least 2 buttons",
                    "Element #markdown-source has non-empty text content"
                ]
            },
            {
                "brief": "Support loading Markdown from a ?url= parameter when present and fall back to the attachment otherwise, showing the active source in #markdown-source-label.",
                "checks": [
                    "Element #markdown-source-label has text content",
                    "Code includes fetch() call"
                ]
            },
            {
                "brief": "Display a live word count badge #markdown-word-count that updates after every render and formats numbers with Intl.NumberFormat.",
                "checks": [
                    "Element #markdown-word-count contains comma",
                    "Code uses Intl.NumberFormat"
                ]
            }
        ]
    },
    {
        "id": "github-user-created",
        "brief": "Publish a Bootstrap page with form id=\"github-user-{seed}\" that fetches a GitHub username, optionally uses ?token=, and displays the account creation date in YYYY-MM-DD UTC inside #github-created-at.",
        "attachments": [],
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Form #github-user-{seed} exists",
            "Element #github-created-at displays date in YYYY-MM-DD format",
            "Code fetches from GitHub API"
        ],
        "round2": [
            {
                "brief": "Show an aria-live alert #github-status that reports when a lookup starts, succeeds, or fails.",
                "checks": [
                    "Element #github-status has aria-live='polite'",
                    "Code updates #github-status"
                ]
            },
            {
                "brief": "Display the account age in whole years inside #github-account-age alongside the creation date.",
                "checks": [
                    "Element #github-account-age displays integer >= 0",
                    "Text includes 'years'"
                ]
            },
            {
                "brief": "Cache the last successful lookup in localStorage under \"github-user-{seed}\" and repopulate the form on load.",
                "checks": [
                    "Code uses localStorage.setItem for 'github-user-{seed}'",
                    "Code uses localStorage.getItem for 'github-user-{seed}'"
                ]
            }
        ]
    }
]


def generate_sales_csv(seed: str) -> str:
    """Generate a sample sales CSV file."""
    products = ["Widget", "Gadget", "Doohickey", "Thingamajig", "Whatchamacallit"]
    regions = ["North", "South", "East", "West"]
    
    import random
    random.seed(seed)
    
    lines = ["product,region,sales"]
    for _ in range(20):
        product = random.choice(products)
        region = random.choice(regions)
        sales = round(random.uniform(100, 1000), 2)
        lines.append(f"{product},{region},{sales}")
    
    return "\n".join(lines)


def generate_exchange_rates(seed: str) -> str:
    """Generate exchange rates JSON."""
    rates = {
        "USD": 1.0,
        "EUR": 0.85,
        "GBP": 0.73,
        "JPY": 110.0,
        "INR": 74.0
    }
    return json.dumps(rates, indent=2)


def generate_markdown(seed: str) -> str:
    """Generate sample Markdown content."""
    return f"""# Sample Document

This is a sample Markdown document generated with seed: {seed}

## Features

- **Bold text**
- *Italic text*
- `Code snippets`

## Code Block

```python
def hello():
    print("Hello, World!")
```

## Conclusion

This is a test document.
"""


def get_seed(email: str, timestamp: datetime = None) -> str:
    """Generate a seed for parametrizing tasks."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    # Format: YYYY-MM-DD-HH
    date_str = timestamp.strftime("%Y-%m-%d-%H")
    seed_input = f"{email}-{date_str}"
    
    # Hash to get consistent seed
    return hashlib.sha256(seed_input.encode()).hexdigest()[:8]


def parametrize_template(template: dict, seed: str) -> dict:
    """Replace {seed} placeholders in template with actual seed."""
    template_str = json.dumps(template)
    parametrized_str = template_str.replace("{seed}", seed)
    return json.loads(parametrized_str)


def generate_attachments(attachments_config: list, seed: str) -> list[dict]:
    """Generate actual attachment data URIs from config."""
    import base64
    
    attachments = []
    for config in attachments_config:
        generator_name = config.get("generator")
        if generator_name:
            # Call generator function
            content = globals()[generator_name](seed)
            
            # Encode as data URI
            encoded = base64.b64encode(content.encode()).decode()
            
            # Determine MIME type
            name = config["name"]
            if name.endswith(".csv"):
                mime = "text/csv"
            elif name.endswith(".json"):
                mime = "application/json"
            elif name.endswith(".md"):
                mime = "text/markdown"
            else:
                mime = "text/plain"
            
            attachments.append({
                "name": name,
                "url": f"data:{mime};base64,{encoded}"
            })
    
    return attachments
