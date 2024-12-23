# Use Alpine-based Python image
FROM python:3.12-slim

WORKDIR /app

COPY docker/install_package_script.sh /app/docker/install_package_script.sh
RUN chmod +x /app/docker/install_package_script.sh

RUN /app/docker/install_package_script.sh

# Copy the source code into the container.
COPY ./requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

RUN chmod +x /app/docker/prepare_script.sh /app/docker/launch_script.sh

RUN /app/docker/prepare_script.sh

# Command to run the application with automatic reload
CMD ["/app/docker/launch_script.sh"]