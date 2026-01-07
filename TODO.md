# OSS-TUI TODO

## In Progress

- [ ] Complete FilesystemProvider implementation (read-only done, write operations pending)

## High Priority

### Provider Implementation
- [ ] Implement AliyunOSSProvider (Alibaba Cloud OSS)
- [ ] Add provider factory/registry for dynamic provider loading
- [ ] Add configuration-based provider selection

### UI Features
- [ ] Add search/filter functionality (`/` key)
- [ ] Implement file preview (text files, images metadata)
- [ ] Add file size and date columns to file list
- [ ] Implement `Ctrl+d` / `Ctrl+u` for page down/up
- [ ] Add loading indicators for async operations

### File Operations
- [ ] Download file (`D` key)
- [ ] Upload file (`u` key)
- [ ] Delete file/directory (`d` key with confirmation)
- [ ] Copy file (`y` to yank, `p` to paste)
- [ ] Rename/move file

## Medium Priority

### UI Enhancements
- [ ] Add help modal (`?` key) with full keybinding reference
- [ ] Add account/provider switching (`a` key)
- [ ] Implement multi-select with `Space` key
- [ ] Add breadcrumb navigation in path bar
- [ ] Improve styling and color scheme
- [ ] Add file type icons (directory, file, image, etc.)

### Provider Expansion
- [ ] Implement S3Provider (AWS S3)
- [ ] Implement MinIOProvider
- [ ] Implement COSProvider (Tencent Cloud COS)

### Configuration
- [ ] Load provider config from config.toml
- [ ] Support multiple accounts/profiles
- [ ] Add command-line arguments for provider/root selection

## Low Priority

### Testing
- [ ] Add TUI integration tests using textual's test framework
- [ ] Add AliyunOSSProvider unit tests (with mocking)
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
- [x] Vim-style navigation (j/k/g/G/l/h)
- [x] Directory enter/back navigation
- [x] Tab to switch panes
- [x] Refresh functionality
