import firebase_admin
from firebase_admin import credentials, storage
import os

# Initialize Firebase
cred = credentials.Certificate("path/to/serviceAccountKey.json")  # Replace with your JSON path
firebase_admin.initialize_app(cred, {
    'storageBucket': 'video-feed-ee737.appspot.com'  # Replace with your bucket name
})

# Upload function
def upload_photo(file_path, upload_name=None):
    bucket = storage.bucket()
    file_name = upload_name if upload_name else os.path.basename(file_path)
    blob = bucket.blob(f'photos/{file_name}')
    
    blob.upload_from_filename(file_path)
    blob.make_public()  # Optional: makes the image viewable without auth

    print(f"✅ Uploaded {file_name}")
    print(f"🌐 Public URL: {blob.public_url}")
    return blob.public_url

# Example usage
if __name__ == "__main__":
    uploaded_url = upload_photo("example.jpg")  # Replace with your image path
