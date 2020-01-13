from fileshare.shared.database.Directory import Directory
from fileshare.shared.database.File import File

from fileshare.shared.database.common_query import CommonQuery

import os


def db_directory_to_api_resp(record: Directory) -> dict:
    content = {}

    if record.content_dir: 
        # If they contains directories.
        # without this check an empty string (no contents that is a folder) can exist and split will return [] which makes the query can't find anything
        # which it just means the directory doesn't contain any folders
        for folder in record.content_dir.split(","):
            dir_rel_path = os.path.join(record.rel_path, folder)
            dir_info = CommonQuery.query_dir_by_relative_path(dir_rel_path)
            content.update({
                dir_info.name: {
                    "name"      : dir_info.name,
                    "isDir"     : True,
                    "path"      : dir_info.rel_path.replace("\\", "/"),
                    "size"      : dir_info.size,
                    "last_mod"  : dir_info.last_mod,
                    "dir_count" : dir_info.dir_count,
                    "file_count": dir_info.file_count
                }
            })

    if record.content_file:
        for file in record.content_file.split(","):
            file_rel_path = os.path.join(record.rel_path, file)
            file_info = CommonQuery.query_file_by_relative_path(file_rel_path)
            content.update({
                file_info.name: {
                    "name"      : file_info.name,
                    "isDir"     : False,
                    "path"      : file_info.rel_path.replace("\\", "/"),
                    "size"      : file_info.size,
                    "last_mod"   : file_info.last_mod,
                    "mimetype"  : file_info.mimetype
                }
            })

    parent = record.rel_path.replace("\\", "/")

    return {parent: content}
