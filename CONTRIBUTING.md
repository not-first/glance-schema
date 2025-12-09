## Contribution

Any help in maintaining the schema is appreciated. This may include:
- Adding new widgets
- Updating widget properties as they change
- Updating property descriptions to be more specific/helpful
- Updating property examples
- Adding installation instructions for more environments into this README

### Schema Generation Script
In order to make building the schema easier, it is split into a file per each base property (e.g server, branding, pages) and widgets. A python script is then run to build a singular JSON file for the schema.

#### Local Testing
To test locally, run the schema generation script using `uv`:
```bash
uv run scripts/generate-schema.py
```
This will generate a `schema.json` at the root of the repo. Then use:
```
yaml-language-server: $schema=file://{PATH_TO_YOUR_SCHEMA.JSON}
```
at the top of any `glance.yml` to test the locally generated version of the schema (in vscode).

**Remove this `schema.json` file from your commit**, as it is built by a Github Action on push to ensure consistency. A locally generated schema will function the same as one generated automatically.

#### Script Functionality
1. Combines all the top-level properties into the base schema template (branding, pages, server, etc.)
2. Loads the widget base properties and creates a specific schema for each widget by combining it with every widget file
3. Creates definitions for:
   - `widget`: A single widget object (with `$include` support)
   - `widget-array`: An array of widgets (for include files with multiple widgets)
   - `page`: A single page object (with `$include` support)
   - `page-array`: An array of pages (for include files with multiple pages)
   - `include`: The `$include` directive definition
4. Injects `$include` support globally by wrapping definitions with `oneOf` to allow either the original schema or an include directive
5. Outputs the complete schema to `schema.json`

#### Schema Definitions for Split Config Files
The schema supports Glance's `$include` directive for splitting configurations:

- **`#/definitions/widget`**: For single widget files (one widget object without array syntax)
- **`#/definitions/widget-array`**: For files containing multiple widgets (array with dashes)
- **`#/definitions/page`**: For single page files (one page object without array syntax)
- **`#/definitions/page-array`**: For files containing multiple pages (array with dashes)
- **`#/definitions/include`**: The `$include` directive itself (injected into all definitions)

When adding or modifying widgets, the script automatically generates both singular and array definitions.

