# Photo OCR Extractor - Simple Explanation

This is a **Windows desktop application** that extracts text from photos using OCR (Optical Character Recognition). Here's everything it does in simple terms:

---

## **What It Does**
- Lets you select up to **100 photos** (PNG, JPG, JPEG, BMP, TIFF, WebP)
- Reads any text found in those photos
- Shows the extracted text in a window
- Lets you copy or save the text

---

## **How It Works**

### **1. User Interface**
- A window with:
  - **"Select Photos" button** - pick your images
  - **Dark/Light theme toggle** - change colors
  - **Progress bar** - shows how many photos are done
  - **Status label** - tells you what's happening
  - **Text display area** - shows extracted text
  - **"Copy" and "Save" buttons** - export the text

### **2. The OCR Process**
1. You click "Select Photos & Extract Text"
2. It launches a **separate process** (so the window doesn't freeze)
3. The OCR engine loads (takes a few seconds first time)
4. Each photo is processed one by one
5. Text is displayed as it's extracted

### **3. What It Uses**
- **PaddleOCR** - the actual text recognition engine
- **Tkinter** - creates the window and buttons
- **Multiprocessing** - runs OCR in the background

---

## **Important Technical Details**

### **Memory/Performance**
- Uses **separate processes** (not just threads) - this prevents the GUI from freezing
- Limits to **100 photos** to avoid memory issues
- Processes photos one at a time

### **Error Handling**
- If a photo can't be read, it shows `[Error reading filename: error message]`
- Won't crash if a single image fails

### **Theme System**
- Light theme: white background, black text
- Dark theme: dark gray background, white text
- Changes colors of the main window, text box, and status bar

### **File Output**
- Saves as `.txt` file with UTF-8 encoding
- Each photo's text is separated by `--- filename ---` headers

---

## **First-Time Use Notes**
- **First run is slow** - it needs to download/load the OCR model
- Status bar will say "Loading OCR model..." during this time
- After the model loads, processing is faster

---

## **Potential Issues**
- **Only English** - the OCR is set to English only
- **No progress if you close the window** - the background process might keep running
- **Photo quality matters** - blurry or small text won't read well

---

## **For Developers**
- It's a single Python file
- Uses `multiprocessing` with `freeze_support()` for Windows compatibility
- The OCR runs in a separate function `ocr_worker_process()`
- Uses a queue to communicate between processes

---

## **User Workflow**
1. Run the program
2. Click "Select Photos & Extract Text"
3. Choose your images
4. Wait for processing (watch progress bar)
5. View/scroll through extracted text
6. Click "Copy" to copy all text or "Save" to create a .txt file

---

That's it! It's a simple tool that turns text in images into editable text you can copy or save.
