# ----------
# Project TIM – Phase 1+2 Docker image
# ----------
FROM python:3.11-slim

# Create a non‑root user for safety
RUN useradd -m timuser
WORKDIR /home/timuser/app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code into the image
COPY . .

# Make the launch script executable and set ownership
RUN chmod +x run.sh && chown -R timuser:timuser /home/timuser/app

# Expose both Governor (8080) and Draftsman (8081) ports
EXPOSE 8080 8081

# Switch to the non‑root user
USER timuser

# Default command starts both services side‑by‑side
CMD ["./run.sh"]