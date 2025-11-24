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
1. Combines all the top-level properties into the base schema template (branding, pages etc)
2. Loads the widget base properties and creates a specific schema for each widget by combining it with every widget file
3. Creates a definition for each widget and reference it in the schema
4. Output schema to `schema.json`

