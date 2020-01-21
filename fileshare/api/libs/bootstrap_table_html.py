class _BootstrapTableHtmlTemplate:
    T_NAME_DIRECTORY: str           = """<a href="javascript:changeDirectory('{path}')">{name}</a>"""
    T_NAME_FILE: str                = """<a href="{path}">{name}</a>"""


    T_OPS_OPEN_FILE_NEW_TAB: str    = """<a class="ops-btn" href="{path}" target="_blank"><i class="fa fa-fw fa-external-link" aria-hidden="true"></i></a>"""
    T_OPS_OPEN_DIR_NEW_TAB: str     = """<a class="ops-btn" href="/?path={path}" target="_blank"><i class="fa fa-fw fa-external-link" aria-hidden="true"></i></a>"""

    T_OPS_DOWNLOAD: str             = """<a class="ops-btn" href="javascript:downloadFile('{path}')" ><i class="fa fa-fw fa-download" aria-hidden="true"></i></a>"""

    T_OPS_DELETE: str               = """<a class="ops-btn" href="{path}" ><i class="fa fa-fw fa-trash-o" aria-hidden="true"></i></a>"""
    
    T_OPS_RENAME: str               = """<a class="ops-btn" href="{path}" ><i class="fa fa-fw fa-pencil-square-o" aria-hidden="true"></i></a>"""
    
    T_OPS_MOVE: str                 = """<a class="ops-btn" href="{path}" ><i class="fa fa-fw fa-exchange" aria-hidden="true"></i></a>"""


class BootstrapTableHtmlFormatter:
    @staticmethod
    def name_to_html_link(name, path, is_file):
        if is_file:
            return _BootstrapTableHtmlTemplate.T_NAME_FILE.format(path=path, name=name)
        return _BootstrapTableHtmlTemplate.T_NAME_DIRECTORY.format(path=path, name=name)


    @staticmethod
    def generate_ops(name, path, is_file):
        complete_html_string = ""

        complete_html_string = complete_html_string + _BootstrapTableHtmlTemplate.T_OPS_DOWNLOAD.format(path=path)

        if is_file:
            complete_html_string = complete_html_string + _BootstrapTableHtmlTemplate.T_OPS_OPEN_FILE_NEW_TAB.format(path=path)

        else:
            complete_html_string = complete_html_string + _BootstrapTableHtmlTemplate.T_OPS_OPEN_DIR_NEW_TAB.format(path=path)

        return complete_html_string
