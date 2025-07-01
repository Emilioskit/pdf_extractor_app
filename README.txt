# PDF Task Extractor

A desktop application that extracts task tables from PDF files and converts them into structured Excel spreadsheets.

## Features

- **PDF Table Extraction**: Automatically detects and extracts tables from PDF files
- **Task Structuring**: Organizes tasks into main tasks and subtasks with proper numbering
- **Excel Output**: Saves results to Excel format with proper column headers
- **User-Friendly GUI**: Simple interface for selecting files and monitoring progress
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Quick Start (Using Pre-built Executables)

### Windows
1. Download `PDFTaskExtractor.exe`
2. Double-click to run (no installation required)
3. Select your PDF file and output location
4. Click "Process PDF"

### macOS
1. Download `PDFTaskExtractor.app`
2. Right-click and select "Open" (first time only, due to security)
3. Select your PDF file and output location
4. Click "Process PDF"

## Building from Source

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Download the source files**:
   - `pdf_task_extractor.py` (main application)
   - `requirements.txt` (dependencies)
   - `build_executable.py` (build script)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application directly**:
   ```bash
   python pdf_task_extractor.py
   ```

### Building Executables

To create standalone executables (.exe for Windows, .app for macOS):

1. **Ensure all source files are in the same directory**
2. **Run the build script**:
   ```bash
   python build_executable.py
   ```
3. **Find your executable in the `dist/` folder**

### Manual PyInstaller Build (Alternative)

If the build script doesn't work, you can build manually:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name PDFTaskExtractor pdf_task_extractor.py

# Executable will be in dist/ folder
```

## How It Works

The application processes PDF files in the following steps:

1. **PDF Parsing**: Uses `pdfplumber` to extract tables from each page
2. **Data Processing**: Identifies main tasks (rows without end dates) and subtasks
3. **Structuring**: Creates hierarchical task numbering (1, 1.1, 1.2, 2, 2.1, etc.)
4. **Excel Export**: Saves structured data with proper column headers

### Expected PDF Format

The application expects PDF tables with at least 3 columns:
- **Column 1**: Task/Subtask Description
- **Column 2**: Start Date
- **Column 3**: End Date (empty for main tasks)

### Output Format

The generated Excel file contains:
- **Numero de OT**: Work order number (empty)
- **Rubro Principal**: Main task number
- **Detalle Rubro**: Main task description
- **Numero de Actividad**: Subtask number (e.g., 1.1, 1.2)
- **Detalle de Rubro**: Subtask description
- **Fecha inicio**: Start date
- **Fecha fin**: End date

## Troubleshooting

### Common Issues

1. **"No tables found in PDF"**
   - Ensure your PDF contains properly formatted tables
   - Tables should have clear borders or consistent spacing
   - Try different PDF files to verify the issue

2. **Application won't start on macOS**
   - Right-click the .app file and select "Open"
   - Go to System Preferences > Security & Privacy and allow the app

3. **Build fails with PyInstaller**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Try updating PyInstaller: `pip install --upgrade pyinstaller`
   - Check that you have the latest Python version

### Getting Help

If you encounter issues:
1. Check that your PDF format matches the expected structure
2. Verify all dependencies are installed correctly
3. Try running the script directly with `python pdf_task_extractor.py`

## Technical Details

### Dependencies
- **pdfplumber**: PDF table extraction
- **pandas**: Data manipulation and processing
- **openpyxl**: Excel file creation
- **tkinter**: GUI interface (included with Python)
- **pyinstaller**: Executable creation (build-time only)

### File Structure
```
pdf-task-extractor/
├── pdf_task_extractor.py    # Main application
├── requirements.txt         # Python dependencies
├── build_executable.py      # Build script
├── README.md               # This file
└── dist/                   # Built executables (after building)
    ├── PDFTaskExtractor.exe    # Windows executable
    └── PDFTaskExtractor.app    # macOS application
```

## License

This project is provided as-is for educational and personal use.