# google-chat-viewer

A cross-platform terminal viewer for **Google Chat Takeout exports**.

This tool lets you browse your exported Google Chat history directly inside the terminal with:

- Direct Messages (DMs)
- Spaces / Group chats
- Pinned-only mode
- Interactive selection using `fzf`
- Automatic Takeout ZIP detection + extraction
- Clean chat bubble rendering
- Works on Linux, macOS, and Windows (no `less` required)

---

## ✨ Features

✅ Browse Google Chat Takeout conversations in the terminal  
✅ DM + Space category selector  
✅ View only pinned messages instantly  
✅ Highlights pinned messages with `[PINNED]` marker  
✅ Auto-detects Takeout folder if already extracted  
✅ Auto-extracts latest `takeout-*.zip` from Downloads  
✅ Cross-platform pager using Python (`pydoc.pager`)  
✅ Emoji + Unicode-safe message alignment  

---

## 📦 Requirements

### Python

- Python **3.8+**

Check:

```bash
python3 --version
```

### Python Package

Install required module:

```bash
pip install wcwidth
```

### External Dependency: `fzf`

This tool uses `fzf` for interactive chat selection.

**Linux**

```bash
sudo apt install fzf
# or
sudo dnf install fzf
```

**macOS**

```bash
brew install fzf
```

**Windows**

Using Chocolatey:

```bash
choco install fzf
```

Or Winget:

```bash
winget install fzf
```

---

## 📂 Google Takeout Setup

1. Export your Google Chat data from Takeout:  
   https://takeout.google.com/
2. Download the ZIP file.
3. Place it inside your Downloads folder:

```
~/Downloads/takeout-xxxx.zip
```

OR extract it so this folder exists:

```
~/Downloads/Takeout/Google Chat/Groups
```

The script automatically detects either case.

---

## 🚀 Usage

Run the script:

```bash
python3 chat_viewer.py
```

### First Menu

You can choose:

- `DM` → Direct Messages
- `SPACE` → Group Spaces
- `PINNED ONLY` → Only pinned messages

### Navigation Inside Viewer

Once a chat opens:

- Search pinned messages:
  ```
  /PINNED
  ```

- Quit viewer:
  ```
  q
  ```

---

## 📌 Pinned Only Mode

Selecting **PINNED ONLY** will:

- Show only chats that contain pinned messages
- Display only pinned messages inside the conversation

---

## 🖥 Cross-Platform Support

| OS      | Supported |
|---------|-----------|
| Linux   | ✅ Yes    |
| macOS   | ✅ Yes    |
| Windows | ✅ Yes (with fzf installed) |

No need for `less` — pager is handled internally by Python.

---

## ⚠️ Notes / Limitations

- Attachments or non-text pinned messages are shown as:
  ```
  [Pinned message (non-text)]
  ```

- Multi-part Takeout ZIP exports (`-001.zip`, `-002.zip`) are not yet merged automatically.

---

## 📌 Roadmap / Future Improvements

- Full attachment rendering
- Multi-part ZIP support
- Pure Python selector (remove fzf dependency)
- Export pinned messages to a separate file

---

## 🤝 Contributing

Pull requests and suggestions are welcome!

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

See the [LICENSE](LICENSE) file for details.
