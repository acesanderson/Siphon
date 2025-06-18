To "Flatten" a git repo is to convert it to an xml object that is easy for LLMs to understand.

4 scripts:

## 📁 **flatten_xml.py** - Shared XML Logic
- **`EXCLUDE_PATTERNS`** & **`INCLUDE_EXTENSIONS`** - Single source of truth
- **`create_directory_tree_xml()`** - Generic directory tree builder
- **`create_file_contents_xml()`** - Generic file contents with CDATA
- **`package_to_xml()`** - Main orchestrator function
- **`format_xml()`** - Pretty printing with minidom

## 📁 **flatten_directory.py** - Local Directory Processing
- **`flatten_directory()`** - Main function for local dirs
- **`get_local_file_iterator()`** - Walks filesystem with `os.walk()`
- **`read_local_file()`** - Reads from filesystem
- Handles relative paths and path normalization

## 📁 **flatten_url.py** - GitHub Repository Processing  
- **`flatten_github_repo()`** - Main function for GitHub repos
- **`parse_github_url()`** - Converts GitHub URLs to API endpoints
- **`download_github_repo()`** - Downloads and returns ZipFile
- **`get_github_file_iterator()`** - Iterates over zip contents
- **`create_github_file_reader()`** - Reads from zip with path mapping

## 📁 **Flatten.py** - CLI Entry Point
- **`main()`** - Argument parsing and dispatch
- Detects GitHub URLs vs local paths
- Clean error handling and help text
- Single responsibility: just CLI logic

## Benefits of This Architecture:

✅ **~70% code reduction** through shared XML logic  
✅ **Single source of truth** for exclude patterns and file types  
✅ **Easily testable** - each module has clear responsibilities  
✅ **Consistent output** - both modes use identical XML generation  
✅ **Extensible** - easy to add new sources (GitLab, file uploads, etc.)  

The core insight was making the XML generation **source-agnostic** by using callback functions for file reading and path iteration. Now both local and GitHub processing just provide different implementations of "how to read a file" and "how to list files" - everything else is shared!
