
FROM python:3.11

# Set the working directory in the container
WORKDIR /usr/src/app

# Install necessary libraries for Qt and X11
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libx11-xcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    xkb-data \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    libxcb1 \
    libqt5widgets5 \
    libqt5gui5 \
    libqt5core5a \
    xauth \
    xvfb


# Create .Xauthority file
RUN touch /root/.Xauthority

# Set environment variables for Qt and X11
ENV DISPLAY=:0

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run Xvfb, then your application
CMD Xvfb :0 -screen 0 1024x768x16 & \
    sleep 5 && \
    xauth add :0 . $(mcookie) && \
    echo "Xvfb started" && \
    python ./application.py