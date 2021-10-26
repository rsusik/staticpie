<p align="center">
    <img src="https://raw.githubusercontent.com/rsusik/staticpie/main/staticpie.png" style="width: 130pt;" alt="StaticPIE" />
</p>
<p align="center">
    <em>Simple and extensible static site generator written in Python.</em>
</p>
<p align="center">
<a href="https://pypi.org/project/staticpie" target="_blank">
    <img src="https://img.shields.io/pypi/v/staticpie?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://github.com/rsusik/staticpie/blob/master/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/rsusik/staticpie" alt="Package version">
</a>
</p>

## Features
- simplicity
- extensibility
- **live update** (changes are visible in browser right after saving the file)
- jinja2 templates
- front matter markdown


## Installation
```shell
pip install staticpie
```

**Note: At least Python 3.8 version is required.**

## Create a new website
```shell
pie create website mywebsite
```

<img src="https://raw.githubusercontent.com/rsusik/staticpie/main/create_website.png" />

## Create page
```shell
pie create page anotherpage
```

<img src="https://raw.githubusercontent.com/rsusik/staticpie/main/create_page.png" />

## Edit page
The pages are editable front matter markdown files.
That means the pages are divided into two parts: 
- metadata part written in YAML
- content part written in Markdown

Both parts are separated by `---`.

### Serve the website

To edit page open the `*.md` file in any text file editor and run:
```shell
pie serve -c mywebsite/mywebsite.yaml
```

The command will generate the website in public folder (given in config file), run http server and open the website in browser.

After successfull execution of `serve` you should see screen similar to below:

<img src="https://raw.githubusercontent.com/rsusik/staticpie/main/serve.png" />

Once the file is saved, the browser refreshes the website (or some parts of it).

### Deployment

The serve action generates the website for localhost. That means it replaces all the addresses to localhost. The `deploy` option should be used to generate website with parameters given in yaml config file:
```shell
pie deploy 
```

<img src="https://raw.githubusercontent.com/rsusik/staticpie/main/deploy.png" />

## Configuration
The configuration is a YAML file and contains following elements:
* `PUBLIC_FOLDER` - where the website should be deployed (or served)
* `BASE_URL` - the website domain
* `PROTOCOL` - `http://` or `https://`
* `includes` - list of files that should be copied to public folder (css, js, imgs)
* `extensions` - list of extensions (elements) used on website
* and other elements (such as extension configs, etc.)


### Example configuration:
```yaml
# deployment folder
PUBLIC_FOLDER: ./public_www
# the URL used for deploy
BASE_URL: www.example.com
# the protocol http:// or https://
PROTOCOL: http://

# Folders/files that should be copied to public folder
includes:
    - assets
    - styles.css
    - styles.rtl.css

# Extensions
extensions:
    - menu
    - tags
    - pagelist
    - search
    - mostrecent

# Extension config
tags:
    tags_ignored:
        - movie
    tags_map:
        art:
            label: Article # the `art` tag will be displayed as Article
            order: 100
        art2:
            label: Annother article category
            order: 101
```

## Extensions
Most of the parts of this engine is written as extension. 

Writing a custom extension is straightforward and can be described in a few steps:

1. Create a python (`*.py`) file in the `extensions` folder inside the root webside folder. It can be also a folder with a `*.py` file of the same name. Example:
    ```
    mywebsite
    +- mywebsite.yaml
    +- extensions
       +- myextension.py    # 1st way
       +- anotherext        # 2nd way
          +- __init__.py
          +- anotherext.py
    +- ...
    ```
2. The extension file (i.e. `myextension.py`) contains a class that inherits from `Extension` class. Example:
    ```python
    from pie.core.extension import Extension
    class Myextension(Extension):
        ...
    ```

3. Finally, the `Myextension` class implements at least one of the following methods:
    * `on_generation_start`,
    * `preprocessing`,
    * `postprocessing`,
    * `on_generation_end`.

    The details can be found in `pie.core.extension.Extension` class.



Note: This project was created only for my use case and I suggest using some popular widely used frameworks such as Hugo or Jekyll for production.
