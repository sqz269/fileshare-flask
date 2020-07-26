class _BootstrapTableHtmlTemplate:
    T_NAME_DIRECTORY: str           = """<a href="javascript:changeDirectory('{path}')">{name}</a>"""
    T_NAME_FILE: str                = """<a href="{path}">{name}</a>"""


    T_OPS_OPEN_FILE_NEW_TAB: str    = """<a class="dropdown-item" href="{path}" target="_blank">Open (New tab)</a>"""
    T_OPS_OPEN_DIR_NEW_TAB: str     = """<a class="dropdown-item" href="/?path={path}" target="_blank">Open (New tab)</i></a>"""

    T_OPS_PREVIEW: str              = """<a class="dropdown-item" href="{path}">Open (Preview)<a>"""

    T_OPS_DOWNLOAD_FOLDER: str      = """<a class="dropdown-item" href="javascript:downloadFile('{path}', true)" >Download</a>"""
    T_OPS_DOWNLOAD_FILE: str        = """<a class="dropdown-item" href="javascript:downloadFile('{path}', false)" >Download</a>"""

    T_OPS_COPY_NORMALIZED_PATH: str = """<a class="dropdown-item" href="javascript:copyPathToClipboard('{path}')" >Copy Path (Escaped)</a>"""

    T_OPS_DELETE: str               = """<a class="dropdown-item" href="javascript:deleteItem('{path}')" >Delete</a>"""

    T_OPS_RENAME: str               = """<a class="dropdown-item" href="{path}" >Rename</a>"""

    T_OPS_MOVE: str                 = """<a class="dropdown-item" href="{path}" >Move</a>"""


class BootstrapTableHtmlFormatter:
    @staticmethod
    def name_to_html_link(name, path, is_file):
        if is_file:
            return _BootstrapTableHtmlTemplate.T_NAME_FILE.format(path=path, name=name)
        return _BootstrapTableHtmlTemplate.T_NAME_DIRECTORY.format(path=path, name=name)

    @staticmethod
    def generate_ops(name, path, is_file):
        complete_html_string = """<div class="dropdown">
                                  <button class="btn btn-sm btn-block dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                    Show Operations
                                  </button>
                                  <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">"""
        if is_file:
            complete_html_string = complete_html_string + _BootstrapTableHtmlTemplate.T_OPS_OPEN_FILE_NEW_TAB.format(path=path)
            complete_html_string = complete_html_string + _BootstrapTableHtmlTemplate.T_OPS_PREVIEW.format(path=path)
            complete_html_string = complete_html_string + _BootstrapTableHtmlTemplate.T_OPS_DELETE.format(path=path)
            complete_html_string = complete_html_string + _BootstrapTableHtmlTemplate.T_OPS_DOWNLOAD_FILE.format(path=path)
            complete_html_string = complete_html_string + _BootstrapTableHtmlTemplate.T_OPS_COPY_NORMALIZED_PATH.format(path=path)
        else:
            complete_html_string = complete_html_string + _BootstrapTableHtmlTemplate.T_OPS_OPEN_DIR_NEW_TAB.format(path=path)

        complete_html_string = complete_html_string + "</div></div>"
        return complete_html_string
