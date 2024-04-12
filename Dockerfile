# Stage 1: Build stage
FROM python:3.10 AS builder
# Install Tesseract OCR, Poppler, and apt-utils
RUN apt-get update && \
    apt-get install -y tesseract-ocr poppler-utils apt-utils
# Set the working directory in the builder stage
WORKDIR /usr/share/tesseract-ocr/5/tessdata/
# Copy Tesseract OCR language data files into the builder stage
COPY . .
# Stage 2: Final stage
FROM python:3.10
# Install Poppler
RUN apt-get update && \
    apt-get install -y poppler-utils
# Set the working directory in the container
WORKDIR /question-answerBack
# Copy the current directory contents into the container at /question-answerBack
COPY . .
# Copy Tesseract OCR from the builder stage
COPY --from=builder /usr/bin/tesseract /usr/bin/tesseract
# Install Tesseract and any needed Python dependencies
RUN apt-get update && apt-get install -y tesseract-ocr && \
    pip install flask flask-cors pdfminer.six transformers==4.23.0 \
    docquery==0.0.7 torch tensorflow pydantic==1.9.0 pytesseract
# Set TESSDATA_PREFIX environment variable
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata/
# Expose port 7000 for Flask app
EXPOSE 7000
# Run app.py when the container launches
CMD python ./app.py