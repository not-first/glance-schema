# Glance Schema
*A JSON schema detailing the [Glance](https://github.com/glanceapp/glance) config file.*

> [!NOTE]
> Currently represents version: v0.8.4. Now supports validation of split config files using [`$include`](https://github.com/glanceapp/glance/blob/main/docs/configuration.md?tab=readme-ov-file#including-other-config-files)!

> [!WARNING]
> Although split config files can now be validated using the new exposed definitions, full schema support for $include is still being ironed out. Expect some errors here and there, even though your config file may be correct!

## Usage
The schema is available at: `https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json`

### Main Config File (glance.yml)

For your main `glance.yml` configuration file:

1. Install the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) for VS Code.
2. At the top of your `glance.yml` file, add this line:
   ```yaml
   # yaml-language-server: $schema=https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json
   ```
3. Done! You'll now get typing completions, hover descriptions, and validation errors.

### Split Config Files

The schema now supports validating split config files using the `$include` directive. Here are examples for common use cases:

#### Single Widget Files

For files containing a single widget to be included (e.g., `widgets/weather.yml`):

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json#/definitions/widget

type: weather
location: New York, United States
```

#### Multiple Widget Files (Array)

For files containing multiple widgets (e.g., `widgets/rss.yml`):

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json#/definitions/widget-array

- type: rss
  title: Tech News
  feeds:
    - url: https://example.com/tech/feed

- type: rss
  title: World News
  feeds:
    - url: https://example.com/world/feed
```

#### Single Page Files

For files containing a single page (e.g., `pages/home.yml`):

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json#/definitions/page

name: Home
columns:
  - size: full
    widgets:
      - type: rss
        title: News
```

#### Multiple Page Files (Array)

For files containing multiple pages (e.g., `pages/dashboards.yml`):

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json#/definitions/page-array

- name: Dashboard 1
  columns:
    - size: full
      widgets:
        - type: monitor
          title: System Monitor

- name: Dashboard 2
  columns:
    - size: full
      widgets:
        - type: server-stats
```

#### Using $include in Your Main Config

Example `glance.yml` with includes:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json

server:
  port: 8080

pages:
  - $include: pages/home.yml          # Single page
  $include: pages/dashboards.yml      # Multiple pages
  - name: Inline Page
    columns:
      - size: full
        widgets:
          - $include: widgets/weather.yml  # Single widget
          $include: widgets/rss.yml        # Multiple widgets
          - type: clock                    # Inline widget
```

**Important:** How you use `$include` depends on the file's content:
- **Single item files** (using `#/definitions/widget` or `#/definitions/page`): Use `- $include:` with a dash, because the file contains one object that becomes an array item
- **Array files** (using `#/definitions/widget-array` or `#/definitions/page-array`): Use `$include:` without a dash, because the file already contains array items with dashes that will be merged in

### Automatic Schema Application for Folders

For projects with dedicated folders for widgets and pages, you can configure VS Code to automatically apply the appropriate schema without adding comments to each file.

Add this to your `.vscode/settings.json`:

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json": ["glance.yml"],
    "https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json#/definitions/widget": ["widgets/*.yml"],
    "https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json#/definitions/page": ["pages/*.yml"]
  }
}
```

**Note:** The above configuration uses the singular `widget` and `page` schemas. If your files typically contain arrays of multiple widgets/pages, you can use `widget-array` and `page-array` instead:

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json": ["glance.yml"],
    "https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json#/definitions/widget-array": ["widgets/*.yml"],
    "https://raw.githubusercontent.com/not-first/glance-schema/master/schema.json#/definitions/page-array": ["pages/*.yml"]
  }
}
```

This configuration:
- Applies the main schema to `glance.yml`
- Applies the widget/widget-array schema to all `.yml` files in the `widgets/` folder
- Applies the page/page-array schema to all `.yml` files in the `pages/` folder

#### Recommended Project Structure

```
your-project/
├── glance.yml           # Main config file
├── .vscode/
│   └── settings.json    # VS Code schema configuration
├── pages/
│   ├── home.yml         # Single page
│   ├── dashboard.yml    # Single page
│   └── monitoring.yml   # Single page or multiple pages
└── widgets/
    ├── rss.yml          # Single widget or array of widgets
    ├── weather.yml      # Typically a single widget
    └── stats.yml        # Single widget or array of widgets
```


## Known Limitations
Some error messages can be autogenerated by the schema validator and are unhelpful in figuring out what is wrong. These can be customised in the schema once they are located, so please create an issue if you experience one.

