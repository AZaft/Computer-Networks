# Programming Assignment #1

HTTP server and HTTP proxy server using only the socket library.

## Running programs

The webserver and proxyserver can be run in the terminal with the command "python webserver.py" or "python proxyserver.py" depending on the python installation.

## Webpages tested on web server (chrome)
localhost:6789/HelloWorld.html return html file successfully

localhost:6789/sbu.jpg return jpg file successfully

localhost:6789/test/seawolf.png return png file successfully

localhost:6789/doesnotexist.html returned 404 successfully

## Webpages tested on proxy (chrome)
The following files/images were tested and returned image successfully and request response was cached
Note: Response buffer set to 64k bytes and may require increase for larger images/files
http://localhost:8888/http://gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file2.html
http://localhost:8888/http://gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file3.html
http://localhost:8888/https://www.bravofurniture.net/images/catalog_icons/27.jpg  
http://localhost:8888/https://png.pngtree.com/png-vector/20210119/ourmid/pngtree-3d-alphabet-small-c-png-image_2764190.png


