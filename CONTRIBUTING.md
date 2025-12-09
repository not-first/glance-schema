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
   - `widget-item`: Internal single widget object definition
   - `widget`: An array of widgets (primary consumer-facing definition for widget files)
   - `page-item`: Internal single page object definition
   - `page`: An array of pages (primary consumer-facing definition for page files)
   - `include`: The `$include` directive definition
4. Injects `$include` support globally by wrapping definitions with `oneOf` to allow either the original schema or an include directive
5. Outputs the complete schema to `schema.json`

#### Schema Definitions for Split Config Files
The schema supports Glance's `$include` directive for splitting configurations:

- **`#/definitions/widget`**: For widget include files (always arrays, even for single widgets)
- **`#/definitions/page`**: For page include files (always arrays, even for single pages)
- **`#/definitions/widget-item`**: Internal definition for individual widget objects (used within arrays)
- **`#/definitions/page-item`**: Internal definition for individual page objects (used within arrays)
- **`#/definitions/include`**: The `$include` directive itself (injected into all definitions)

When adding or modifying widgets or pages, the script automatically generates the appropriate definitions and maintains consistency between singular and array usage.

