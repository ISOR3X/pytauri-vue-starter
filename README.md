![src/assets/banner.png](src/assets/banner.png)

## Getting started

From project root, enter the following commands:

```Command prompt
uv venv --python-preference only-system
.venv\Scripts\activate
uv pip install -e src-tauri\src-python
npm install
```

You can then run the app with:

```Command prompt
npm run tauri dev
```

### Setting up for development in JetBrains IDEAs

##### Webstorm - for frontend development

1. Add a new run configuration -> npm
2. Command: `run`, Scripts: `tauri`, Arguments: `dev`
3. Add a new environment variable named `VIRTUAL_ENV`. Its value should be an absolute path pointing to the virtual
   environment, e.g. `C:\Users\...\...\pytauri-vue-starter\.venv`.

#### PyCharm - for python development

_Requires PyCharm professional_

1. Set the python interpreter (should be the `python.exe` in  `.venv\Scripts`)
2. Open a terminal, make sure the virtual environment is activated.
3. Install pydevd for PyCharm
```
uv pip install pydevd-pycharm~=243.25659.43
```
4. Add the following code to the top of `__init__.py`
```python
import pydevd_pycharm
pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True) 
```
5. Add a new run configuration -> Python Debug Server
6. IDE host name: `localhost`, Port: `5678`
7. Run the Python Debug Server before starting the npm server.  
You can now set breakpoints as you usually would to debug your python code