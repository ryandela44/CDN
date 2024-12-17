# CDN Project with Reverse Proxy and HTTP/2

This project implements a Content Delivery Network (CDN) architecture using `aiohttp` servers for origin and replica nodes, a controller for load balancing and caching logic, and Nginx as a reverse proxy to provide HTTPS and HTTP/2 support throughout the entire client journey.

## Overview

- **Origin Server**: Hosts all original video files.
- **Replica Servers**: Cache videos preemptively pushed from the origin. Multiple replicas can serve content to clients.
- **Controller (Load Balancer)**:
  - Fetches a list of videos from the origin at startup.
  - Ensures all replicas cache these videos before requests arrive.
  - Implements load balancing (e.g., round-robin) and redirects clients to the appropriate replica.
- **Nginx (Reverse Proxy)**:
  - Terminates TLS and serves content over HTTP/2 to the client.
  - Handles all traffic so the client never directly accesses origin or replicas via plain HTTP.
  - Routes requests internally to the controller and replicas over HTTP, ensuring the client experience remains fully encrypted and uses HTTP/2.

## How It Works

1. **Startup**:
   - The **Origin Server** runs on a specified port (e.g., 9001) and hosts the original videos in a directory.
   - Each **Replica Server** runs on its own port (e.g., 9002 and 9003) and starts empty.
   - The **Controller** runs on its port (e.g., 9004), fetches the video list from the origin, and instructs the origin to push videos to replicas that don’t have them cached.

2. **Pre-Caching**:
   - On startup, the controller calls the origin’s `/list_videos` endpoint.
   - For each video, it checks each replica’s `/is_cached/<filename>` endpoint.
   - If not cached, the controller requests the origin’s `/push_video` endpoint to send the file to that replica’s `/cache_video/<filename>` endpoint.
   - After this process, all replicas have the required videos ready to serve.

3. **Request Handling**:
   - The client connects to Nginx over HTTPS and HTTP/2 (e.g., `https://localhost:9005/video/<filename>`).
   - Nginx proxies that request to the **Controller**.
   - The Controller decides which replica should serve the request, then returns a redirect to a replica-specific path (e.g., `https://localhost:9005/replica1/video/<filename>`).
   - The client follows this redirect, still staying under Nginx’s HTTPS domain and HTTP/2 connection.
   - Nginx maps `/replica1/` or `/replica2/` paths internally to the respective replica servers (e.g., `http://localhost:9002` or `http://localhost:9003`), serving the cached video file back to the client over the existing encrypted, HTTP/2 connection.

4. **Result**:
   - The client sees a seamless HTTPS/HTTP/2 experience.
   - The origin and replicas communicate internally via HTTP, but the client never leaves the secure domain of Nginx.
   - All video content, redirects, and caching operations remain transparent to the client, while benefiting from modern HTTP protocols and security.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

2. **Set Environment Variables**:
   ```bash
   export VIDEO_DIR=./videos
   export ORIGIN_PORT=9001
   export CACHE_DIR_1=./videos1
   export REPLICA_PORT_1=9002
   export CACHE_DIR_2=./videos2
   export REPLICA_PORT_2=9003
   export CONTROLLER_PORT=9004
   ```
3. **Set Environment Variables**:
   ```bash
   python3 origin_server.py
   python3 replica_server_1.py
   python3 replica_server_2.py
   python3 controller.py

   ```
4. **Configure Nginx**:
  - Set up nginx.conf with:
    - A server block listening on a port (e.g., 9005) with ssl and http2 on;
    - proxy_pass rules pointing / to the controller and `/replica1/` or `/replica2/` to each replica.
    - Obtain or generate TLS certificates and reference them in `nginx.conf`.
5. **Configure Nginx**:
   ```bash
   brew services start nginx
   ```


