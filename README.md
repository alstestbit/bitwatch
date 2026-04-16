# bitwatch

A lightweight CLI tool to monitor file and directory changes with configurable webhook alerts.

---

## Installation

```bash
pip install bitwatch
```

Or install from source:

```bash
git clone https://github.com/youruser/bitwatch.git && cd bitwatch && pip install .
```

---

## Usage

Watch a directory and send alerts to a webhook when changes are detected:

```bash
bitwatch watch ./my-project --webhook https://hooks.example.com/notify
```

Watch a single file with a custom polling interval:

```bash
bitwatch watch ./config.yaml --interval 5 --webhook https://hooks.example.com/notify
```

**Options:**

| Flag | Description | Default |
|------|-------------|---------|
| `--webhook` | Webhook URL to POST change events | None |
| `--interval` | Polling interval in seconds | `10` |
| `--recursive` | Watch directories recursively | `False` |
| `--filter` | File pattern to watch (e.g. `*.log`) | All files |

Example webhook payload:

```json
{
  "event": "modified",
  "path": "./my-project/app.py",
  "timestamp": "2024-06-01T12:34:56Z"
}
```

---

## Requirements

- Python 3.8+
- `watchdog`
- `requests`

---

## License

This project is licensed under the [MIT License](LICENSE).