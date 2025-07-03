# flp

A Python script to download audio files from the [Feynman Lectures on Physics](https://www.feynmanlectures.caltech.edu/) in `m4a` or `ogg` format.

## Requirements

- Python 3+
- `requests` library

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic usage

Download all lectures to the default `out` directory:

```bash
python download.py
```

### Options

- `-o, --output-dir`: Specify output directory (default: `out`)
- `-f, --format`: Choose audio format — `m4a` or `ogg` (default: `m4a`)
- `--no-date`: Don't include lecture date in filenames
  - **Note:** Dates are included by default for easier organization (sorting).
- `--overwrite`: Overwrite existing files
- `-v, --verbose`: Enable verbose output
