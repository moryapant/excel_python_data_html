import csv
import os
from datetime import datetime
import logging
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_todays_date():
    return datetime.now().strftime("%d/%m/%y")  # Returns format like "28/08/23"

def process_csv_file(filepath):
    try:
        with open(filepath, 'r') as csvfile:
            content = csvfile.read()
            logging.debug(f"File content:\n{content}")
            
            csvfile.seek(0)  # Reset file pointer to the beginning
            reader = csv.reader(csvfile)
            peak_contacts = None
            portal = None
            date = get_todays_date()  # Use today's date
            for row in reader:
                logging.debug(f"Processing row: {row}")
                if row and len(row) > 1:
                    if row[0].startswith('Peak Contacts'):
                        peak_contacts = row[1]
                    elif row[0] == 'Experience Portal':
                        # Read the next non-empty row for the portal value
                        portal = next((r[0] for r in reader if r and r[0]), None)
            if portal and peak_contacts:
                logging.info(f"Processed file {filepath}: date={date}, portal={portal}, peak_contacts={peak_contacts}")
                return date, portal, peak_contacts
            else:
                logging.warning(f"Missing data in file {filepath}: date={date}, portal={portal}, peak_contacts={peak_contacts}")
    except Exception as e:
        logging.error(f"Error processing file {filepath}: {str(e)}")
    return None

def generate_html_report(date, data, is_output=False):
    title = "Latest Experience Portal Data" if is_output else f"Experience Portal Data - {date}"
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <h1>{title}</h1>
        <table>
            <tr>
                <th>Experience Portal</th>
                <th>Peak Contacts</th>
            </tr>
    '''
    for portal, peak_contacts in data:
        html += f'''
            <tr>
                <td>{portal}</td>
                <td>{peak_contacts}</td>
            </tr>
        '''
    html += '''
        </table>
        <p><a href="index.html">View All Reports</a></p>
    </body>
    </html>
    '''
    return html

def generate_index_html(data_by_date):
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Experience Portal Data Index</title>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <h1>Experience Portal Data Index</h1>
        <ul>
    '''
    for date, filename in sorted(data_by_date.items(), reverse=True):
        html += f'<li><a href="{filename}">{date}</a></li>'
    html += '''
        </ul>
    </body>
    </html>
    '''
    return html

def generate_css():
    return '''
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    h1 {
        color: #2c3e50;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
    }
    th, td {
        padding: 12px 15px;
        text-align: left;
        border-bottom: 1px solid #e0e0e0;
    }
    th {
        background-color: #3498db;
        color: white;
        text-transform: uppercase;
        font-weight: bold;
    }
    tr:nth-child(even) {
        background-color: #f8f8f8;
    }
    tr:hover {
        background-color: #e8f4f8;
    }
    a {
        color: #3498db;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    '''

def main():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    output_directory = os.path.join(current_directory, 'output')
    os.makedirs(output_directory, exist_ok=True)

    data_by_date = defaultdict(list)
    today_date = get_todays_date()

    csv_files = [f for f in os.listdir(current_directory) if f.endswith('.csv')]
    logging.info(f"Found {len(csv_files)} CSV files")

    for filename in csv_files:
        filepath = os.path.join(current_directory, filename)
        result = process_csv_file(filepath)
        if result:
            date, portal, peak_contacts = result
            data_by_date[date].append((portal, peak_contacts))
            logging.info(f"Processed file: {filename}")
        else:
            logging.warning(f"Failed to process file: {filename}")

    if not data_by_date:
        logging.error("No data was extracted from CSV files")
    else:
        report_html = generate_html_report(today_date, data_by_date[today_date])
        report_filename = f'report_{today_date.replace("/", "_")}.html'
        with open(os.path.join(output_directory, report_filename), 'w') as f:
            f.write(report_html)
        logging.info(f"Generated report file: {report_filename}")

        index_html = generate_index_html({today_date: report_filename})
        with open(os.path.join(output_directory, 'index.html'), 'w') as f:
            f.write(index_html)
        logging.info("Generated index.html")

        output_html = generate_html_report(today_date, data_by_date[today_date], is_output=True)
        with open(os.path.join(output_directory, 'output.html'), 'w') as f:
            f.write(output_html)
        logging.info("Generated output.html with today's data")

    css = generate_css()
    with open(os.path.join(output_directory, 'styles.css'), 'w') as f:
        f.write(css)
    logging.info("Generated styles.css")

if __name__ == '__main__':
    main()