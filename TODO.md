# OSS-TUI TODO

## In Progress

- [ ] Complete FilesystemProvider implementation (read-only done, write operations pending)

## High Priority

### Provider Implementation
- [x] Implement AliyunOSSProvider (Alibaba Cloud OSS)
  - [x] All CRUD operations (list_buckets, list_objects, get/put/delete/copy_object)
  - [x] Cross-region bucket access (auto-detect bucket location)
  - [x] Bucket object caching
  - [x] Exception handling (convert oss2 exceptions to custom exceptions)
  - [x] Unit tests with mocking
  - [x] Integration tests (require OSS credentials)
- [x] Add provider factory/registry for dynamic provider loading
- [x] Add configuration-based provider selection

### Future Provider Improvements
- [ ] Optimize bucket cache strategy (LRU, TTL)
- [ ] Large file streaming support for get_object

### UI Features
- [ ] Implement `Ctrl+d` / `Ctrl+u` for page down/up
- [ ] Add loading indicators for async operations

### File Operations
- [x] Download file (`D` key)
- [x] Upload file (`u` key)
- [x] Delete file/directory (`d` key with confirmation)
- [ ] Copy file (`y` to yank, `p` to paste)
- [ ] Rename/move file

## Medium Priority

### UI Enhancements
- [ ] Add help modal (`?` key) with full keybinding reference
- [x] Add account/provider switching (`a` key)
- [ ] Implement multi-select (need new keybinding, `Space` now used for preview)
- [ ] Add breadcrumb navigation in path bar
- [ ] Improve styling and color scheme
- [ ] Add file type icons (directory, file, image, etc.)

### Provider Expansion
- [ ] Implement S3Provider (AWS S3)
- [ ] Implement MinIOProvider
- [ ] Implement COSProvider (Tencent Cloud COS)

### Configuration
- [x] Load provider config from config.toml
- [x] Support multiple accounts/profiles
- [x] Add command-line arguments for provider/root selection

## Low Priority

### Testing
- [ ] Add TUI integration tests using textual's test framework
- [x] Add AliyunOSSProvider unit tests (with mocking)
- [ ] Increase test coverage

### Documentation
- [ ] Add usage examples to README
- [ ] Document keybindings in detail
- [ ] Add screenshots/GIFs to documentation

### Polish
- [ ] Add clipboard integration for copy operations
- [ ] Add progress bar for large file transfers
- [ ] Implement undo for delete operations
- [ ] Add bookmarks/favorites feature

## Completed

- [x] Project skeleton setup
- [x] FilesystemProvider basic implementation
- [x] Pagination support for list_objects
- [x] Error handling (BucketNotFoundError, ObjectNotFoundError)
- [x] TUI dual-pane layout (bucket list + file list)
- [x] Vim-style navigation (j/k/g/G/l/h) - Note: `g` is single key, Textual doesn't support `g g`
- [x] Directory enter/back navigation
- [x] Tab to switch panes
- [x] Refresh functionality
- [x] Search/filter functionality (`/` key) with live filtering and ESC to cancel
- [x] File preview (`Space` key) with syntax highlighting for text files
  - Modal overlay (90% x 80%), focus locked
  - Text files: syntax highlighting via rich.Syntax
  - Binary files: metadata only
  - Large files (>100KB): truncated with warning
  - Vim-style scrolling (j/k/g/G/Ctrl+d/u) in preview
  - ESC/q to close preview
- [x] File size and date columns in file list
- [x] AliyunOSSProvider full implementation with cross-region support
- [x] Provider factory/registry for dynamic provider loading
- [x] Configuration-based provider selection (from config.toml)
- [x] Command-line arguments (`-c/--config`, `-a/--account`)
- [x] Account switching with `a` key (cycles through configured accounts)
- [x] Download file (`D` key) with path input modal
- [x] Upload file (`u` key) with path input modal
- [x] Delete file/directory (`d` key) with confirmation modal
