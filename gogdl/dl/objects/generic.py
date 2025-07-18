from dataclasses import dataclass
from enum import Flag, auto
from fnmatch import fnmatch
import os
from typing import Optional


class BaseDiff:
    def __init__(self):
        self.deleted = []
        self.new = []
        self.changed = []
        self.redist = []
        self.removed_redist = []

        self.links = [] # Unix only

    def __str__(self):
        return f"Deleted: {len(self.deleted)} New: {len(self.new)} Changed: {len(self.changed)}"

class TaskFlag(Flag):
    NONE = 0
    SUPPORT = auto()
    OPEN_FILE = auto()
    CLOSE_FILE = auto()
    CREATE_FILE = auto()
    CREATE_SYMLINK = auto()
    RENAME_FILE = auto()
    COPY_FILE = auto()
    DELETE_FILE = auto()
    OFFLOAD_TO_CACHE = auto()
    MAKE_EXE = auto()
    PATCH = auto()
    RELEASE_MEM = auto()
    ZIP_DEC = auto()

@dataclass
class MemorySegment:
    offset: int
    end: int

    @property
    def size(self):
        return self.end - self.offset

@dataclass
class ChunkTask:
    product: str
    index: int

    compressed_md5: str
    md5: str
    size: int
    download_size: int
    
    cleanup: bool = False
    offload_to_cache: bool = False
    old_offset: Optional[int] = None
    old_flags: TaskFlag = TaskFlag.NONE 
    old_file: Optional[str] = None

@dataclass
class V1Task:
    product: str
    index: int
    offset: int
    size: int
    md5: str
    cleanup: Optional[bool] = True

    old_offset: Optional[int] = None
    offload_to_cache: Optional[bool] = False
    old_flags: TaskFlag = TaskFlag.NONE 
    old_file: Optional[str] = None

    # This isn't actual sum, but unique id of chunk we use to decide 
    # if we should push it to writer
    @property
    def compressed_md5(self):
        return self.md5 + "_" + str(self.index)

@dataclass
class FileTask:
    path: str
    flags: TaskFlag

    old_flags: TaskFlag = TaskFlag.NONE 
    old_file: Optional[str] = None

    patch_file: Optional[str] = None


@dataclass
class TerminateWorker:
    pass

class FileExlusion:
    def matches(file, exclude_list):
                for pattern in exclude_list:
                    if '/' in pattern and '/' in file.path: #If pattern contains a seperator, check dirname and basename seperately. Ensures that only files in specified directories are excluded.
                        if os.path.dirname(file.path) == os.path.dirname(pattern) and fnmatch(os.path.basename(file.path), os.path.basename(pattern)):
                            return True
                    else:
                        if fnmatch(file.path, pattern):
                            return True
                return False
