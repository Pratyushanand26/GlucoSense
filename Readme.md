# ⚙️ Setup Instructions only for backend

Follow these steps to run **GlucoSense** locally.  
Everything below works on **Windows, macOS, and Linux**.  

---

### 🧩 1. Clone the Repository
```bash
git clone https://github.com/pratyushanand26/GlucoSense.git
```
```bash
cd GlucoSense
```
Windows
```bash
python -m venv venv
venv\Scripts\activate
```
macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```
```bash
pip install -r requirements.txt
```
Configure Environment Variables

Create a .env file inside the models/ or root folder (based on your structure).
Use the following template
```bash
MONGO_CONNECTION_STRING=mongodb://localhost:27017/glucosense
GEMINI_API_KEY=your_gemini_api_key_here
```

Run the Main FastAPI Server

Once your .env is configured and MongoDB is running
```bash
python -m server.main
```
### Now your backend is running on port 8000 can access
```bash
http://localhost:8000/docs
```
now you see your all API end points
