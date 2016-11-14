# JSON spec renderer for Django Rest Framework
JSON spec renderer for Django Rest Framework

## How to use ?
Copy code from the renderers.py in the renderers folder.
Create a file in your desired app in your Django Project, let the file name be renderers.py

### Set the renderer in your settings.py file
`
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'yourapp.renderers.APIRenderer',
    ),
}
`
