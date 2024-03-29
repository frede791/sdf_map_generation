FROM px4io/px4-dev-simulation-jammy as build-stage

ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir /work

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    zip \
    python3

# Clone the repo and build libextern_draco.so
RUN cd /work && git clone https://github.com/ux3d/blender_extern_draco.git --recursive
RUN mkdir -p /work/blender_extern_draco/build
RUN cd /work/blender_extern_draco/build && cmake .. && make -j `nproc`

# Modify blosm code. Required as blosm's replaceMaterial doesn't per default work with API.
COPY blosm.zip /work/blosm.zip
COPY blosm_replacematerial_execute.py /work/blosm_replacematerial_execute.py
RUN unzip /work/blosm.zip -d /work
RUN python3 /work/blosm_replacematerial_execute.py
RUN zip -r -FS blosm.zip /work/blosm
RUN rm -rf /work/blosm


FROM ubuntu:22.04 as run-stage

RUN apt-get update && apt-get install -y \
    python3.10 \
    pip \
    build-essential \
    git \
    subversion \
    cmake \
    libx11-dev \
    libxxf86vm-dev \
    libxcursor-dev \
    libxi-dev \
    libxrandr-dev \
    libxinerama-dev \
    libegl-dev \
    libwayland-dev \
    wayland-protocols \
    libxkbcommon-dev \
    libdbus-1-dev \
    linux-libc-dev \
    libsm6 \
    libxext6 \
    libxrender-dev


RUN pip install bpy==4.0.0 folium

RUN mkdir -p /work/map_generator
RUN mkdir /work/blender_maps
RUN mkdir /work/output

ENV DEBIAN_FRONTEND=noninteractive


RUN mkdir -p /work/map_generator/4.0/python/lib/python3.10/site-packages
COPY --from=build-stage /work/blender_extern_draco/build/libextern_draco.so /work/map_generator/4.0/python/lib/python3.10/site-packages/
COPY --from=build-stage /work/blosm.zip /work/map_generator/blosm.zip
COPY map_generation.py /work/map_generator/map_generation.py
COPY world_template.sdf /work/map_generator/world_template.sdf


WORKDIR /work/map_generator/
