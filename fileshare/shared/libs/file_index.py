import os
import magic
import json


def abs_path_to_rel_path(abs_path: str, path_prefix: str) -> str:
    """Constructs a relative path from an absolute path
    
    The only thing this function does that is remove the common path 
    
    Arguments:
        abs_path {str} -- the absolute path that is going to be converted to relative path
        path_prefix {str} -- the path that the relative path is relative to
    
    Raises:
        AssersionError - Raises when the abs_path does not have the pre fix of path_prefix

    Returns:
        str -- the relative path that points to the same path as abs_path that is relative to path_prefix
                NOTE: When the abs path is the prefix path the return value with become empty
    """    
    if os.path.commonprefix((abs_path, path_prefix)) == path_prefix:
        rel_path = abs_path[len(path_prefix):]
        if not rel_path:
            rel_path = "\\" if os.name == "nt" else "/"
        return rel_path
    raise AssertionError("Unable to turn the absolute path into a relative path")


def get_file_info(path: str, dirpath: str, filename: str) -> dict:
    """
    Gets detailed infomation about a file on the filesystem should be used with os.walk

    Arguments:
        path {str} - the absolute path that points to the directory this is the argument from os.walk
        dirpath {str} - the directory path (can be both abs or rel path) the first item in the tuple that os.walk returns
        filename {str} - the name of the file

    Return:
        {dict} - the infomation gathered about the file see file_info for details. the dict's key is the relative path of the file
    """
    abs_path = os.path.abspath(os.path.join(path, dirpath, filename))
    rel_path = abs_path_to_rel_path(abs_path, path)
    last_mod = os.path.getmtime(abs_path)
    size     = os.path.getsize(abs_path)

    with open(abs_path, "rb") as f:
        buff = f.read(1024)

    mimetype = magic.from_buffer(buff, True)

    parent_path = rel_path[:len(rel_path) - len(filename)].rstrip(os.sep)
    if not parent_path: parent_path = os.sep

    file_info = {rel_path: 
        {
            "relative_path" : rel_path,
            "absolute_path" : abs_path,
            "parent_path"   : parent_path,
            "name"          : filename,
            "last_mod"      : last_mod,
            "size"          : size,
            "mimetype"      : mimetype,
        }}

    return file_info


def get_directory_extra_info(path: str) -> dict:
    """
    Gets the info of a directory which needs iteration through files

    Gets the file_count, directory count and size of the directory

    Arguments:
        path {str} - the path of the directory to retrieve extended infomation

    Return:
        {dict} - the infomation of the directory with key: [file_count, dir_count, size]
    """
    size = 0
    file_count = 0
    dir_count = 0
    for dirpath, dirs, files in os.walk(path):
        for file in files:
            path = os.path.join(dirpath, file)
            if not os.path.islink(path):  # Ignore symbolic link
                size += os.path.getsize(path)
    
        file_count += len(files)
        dir_count  += len(dirs)

    info = {
        "file_count": file_count,
        "dir_count" : dir_count,
        "size"      : size
    }

    return info


def get_directory_info(path: str, dirpath: str, file_content: dict, dir_content: list) -> dict:
    """
    Gets detailed infomation about a directory on the filesystem, should be used with os.walk

    Arguments:
        path {str} - the absolute path that points to the directory this is the argument from os.walk
        dirpath {str} - the directory path (can be both abs or rel path) the first item in the tuple that os.walk returns  
        file_content {dict} - the file content of the directory, should be dict
        dir_content {list} - list of first level sub directory should be the 2nd item in the tuple that os.walk returns

    Return:
        {dict} - the complete list of the sub directory and files under the directory. see dir_info variable to see details of the return content
    """
    abs_path     = os.path.abspath(os.path.join(path, dirpath))
    rel_path     = abs_path_to_rel_path(abs_path, path)

    info         = get_directory_extra_info(abs_path)
    size         = info["size"]
    file_count   = info["file_count"]
    dir_count    = info["dir_count"]

    last_mod     = os.path.getmtime(abs_path)
    file_content = file_content
    dir_content  = dir_content

    name = dirpath.split("/")[-1] if os.name != "nt" else dirpath.split("\\")[-1]

    dir_info = {
        "relative_path" : rel_path,
        "absolute_path" : abs_path,
        "parent_path"   : rel_path[:len(rel_path) - len(name)].rstrip(os.sep),
        "name"          : name,
        "last_mod"      : last_mod,
        "sub_dir_count" : dir_count,
        "sub_file_count": file_count,
        "size"          : size,
        "dir_content"   : dir_content,
        "file_content"  : file_content
    }

    return dir_info


def index_file(path: str) -> dict:
    """
    Indexes the files and directory under a certain directory

    Arguments:
        path {str} - the path of the DIRECTORY to index

    Return:
        {dict} - structures of the indexed directory
    """
    structure = {}  # Represents the directory structure

    for dirpath, directory, files in os.walk(path):
        all_files = {}
        for file in files:
            all_files.update(get_file_info(path, dirpath, file))

        node_info = get_directory_info(path, dirpath, all_files, directory)

        structure.update({dirpath: node_info})

    return structure

"""
Returned structure sample
{
    "D:\\PROG\\fileshare-flask\\.vscode": {
        "relative_path": "D:\\PROG\\fileshare-flask\\.vscode",
        "absolute_path": "D:\\PROG\\fileshare-flask\\.vscode",
        "name": ".vscode",
        "last_mod": 1575731299.6164553,
        "sub_dir_count": 22,
        "sub_file_count": 1197,
        "size": 82194107,
        "dir_content": [
            "cache"
        ],
        "file_content": {
            "D:\\PROG\\fileshare-flask\\.vscode\\c_cpp_properties.json": {
                "relative_path": "D:\\PROG\\fileshare-flask\\.vscode\\c_cpp_properties.json",
                "absolute_path": "D:\\PROG\\fileshare-flask\\.vscode\\c_cpp_properties.json",
                "name": "c_cpp_properties.json",
                "last_mod": 1575734872.063939,
                "size": 1537,
                "mimetype": "text/plain"
            },
            "D:\\PROG\\fileshare-flask\\.vscode\\launch.json": {
                "relative_path": "D:\\PROG\\fileshare-flask\\.vscode\\launch.json",
                "absolute_path": "D:\\PROG\\fileshare-flask\\.vscode\\launch.json",
                "name": "launch.json",
                "last_mod": 1573789875.4484072,
                "size": 887,
                "mimetype": "text/plain"
            },
            "D:\\PROG\\fileshare-flask\\.vscode\\settings.json": {
                "relative_path": "D:\\PROG\\fileshare-flask\\.vscode\\settings.json",
                "absolute_path": "D:\\PROG\\fileshare-flask\\.vscode\\settings.json",
                "name": "settings.json",
                "last_mod": 1575061423.5391603,
                "size": 514,
                "mimetype": "text/plain"
            }
        }
    },
    ...
}
"""

if __name__ == "__main__":
    path = input("Directory to index: ")
    with open("test.json", "w") as file:
        file.write(json.dumps(index_file(path)))
