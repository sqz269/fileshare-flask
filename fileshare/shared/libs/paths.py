import errno, os
from urllib.parse import unquote

# Refer following path validating functions to this stackoverflow post
# https://stackoverflow.com/questions/9532499/check-whether-a-path-is-valid-in-python-without-creating-a-file-at-the-paths-ta

# Sadly, Python fails to provide the following magic number for us.
ERROR_INVALID_NAME = 123
def is_pathname_valid(pathname: str) -> bool:
    '''
    `True` if the passed pathname is a valid pathname for the current OS;
    `False` otherwise.
    '''
    # If this pathname is either not a string or is but is empty, this pathname
    # is invalid.
    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        # Strip this pathname's Windows-specific drive specifier (e.g., `C:\`)
        # if any. Since Windows prohibits path components from containing `:`
        # characters, failing to strip this `:`-suffixed prefix would
        # erroneously invalidate all valid absolute Windows pathnames.
        _, pathname = os.path.splitdrive(pathname)

        # Directory guaranteed to exist. If the current OS is Windows, this is
        # the drive to which Windows was installed (e.g., the "%HOMEDRIVE%"
        # environment variable); else, the typical root directory.
        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if os.name == 'nt' else os.path.sep
        assert os.path.isdir(root_dirname)   # ...Murphy and her ironclad Law

        # Append a path separator to this directory if needed.
        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

        # Test whether each path component split from this pathname is valid or
        # not, ignoring non-existent and non-readable path components.
        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            # If an OS-specific exception is raised, its error code
            # indicates whether this pathname is valid or not. Unless this
            # is the case, this exception implies an ignorable kernel or
            # filesystem complaint (e.g., path not found or inaccessible).
            #
            # Only the following exceptions indicate invalid pathnames:
            #
            # * Instances of the Windows-specific "WindowsError" class
            #   defining the "winerror" attribute whose value is
            #   "ERROR_INVALID_NAME". Under Windows, "winerror" is more
            #   fine-grained and hence useful than the generic "errno"
            #   attribute. When a too-long pathname is passed, for example,
            #   "errno" is "ENOENT" (i.e., no such file or directory) rather
            #   than "ENAMETOOLONG" (i.e., file name too long).
            # * Instances of the cross-platform "OSError" class defining the
            #   generic "errno" attribute whose value is either:
            #   * Under most POSIX-compatible OSes, "ENAMETOOLONG".
            #   * Under some edge-case OSes (e.g., SunOS, *BSD), "ERANGE".
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    # If a "TypeError" exception was raised, it almost certainly has the
    # error message "embedded NUL character" indicating an invalid pathname.
    except TypeError as exc:
        return False
    # If no exception was raised, all path components and hence this
    # pathname itself are valid. (Praise be to the curmudgeonly python.)
    else:
        return True
    # If any other exception was raised, this is an unrelated fatal issue
    # (e.g., a bug). Permit this exception to unwind the call stack.
    #
    # Did we mention this should be shipped with Python already?


# def is_directory_traversal(file_name):
#     current_directory = os.path.abspath(os.curdir)
#     requested_path = os.path.relpath(file_name, start=current_directory)
#     requested_path = os.path.abspath(requested_path)
#     common_prefix = os.path.commonprefix([requested_path, current_directory])
#     return common_prefix != current_directory


def make_abs_path_from_url(uri: str, file_directory: str, fix_nt_path=True) -> bytes:
    """Constructs a absolute path from an uri 
    
    Arguments:
        uri {str} -- uri the user requested
        file_directory {str} -- the shared directory path
    
    Keyword Arguments:
        fix_nt_path {bool} -- try to overcome the NT path limit (255 chars) by add "\\\\?\\" in font of the path (calls fix_long_windows_path on the path string)
                                Only will happen if the os.name is nt (default: {True})
    
    Raises:
        AssertionError: It only raises if the commonprefix of the joined path does not match the shared path (file_directory)
                            which is used as a measure to counter possible directory traversal attack

        FileNotFoundError: Raises when the check of is_pathname_valid check returned false which signifies the constructed file path is not valid
    
    Returns:
        bytes -- the absolute path constructed from the uri
    """
    uri = unquote(uri)

    path = os.path.join(file_directory, uri.lstrip("/"))  # Remove the / in the front else the join will recognize it as root

    if (os.path.commonprefix((os.path.realpath(path), file_directory)) != file_directory):  
        # Prevent Directory Traversal Attack
        # https://stackoverflow.com/questions/45188708/how-to-prevent-directory-traversal-attack-from-python-code
        raise AssertionError("Bruh nice try")

    if is_pathname_valid(path):
        if os.name == 'nt' and fix_nt_path:
            return fix_long_windows_path(path)
        return path.encode()  # Be consistant with fix_long_windows_path so this func will always return bytes

    raise FileNotFoundError("INVALID PATH")


def fix_long_windows_path(path: str) -> bytes:
    """Work around for NT system's 256 character path limit
    https://stackoverflow.com/questions/1880321/why-does-the-260-character-path-length-limit-exist-in-windows
    
    Arguments:
        path {str} -- path to the file that needs to be NT long path capable
    
    Returns:
        [bytes] -- path that with \\\\?\\ prefixed with all forward slashes (/) replaced by backward slash (\\) and encoded via utf-8
    """
    long_path = "\\\\?\\" + path.replace("/", "\\")
    return long_path.encode()
