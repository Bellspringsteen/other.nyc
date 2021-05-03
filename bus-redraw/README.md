# I dont understand the bus

See article here -> 

## Code 

Code is poor quality, hacked together as a scratch pad.

bus_redraw.py is what generates points, parses results, creates js files with polylines

1. Get a google token for the directions api
2. Set environment variable 'export GOOGLE_TOKEN=12345'
3. Change REQUESTS_FOLDER to something on your system
4. uncomment whatever function you want to run at bottom and run

draw_map/index.html shows the map and you can uncomment code to draw different sections

Create local server (ex: python3 -m http.server)
add google api key to url parameter

http://localhost:8000/?access_key=PUT_KEY_HERE