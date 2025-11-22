FROM public.ecr.aws/lambda/python:3.11

# Set the working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt 

# Copy the entire app structure
COPY server/ ./server/
COPY Agents/ ./Agents/
COPY app.py .
COPY lambda_handler.py .

# Set the CMD to your handler
CMD ["lambda_handler.lambda_handler"]
