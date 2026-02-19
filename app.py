from flask import Flask, render_template, request, send_file
import pdfplumber
import re
import os
import pandas as pd

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

# Make sure uploads folder exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

def extract_passengers(pdf_path):
    passengers = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")

            for line in lines:
                match = re.search(r'([A-Z ]+)/([A-Z]+)', line)
                if match:
                    last_name = match.group(1).strip()
                    first_name = match.group(2).strip()
                    passengers.append((first_name, last_name))

    return passengers


def generate_data(passengers, domain):
    data = []

    for index, (first, last) in enumerate(passengers, start=1):
        email = f"{first.lower()}{index:03d}@{domain}"
        custom_id = f"ID-{index:04d}"

        data.append({
            "First Name": first,
            "Last Name": last,
            "Generated Email": email,
            "Generated ID": custom_id
        })

    return pd.DataFrame(data)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["pdf"]
        domain = request.form["domain"]

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        passengers = extract_passengers(filepath)
        df = generate_data(passengers, domain)

        output_file = "generated_ids.xlsx"
        df.to_excel(output_file, index=False)

        return send_file(output_file, as_attachment=True)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
