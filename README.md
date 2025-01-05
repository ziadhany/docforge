
# **Document Processing: Turning Data Into Insights**

## **Requirements**

 - [x] Create a Django project with a REST API using Django Rest
       Framework (DRF).
 - [x] The API should include the following endpoints:
   - **`POST /api/upload/`**: Accepts image and PDF files in Base64 format and saves them to the server.
   - **`GET /api/images/`**: Returns a list of all uploaded images.
   - **`GET /api/pdfs/`**: Returns a list of all uploaded PDFs.
   - **`GET /api/images/{id}/`**: Retrieves details of a specific image, such as file location, width, height, and number of channels.
   - **`GET /api/pdfs/{id}/`**: Retrieves details of a specific PDF, including file location, number of pages, page width, and height.
   - **`DELETE /api/images/{id}/`**: Deletes a specific image.
   - **`DELETE /api/pdfs/{id}/`**: Deletes a specific PDF.
   - **`POST /api/rotate/`**: Accepts an image ID and a rotation angle, rotates the image, and returns the rotated version.
   - **`POST /api/convert-pdf-to-image/`**: Accepts a PDF ID, converts the PDF into images (one per page), and returns them.
 - [x] Develop the required models, serializers, views, and URLs to implement the above functionality.
 - [x] Save the image and PDF files to a server directory and store the file paths in the database.
 - [x]  Ensure proper error handling and validation for all API endpoints.
 - [x] Use Git for version control, making regular commits with clear and meaningful messages.
 - [x] Dockerize the Django project to simplify deployment and testing.

---

## **Extra Credit**

Enhance the project by implementing some or all of the following:
 - [x]  Add automated tests using **pytest** to validate functionality.
 - [ ] Deploy the application on a free hosting platform, such as **PythonAnywhere**.
 - [ ] Provide a **Postman collection** with example requests for all API endpoints.

## **Getting Started**

### **Run With Docker**

Ensure Docker is installed on your system. Then, execute the following commands:

```bash
git clone https://github.com/ziadhany/docforge.git && cd docforge
docker compose build
docker compose up
```

## **Local Development Installation**

For Debian-based systems, follow these steps:
```bash
sudo apt-get install python3-venv python3-dev postgresql libpq-dev build-essential
git clone https://github.com/ziadhany/docforge.git && cd docforge 
python3 -m venv venv 
source venv/bin/activate 
pip install -r requirements.txt 
```
### Set Up Environment Variables

Create a `.env` file in the root of the project to store environment variables. Use the following content as an example:
```bash
DOCFORGE_DB_ENGINE="django.db.backends.postgresql"  
DOCFORGE_DB_HOST="localhost"  
DOCFORGE_DB_NAME="docforge"  
DOCFORGE_DB_USER="docforge"  
DOCFORGE_DB_PASSWORD="docforge"  
DOCFORGE_DB_PORT="5432"
```

```bash
make test 
make run
```

Once complete, the **DocForge** app and API will be available at **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.


