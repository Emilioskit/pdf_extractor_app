from flask import Flask, request, send_file, render_template_string, after_this_request
import shutil
import pdfplumber
import pandas as pd
import os
import tempfile
from werkzeug.utils import secure_filename
import webbrowser
import threading
import signal
import sys

app = Flask(__name__)

# Simple HTML template with shutdown button
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PDF Task Extractor</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .container { text-align: center; }
        input[type="file"] { margin: 20px; padding: 10px; }
        button { background: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 5px; }
        button:hover { background: #0056b3; }
        .shutdown-btn { background: #dc3545; }
        .shutdown-btn:hover { background: #c82333; }
        .message { margin: 20px 0; padding: 10px; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>PDF Task Extractor</h1>
        <p>Upload a PDF file and download the structured Excel file</p>
        
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" accept=".pdf" required>
            <br>
            <button type="submit">Process PDF → Download Excel</button>
        </form>
        
        <div style="margin-top: 30px; border-top: 1px solid #ccc; padding-top: 20px;">
            <form method="POST" action="/shutdown">
                <button type="submit" class="shutdown-btn">Shutdown Application</button>
            </form>
        </div>
        
        {% if message %}
            <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

def shutdown_server():
    """Gracefully shutdown the Flask server"""
    print("Shutting down server...")
    os._exit(0)

def signal_handler(sig, frame):
    """Handle Ctrl+C signal"""
    print('\nReceived interrupt signal. Shutting down...')
    shutdown_server()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Shutdown endpoint"""
    threading.Timer(1.0, shutdown_server).start()
    return '<h1>Server shutting down...</h1><p>You can close this window.</p>'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template_string(HTML_TEMPLATE)

    try:
        file = request.files.get('file')
        if not file or file.filename == '' or not file.filename.lower().endswith('.pdf'):
            return render_template_string(HTML_TEMPLATE, message="Please upload a valid PDF file", message_type="error")

        temp_dir = tempfile.mkdtemp()
        print(f"Temporary directory created at: {temp_dir}")

        pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(pdf_path)

        @after_this_request
        def cleanup(response):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Error cleaning up temp directory: {e}")
            return response


        # === Your PDF logic starts here ===
        df = pd.DataFrame()
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    page_df = pd.DataFrame(table)
                    df = pd.concat([df, page_df], ignore_index=True)

        mask = df.isin(['ITEM'])
        result = mask.any(axis=1)

        if result.any():
            row_idx = result.idxmax()
            col_idx = mask.loc[row_idx].idxmax()
            df_cleaned = df.iloc[row_idx + 1:]
            df_cleaned = df_cleaned.iloc[:, col_idx:col_idx + 4]
        else:
            return render_template_string(HTML_TEMPLATE, message="Header 'ITEM' not found in the PDF.", message_type="error")

        c = 1
        main_task_flag = []
        for _, row in df_cleaned.iterrows():
            if str(c) == str(row[1]):
                main_task_flag.append(True)
                c += 1
            else:
                main_task_flag.append(False)

        df_cleaned["Flag"] = main_task_flag
        df_cleaned = df_cleaned.reset_index(drop=True)

        task_counter = 1
        subtask_counter = 1
        current_main_task = ""

        ot_list = []
        task_number_list = []
        task_name_list = []
        subtask_number_list = []
        subtask_name_list = []
        start_date_list = []
        end_date_list = []

        for index, row in df_cleaned.iterrows():
            task_number = row.iloc[0]
            task_description = row.iloc[1]
            start_date = row.iloc[2]
            end_date = row.iloc[3]
            is_main_task = row.iloc[4]

            if index + 1 < len(df_cleaned):
                next_is_main_task = df_cleaned.iloc[index + 1, 4]
            else:
                next_is_main_task = True

            if is_main_task and next_is_main_task:
                current_main_task = task_description
                ot_list.append("")
                task_number_list.append(task_counter)
                task_name_list.append(current_main_task)
                subtask_number_list.append("")
                subtask_name_list.append("")
                start_date_list.append(start_date)
                end_date_list.append(end_date)
                task_counter += 1

            elif is_main_task and not next_is_main_task:
                current_main_task = task_description
                subtask_counter = 1

            elif not is_main_task and not next_is_main_task:
                ot_list.append("")
                task_number_list.append(task_counter)
                task_name_list.append(current_main_task)
                subtask_number_list.append(f"{task_counter}.{subtask_counter}")
                subtask_name_list.append(task_description)
                start_date_list.append(start_date)
                end_date_list.append(end_date)
                subtask_counter += 1

            else:
                ot_list.append("")
                task_number_list.append(task_counter)
                task_name_list.append(current_main_task)
                subtask_number_list.append(f"{task_counter}.{subtask_counter}")
                subtask_name_list.append(task_description)
                start_date_list.append(start_date)
                end_date_list.append(end_date)
                task_counter += 1

        output_df = pd.DataFrame({
            "Numero de OT": ot_list,
            "Rubro Principal": task_number_list,
            "Detalle Rubro": task_name_list,
            "Numero de Actividad": subtask_number_list,
            "Detalle de Rubro": subtask_name_list,
            "Fecha inicio": start_date_list,
            "Fecha fin": end_date_list
        })

        excel_path = os.path.join(temp_dir, 'structured_tasks.xlsx')
        output_df.to_excel(excel_path, index=False)

        return send_file(excel_path, as_attachment=True, download_name='structured_tasks.xlsx')

    except Exception as e:
        return render_template_string(HTML_TEMPLATE, message=f"Error: {str(e)}", message_type="error")


def open_browser():
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Handle SIGTERM on Unix systems
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting PDF Task Extractor...")
    print("Press Ctrl+C to quit or use the Shutdown button in the web interface")
    
    threading.Timer(1, open_browser).start()
    
    try:
        app.run(debug=False, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        print("Server stopped.")