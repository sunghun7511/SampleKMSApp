from argparse import ArgumentParser
from io import BytesIO
from uuid import uuid4

from boto3 import resource
from flask import Flask, render_template, request, send_file

from encryption import encrypt_aes, decrypt_aes
from kms import generate_key, decrypt_key

parser = ArgumentParser("Sample KMS APP")
parser.add_argument("-c", "--cmk", type=str, required=True, help="Key ID")
parser.add_argument("-b", "--bucket", type=str, default="sunghun-sandbox-sample-kms-bucket", help="Name of bucket")
args = parser.parse_args()

s3 = resource("s3")

filenames = dict()

app = Flask(__name__)


def alert(message):
    return f"<script>alert(\"{message}\");history.back();</script>"


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file_obj = request.files['file']
    bytes = file_obj.stream.read()

    encrypted_key, key = generate_key(args.cmk)
    data = encrypt_aes(key, bytes)

    filename = str(uuid4()).replace("-", "")
    data = len(encrypted_key).to_bytes(2, "little") + encrypted_key + data
    s3.Object(args.bucket, filename).put(Body=data)

    filenames[filename] = file_obj.filename

    return alert(f"Uploaded : {filename}")


@app.route("/download/<filename>")
def download(filename):
    if filename not in filenames:
        return alert("File not found.")
    real_filename = filenames.pop(filename)

    encrypted_data = s3.Object(args.bucket, filename).get()["Body"].read()
    key_size = int.from_bytes(encrypted_data[:2], "little")
    key = decrypt_key(encrypted_data[2:2+key_size])
    data = decrypt_aes(key, encrypted_data[2+key_size:])

    return send_file(
        BytesIO(data),
        mimetype='text/csv',
        attachment_filename=real_filename,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
