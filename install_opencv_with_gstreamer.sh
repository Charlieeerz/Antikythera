#!/bin/bash

set -e  # Arrête le script en cas d'erreur

echo "Mise à jour des paquets..."
sudo apt update && sudo apt upgrade -y

echo "Installation des dépendances de base..."
sudo apt install -y build-essential cmake git pkg-config \
    libgtk2.0-dev libgtk-3-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libxvidcore-dev libx264-dev \
    libjpeg-dev libpng-dev libtiff-dev \
    gfortran openexr libatlas-base-dev \
    python3-dev python3-numpy python3-pip \
    libgstreamer1.0-dev gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly

echo "Téléchargement des sources d'OpenCV..."
mkdir -p ~/opencv_build && cd ~/opencv_build
if [ ! -d "opencv" ]; then
    git clone https://github.com/opencv/opencv.git
else
    echo "OpenCV déjà téléchargé."
fi

if [ ! -d "opencv_contrib" ]; then
    git clone https://github.com/opencv/opencv_contrib.git
else
    echo "OpenCV Contrib déjà téléchargé."
fi

cd opencv
echo "Mise à jour des sources d'OpenCV..."
git pull
cd ../opencv_contrib
git pull

echo "Configuration de la compilation avec CMake..."
cd ~/opencv_build/opencv
mkdir -p build && cd build

cmake -D CMAKE_BUILD_TYPE=Release \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D OPENCV_EXTRA_MODULES_PATH=~/opencv_build/opencv_contrib/modules \
      -D WITH_GSTREAMER=ON \
      -D WITH_FFMPEG=ON \
      -D BUILD_EXAMPLES=OFF \
      ..

echo "Compilation d'OpenCV... (cela peut prendre un certain temps)"
make -j$(nproc)

echo "Installation d'OpenCV..."
sudo make install
sudo ldconfig

echo "Vérification de la version installée d'OpenCV..."
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)"
echo "Installation terminée !"
