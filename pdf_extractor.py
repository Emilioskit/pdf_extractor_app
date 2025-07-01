from flask import Flask, request, send_file, render_template_string
import pdfplumber
import pandas as pd
import os
import tempfile
from werkzeug.utils import secure_filename
import webbrowser
import threading

app = Flask(__name__)

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PDF Task Extractor</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        .container { text-align: center; }
        input[type="file"] { margin: 20px; padding: 10px; }
        button { background: #007bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
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
        
        {% if message %}
            <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template_string(HTML_TEMPLATE)
    
    # Handle file upload and processing
    try:
        if 'file' not in request.files:
            return render_template_string(HTML_TEMPLATE, message="No file selected", message_type="error")
        
        file = request.files['file']
        if file.filename == '':
            return render_template_string(HTML_TEMPLATE, message="No file selected", message_type="error")
        
        if not file.filename.lower().endswith('.pdf'):
            return render_template_string(HTML_TEMPLATE, message="Please upload a PDF file", message_type="error")
        
        # Save uploaded file
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(pdf_path)
        
        # Process PDF - Extract tables
        df = pd.DataFrame()
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    page_df = pd.DataFrame(table)
                    df = pd.concat([df, page_df], ignore_index=True)
        
        if df.empty:
            return render_template_string(HTML_TEMPLATE, message="No tables found in PDF", message_type="error")
        
        # Process data - Structure tasks
        task_counter = 0
        subtask_counter = 0
        current_main_task = ""
        
        ot_list = []
        task_number_list = []
        task_name_list = []
        subtask_number_list = []
        subtask_name_list = []
        start_date_list = []
        end_date_list = []
        
        for index, row in df.iterrows():
            task_description = row.iloc[0] if len(row) > 0 else ""
            start_date = row.iloc[1] if len(row) > 1 else ""
            end_date = row.iloc[2] if len(row) > 2 else ""
            
            is_main_task = pd.isna(end_date) or end_date == ""
            
            if is_main_task:
                task_counter += 1
                subtask_counter = 0
                current_main_task = task_description
            else:
                ot_list.append("")
                subtask_counter += 1
                task_number_list.append(task_counter)
                task_name_list.append(current_main_task)
                subtask_number_list.append(f"{task_counter}.{subtask_counter}")
                subtask_name_list.append(task_description)
                start_date_list.append(start_date)
                end_date_list.append(end_date)
        
        # Create output DataFrame
        output_df = pd.DataFrame({
            "Numero de OT": ot_list,
            "Rubro Principal": task_number_list,
            "Detalle Rubro": task_name_list,
            "Numero de Actividad": subtask_number_list,
            "Detalle de Rubro": subtask_name_list,
            "Fecha inicio": start_date_list,
            "Fecha fin": end_date_list
        })
        
        # Save to Excel
        excel_path = os.path.join(temp_dir, 'structured_tasks.xlsx')
        output_df.to_excel(excel_path, index=False)
        
        # Return Excel file for download
        return send_file(excel_path, as_attachment=True, download_name='structured_tasks.xlsx')
        
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, message=f"Error: {str(e)}", message_type="error")

def open_browser():
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    # Open browser automatically
    threading.Timer(1, open_browser).start()
    
    # Run Flask app
    app.run(debug=False, host='127.0.0.1', port=5000)