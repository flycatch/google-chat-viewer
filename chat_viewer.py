import sys
import platform
import importlib.util
import os
import json
import subprocess
import textwrap
from datetime import datetime
import shutil
import zipfile
import pydoc
from wcwidth import wcswidth

# ==============================
# Dependency Checks
# ==============================


def check_dependencies():
    print("🔍 Checking requirements...\n")

    # ---- Python Version ----
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required.")
        print("Your version:", sys.version)
        sys.exit(1)

    # ---- wcwidth module ----
    if importlib.util.find_spec("wcwidth") is None:
        print("❌ Missing Python package: wcwidth\n")
        print("Install it using:\n")
        print("   pip install wcwidth\n")
        sys.exit(1)

    # ---- fzf binary ----
    if shutil.which("fzf") is None:
        os_name = platform.system()

        print("❌ Missing dependency: fzf\n")

        if os_name == "Linux":
            print("Install fzf using:")
            print("   sudo apt install fzf     # Ubuntu/Debian")
            print("   sudo dnf install fzf     # Fedora")
            print("   sudo pacman -S fzf       # Arch")
        elif os_name == "Darwin":
            print("Install fzf using:")
            print("   brew install fzf")
        elif os_name == "Windows":
            print("Install fzf using:")
            print("   choco install fzf")
            print("or use Winget:")
            print("   winget install fzf")
        else:
            print("Please install fzf manually from:")
            print("   https://github.com/junegunn/fzf")

        sys.exit(1)

    print("✅ All requirements satisfied.\n")


# ==============================
# TERMINAL SETTINGS
# ==============================

TERMINAL_WIDTH = shutil.get_terminal_size().columns
MAX_BUBBLE_WIDTH = int(TERMINAL_WIDTH * 0.55)

DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")


# ==============================
# Unicode Safe Padding
# ==============================


def pad_text(text, width):
    extra = width - wcswidth(text)
    return text + (" " * max(0, extra))


# ==============================
# Pager (Cross Platform)
# ==============================


def open_pager(text):
    """
    Cross-platform pager replacement for less.
    Works on Linux, macOS, Windows.
    """
    pydoc.pager(text)


# ==============================
# Check if Takeout already extracted
# ==============================


def find_existing_takeout():
    groups_path = os.path.join(DOWNLOADS, "Takeout", "Google Chat", "Groups")

    if os.path.exists(groups_path):
        print("✅ Found extracted Takeout folder.")
        return groups_path

    return None


# ==============================
# Find latest takeout-*.zip
# ==============================


def find_latest_takeout_zip():
    zips = [
        f
        for f in os.listdir(DOWNLOADS)
        if f.startswith("takeout-") and f.endswith(".zip")
    ]

    if not zips:
        return None

    zips.sort(key=lambda f: os.path.getmtime(os.path.join(DOWNLOADS, f)), reverse=True)

    latest = os.path.join(DOWNLOADS, zips[0])
    print("✅ Found latest ZIP:", latest)
    return latest


# ==============================
# Extract ZIP into Downloads
# ==============================


def extract_takeout(zip_path):
    print("📦 Extracting ZIP...")

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(DOWNLOADS)

    print("✅ Extraction completed.")


# ==============================
# Load messages safely
# ==============================


def load_messages(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "messages" in data:
        return data["messages"]

    if isinstance(data, list):
        return data

    return []


# ==============================
# Timestamp Cleaner
# ==============================


def clean_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%A, %d %B %Y at %H:%M:%S UTC")
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return date_str


# ==============================
# Detect pinned messages
# ==============================


def is_pinned(msg):
    labels = msg.get("message_labels", [])
    return any(l.get("label_type") == "PINNED" for l in labels)


def count_pinned(messages):
    return sum(1 for m in messages if is_pinned(m))


def extract_pinned(messages):
    return [m for m in messages if is_pinned(m)]


# ==============================
# Auto-detect your email
# ==============================


def detect_my_email(groups_path):
    email_count = {}

    for folder in os.listdir(groups_path):
        msg_file = os.path.join(groups_path, folder, "messages.json")
        if not os.path.exists(msg_file):
            continue

        try:
            with open(msg_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            messages = data.get("messages", [])
            for msg in messages[:200]:
                creator = msg.get("creator", {})
                email = creator.get("email")
                if email:
                    email_count[email] = email_count.get(email, 0) + 1
        except:
            continue

    if not email_count:
        return None

    return max(email_count, key=email_count.get)


# ==============================
# Extract DM participant name
# ==============================


def get_dm_participant(messages, my_email):
    for msg in messages:
        creator = msg.get("creator", {})
        email = creator.get("email")
        name = creator.get("name", "Unknown")

        if email == my_email:
            continue

        if name and name != "Unknown":
            return name

    return "Deleted User"


# ==============================
# Extract Space Title
# ==============================


def get_space_title(folder_path):
    info_file = os.path.join(folder_path, "group_info.json")

    if not os.path.exists(info_file):
        return None

    try:
        with open(info_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("name")
    except:
        return None


# ==============================
# Bubble Drawing
# ==============================


def draw_bubble(text, align="left"):
    wrapped = textwrap.wrap(text, width=MAX_BUBBLE_WIDTH)

    top = "┌" + "─" * (MAX_BUBBLE_WIDTH + 2) + "┐"
    bottom = "└" + "─" * (MAX_BUBBLE_WIDTH + 2) + "┘"

    bubble_lines = [top]

    for line in wrapped:
        bubble_lines.append(f"│ {pad_text(line, MAX_BUBBLE_WIDTH)} │")

    bubble_lines.append(bottom)

    bubble_text = "\n".join(bubble_lines)

    if align == "right":
        padding = TERMINAL_WIDTH - (MAX_BUBBLE_WIDTH + 4)
        bubble_text = "\n".join((" " * padding + l) for l in bubble_text.splitlines())

    return bubble_text


# ==============================
# Format Chat Output
# ==============================


def format_chat(messages, my_email, pinned_only=False):
    output = []

    if pinned_only:
        output.append("📌 Showing ONLY pinned messages\n")
    else:
        output.append(
            "Navigation:\n   /PINNED → search pinned\n   q       → quit pager\n"
        )

    for msg in messages:
        creator = msg.get("creator", {})
        name = creator.get("name", "Unknown")
        email = creator.get("email")

        text = msg.get("text", "").strip()

        if not text:
            if is_pinned(msg):
                text = "[Pinned message (non-text)]"
            else:
                continue

        date = clean_date(msg.get("created_date", ""))

        sender = "You" if email == my_email else name
        align = "right" if email == my_email else "left"

        pin_icon = "[PINNED] " if is_pinned(msg) else ""
        header = f"{pin_icon}{sender} • {date}"

        if align == "right":
            header = header.rjust(TERMINAL_WIDTH)

        output.append("\n" + header)
        output.append(draw_bubble(text, align))

    return "\n".join(output)


# ==============================
# fzf Helper
# ==============================


def run_fzf(options, prompt):
    fzf = subprocess.Popen(
        ["fzf", "--prompt", prompt],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    selected, _ = fzf.communicate("\n".join(options))
    return selected.strip()


# ==============================
# MAIN PROGRAM
# ==============================


def main():
    # Step 1: Find extracted Takeout folder
    groups_path = find_existing_takeout()

    # Step 2: If missing → extract latest ZIP
    if not groups_path:
        zip_path = find_latest_takeout_zip()

        if not zip_path:
            print("❌ No takeout-*.zip found in Downloads.")
            return

        extract_takeout(zip_path)

        groups_path = find_existing_takeout()
        if not groups_path:
            print("❌ Extracted, but Groups folder not found.")
            return

    print("✅ Using Groups folder:", groups_path)

    # Step 3: Detect your email automatically
    my_email = detect_my_email(groups_path)
    if not my_email:
        my_email = input("Enter your email: ").strip()

    print("✅ Your email:", my_email)

    # Step 4: Category selector
    category = run_fzf(["DM", "SPACE", "PINNED ONLY"], "Select Category: ")

    if not category:
        return

    pinned_mode = category.startswith("PINNED")
    show_dm = category.startswith("DM")
    show_space = category.startswith("SPACE")

    # Step 5: Build chat list
    entries = []

    for folder in sorted(os.listdir(groups_path)):
        folder_path = os.path.join(groups_path, folder)
        msg_file = os.path.join(folder_path, "messages.json")

        if not os.path.exists(msg_file):
            continue

        messages = load_messages(msg_file)
        pinned_count = count_pinned(messages)

        if pinned_mode and pinned_count == 0:
            continue

        if (show_dm or pinned_mode) and folder.startswith("DM"):
            name = get_dm_participant(messages, my_email)
            if pinned_count > 0:
                name += f" (📌 {pinned_count})"
            entries.append(f"DM  {name:<45} | {folder}")

        elif (show_space or pinned_mode) and folder.startswith("Space"):
            title = get_space_title(folder_path) or folder
            if pinned_count > 0:
                title += f" (📌 {pinned_count})"
            entries.append(f"SP  {title:<45} | {folder}")

    if not entries:
        print("❌ No chats found.")
        return

    # Step 6: Chat selector
    selected = run_fzf(entries, "Select Chat: ")
    if not selected:
        return

    folder = selected.split("|")[-1].strip()

    # Step 7: Load messages
    msg_file = os.path.join(groups_path, folder, "messages.json")
    messages = load_messages(msg_file)

    if pinned_mode:
        messages = extract_pinned(messages)

    chat_text = format_chat(messages, my_email, pinned_only=pinned_mode)

    # ✅ Cross-platform pager (no less needed)
    open_pager(chat_text)


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    check_dependencies()
    main()
