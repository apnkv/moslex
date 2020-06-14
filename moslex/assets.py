from pathlib import Path

from clld.web.assets import environment

import moslex


environment.append_path(
    Path(moslex.__file__).parent.joinpath('static').as_posix(),
    url='/moslex:static/')
environment.load_path = list(reversed(environment.load_path))
