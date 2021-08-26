from argparse import ArgumentParser
from io import BytesIO
from uuid import uuid4

from boto3 import resource
from flask import Flask, render_template, request, send_file

from kms import decrypt, encrypt

parser = ArgumentParser("Sample KMS APP")
parser.add_argument("-c", "--cmk", type=str, required=True, help="Key ID")
parser.add_argument(
    "-b",
    "--bucket",
    type=str,
    default="sunghun-sandbox-sample-kms-bucket",
    help="Name of bucket",
)
args = parser.parse_args()

s3 = resource("s3")

filenames = dict()

app = Flask(__name__)


def alert(message):
    return f'<script>alert("{message}");history.back();</script>'


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return alert("'File' not found")

    file_obj = request.files["file"]
    bytes = file_obj.stream.read()

    # encrypt with KMS and upload to S3
    data = encrypt(args.cmk, bytes)
    filename = str(uuid4()).replace("-", "")
    s3.Object(args.bucket, filename).put(Body=data)

    filenames[filename] = file_obj.filename
    return alert(f"Uploaded : {filename}")


@app.route("/download/<filename>")
def download(filename):
    if filename not in filenames:
        return alert("File not found.")
    real_filename = filenames.pop(filename)

    # download from S3 and decrypt with KMS
    encrypted_data = s3.Object(args.bucket, filename).get()["Body"].read()
    data = decrypt(encrypted_data)

    return send_file(
        BytesIO(data),
        mimetype="text/csv",
        download_name=real_filename,
        as_attachment=True,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
