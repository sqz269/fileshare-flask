class _BootstrapTableHtmlTemplate:
    T_NAME_DIRECTORY: str           = """<a href="javascript:changeDirectory('{path}')">{name}</a>"""
    T_NAME_FILE: str                = """<a href="{path}">{name}</a>"""


    T_OPS_OPEN_FILE_NEW_TAB: str    = """<a class="ops-btn" href="{path}" target="_blank"><i class="fas fa-fw fa-external-link-square-alt"></i></a>"""
    T_OPS_OPEN_DIR_NEW_TAB: str     = """<a class="ops-btn" href="/?path={path}" target="_blank"><i class="fas fa-fw fa-external-link-square-alt"></i></a>"""

    T_OPS_PREVIEW: str              = """<a class="ops-btn" href="{path}"><i class="fas fa-eye"></i><a>"""

    T_OPS_DOWNLOAD_FOLDER: str      = """<a class="ops-btn" href="javascript:downloadFile('{path}', true)" ><i class="fas fa-fw fa-download" aria-hidden="true"></i></a>"""
    T_OPS_DOWNLOAD_FILE: str        = """<a class="ops-btn" href="javascript:downloadFile('{path}', false)" ><i class="fas fa-fw fa-download" aria-hidden="true"></i></a>"""


    T_OPS_DELETE: str               = """<a class="ops-btn" href="javascript:deleteItem('{path}')" ><i class="fas fa-fw fa-trash"></i></i></a>"""

    T_OPS_RENAME: str               = """<a class="ops-btn" href="{path}" ><i class="fas fa-fw fa-edit"></i></a>"""

    T_OPS_MOVE: str                 = """<a class="ops-btn" href="{path}" ><i class="fas fa-fw fa-exchange-alt"></i></a>"""


class BootstrapTableHtmlFormatter:
    @staticmethod
    def name_to_html_link(name, path, is_file):
        if is_file:
            return _BootstrapTableHtmlTemplate.T_NAME_FILE.format(path=path, name=name)
        return _BootstrapTableHtmlTemplate.T_NAME_DIRECTORY.format(path=path, name=name)


    @staticmethod
    def generate_ops(name, path, is_file):
        complete_html_string = ""
        if is_file:
            complete_html_string = complete_html_string + _BootstrapTableHtmlTemplate.T_OPS_OPEN_FILE_NEW_TAB.format(path=path)
            complete_html_string = complete_html_string + _BootstrapTableHtmlTemplate.T_OPS_PREVIEW.format(path=path)

        else:
            complete_html_string = complete_html_string + _BootstrapTableHtmlTemplate.T_OPS_OPEN_DIR_NEW_TAB.format(path=path)


        return complete_html_string
