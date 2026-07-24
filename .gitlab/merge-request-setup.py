import os
import re
import sys
import json
import urllib.request
import urllib.parse

# Configuration from Environment Variables
GITLAB_API_URL = os.environ.get("CI_API_V4_URL")
PROJECT_ID = os.environ.get("CI_PROJECT_ID")
MERGE_REQUEST_IID = os.environ.get("CI_MERGE_REQUEST_IID")
MERGE_REQUEST_TITLE = os.environ.get("CI_MERGE_REQUEST_TITLE")
MERGE_REQUEST_AUTHOR_ID = os.environ.get("CI_MERGE_REQUEST_AUTHOR_ID")
ACCESS_TOKEN = os.environ.get("SETTINGS__GITLAB_ACCESS_TOKEN")

# Conventional Commit Types and their corresponding Labels
TYPE_TO_LABEL = {
    "feat": "feature",
    "fix": "fix",
    "chore": "chore",
    "docs": "documentation",
    "style": "style",
    "refactor": "refactor",
    "perf": "performance",
    "test": "testing",
    "build": "build",
    "ci": "continuous-integration",
    "revert": "revert",
}

def make_request(method, endpoint, data=None):
    url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_IID}/{endpoint}"
    if endpoint == "": # Base Merge Request endpoint
        url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_IID}"

    headers = {
        "PRIVATE-TOKEN": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Error making request to {url}: {e}")
        return None

def lint_title(title):
    print(f"Linting Merge Request title: {title}")

    # Conventional Commit Regex: type(scope)!: subject
    # Only scope is allowed to have uppercasing.
    pattern = r"^([a-z-]+)(\([^)]+\))?(!?): (.+)$"
    match = re.match(pattern, title)

    if not match:
        print("Error: Merge Request title does not follow conventional commit format 'type(scope): subject'")
        print("Note: Ensure there is a space after the colon.")
        sys.exit(1)

    commit_type = match.group(1)
    is_breaking = match.group(3) == "!"
    subject = match.group(4)

    # Validate Type
    if commit_type not in TYPE_TO_LABEL and commit_type not in TYPE_TO_LABEL.values():
        print(f"Error: Unknown commit type '{commit_type}'")
        sys.exit(1)

    # Validate Uppercasing: Only scope allowed to have uppercasing.
    # This means type and subject must be lowercase.
    if commit_type != commit_type.lower():
        print(f"Error: Commit type '{commit_type}' must be lowercase")
        sys.exit(1)

    if subject != subject.lower():
        print(f"Error: Commit subject '{subject}' must be lowercase")
        sys.exit(1)

    print("Title linting passed!")
    return commit_type, is_breaking

def auto_assign():
    if not MERGE_REQUEST_AUTHOR_ID:
        print("Skipping auto-assignment: CI_MERGE_REQUEST_AUTHOR_ID not found.")
        return

    print(f"Auto-assigning Merge Request to author (ID: {MERGE_REQUEST_AUTHOR_ID})...")
    make_request("PUT", "", {"assignee_ids": [MERGE_REQUEST_AUTHOR_ID]})

def get_labels_from_files(files):
    labels = set()
    for file in files:
        if not file:
            continue

        if file.startswith("ui/"):
            labels.add("frontend")
        elif file.startswith("app/") or file == "start.py":
            labels.add("backend")

        if file.endswith(".md") or file.startswith("docs/"):
            labels.add("documentation")

        # Testing
        if any(p in file for p in ["/__tests__/", "cypress/"]) or \
           file.endswith(".test.js") or file.endswith(".spec.js") or \
           file.startswith("tests/") or file.startswith("test_") or \
           file.endswith("_test.py"):
            labels.add("testing")

        # CI
        if file == ".gitlab-ci.yml" or file.startswith(".gitlab/"):
            labels.add("continuous-integration")

        # Build
        if file in ["package.json", "bun.lock", "pyproject.toml", "uv.lock", "Cornerstone.spec", "vite.config.js", "vitest.config.js"] or \
           file.startswith("commands/"):
            labels.add("build")

        # Style
        if file in ["biome.json", ".pre-commit-config.yaml"]:
            labels.add("style")

    return list(labels)

def auto_label(commit_type, is_breaking):
    # Fetch existing MR to see current labels
    print("Fetching existing Merge Request labels...")
    mr_details = make_request("GET", "")
    if not mr_details:
        print("Error: Could not fetch Merge Request details. Skipping auto-labeling.")
        return

    current_labels = mr_details.get("labels", [])
    print(f"Current labels: {', '.join(current_labels) if current_labels else 'None'}")

    labels_to_add = []

    # 1. Labels from Title
    label = TYPE_TO_LABEL.get(commit_type)
    if not label and commit_type in TYPE_TO_LABEL.values():
        label = commit_type

    if label and label not in current_labels:
        labels_to_add.append(label)

    if is_breaking and "breaking-change" not in current_labels:
        labels_to_add.append("breaking-change")

    # 2. Labels from Files
    print("Fetching changed files for additional labeling...")
    mr_changes = make_request("GET", "changes")
    if mr_changes:
        changed_files = [c.get("new_path") for c in mr_changes.get("changes", [])]
        file_labels = get_labels_from_files(changed_files)
        for fl in file_labels:
            if fl not in current_labels and fl not in labels_to_add:
                labels_to_add.append(fl)
    else:
        print("Warning: Could not fetch changed files.")

    if labels_to_add:
        print(f"Adding labels: {', '.join(labels_to_add)}")
        # To just add labels, we use 'add_labels' parameter in GitLab 12.8+
        make_request("PUT", "", {"add_labels": ",".join(labels_to_add)})
    else:
        print("No new labels to add.")

if __name__ == "__main__":
    if not ACCESS_TOKEN:
        print("Error: SETTINGS__GITLAB_ACCESS_TOKEN not set.")
        print("Tip: If the variable is set in GitLab, ensure the 'Protected' flag is UNCHECKED,")
        print("otherwise it won't be available to Merge Request pipelines on feature branches.")
        sys.exit(1)

    if not MERGE_REQUEST_IID:
        print("This script must be run in a GitLab CI Merge Request pipeline.")
        sys.exit(0)

    # 1. Lint Title
    ctype, breaking = lint_title(MERGE_REQUEST_TITLE)

    # 2. Auto Assign (Only on Merge Request open - we check for a specific flag or just always do it if it's the first time)
    # The requirement says "Only on merge open".
    # We can detect this via CI_PIPELINE_SOURCE or CI_MERGE_REQUEST_EVENT_TYPE if available.
    # But usually, it's safer to just do it if not assigned yet.
    event_type = os.environ.get("CI_MERGE_REQUEST_EVENT_TYPE")
    if event_type == "opened":
        auto_assign()
    else:
        print(f"Skipping auto-assignment (event type: {event_type})")

    # 3. Auto Label
    auto_label(ctype, breaking)
