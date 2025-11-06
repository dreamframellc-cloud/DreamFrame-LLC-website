#!/usr/bin/env python3
"""
Simple HTTP file server for direct video downloads
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class VideoDownloadHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/lion':
            self.send_video('static/lion_customer.mp4', 'Lion_of_Judah_Customer_Video.mp4')
        elif self.path == '/kindness':
            self.send_video('static/kindness_customer.mp4', 'Kindness_Customer_Video.mp4')
        else:
            super().do_GET()
    
    def send_video(self, file_path, download_name):
        if os.path.exists(file_path):
            self.send_response(200)
            self.send_header('Content-Type', 'video/mp4')
            self.send_header('Content-Disposition', f'attachment; filename="{download_name}"')
            self.send_header('Content-Length', str(os.path.getsize(file_path)))
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, 'Video not found')

def start_download_server():
    port = 8080
    server = HTTPServer(('0.0.0.0', port), VideoDownloadHandler)
    print(f"Download server started on port {port}")
    print(f"Lion video: http://localhost:{port}/lion")
    print(f"Kindness video: http://localhost:{port}/kindness")
    server.serve_forever()

if __name__ == "__main__":
    start_download_server()