import json
import re
import secrets
import time

import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

session = requests.Session()

session.headers.update( {
  "User-Agent": (
    "Mozilla/5.0 (X11; Linux x86_64; rv:155.0) "
    "Gecko/20100101 Firefox/155.0"
  ),
  "Referer": "https://www.wcostream.tv/",
} )

episode_url = "https://www.wcostream.tv/super-kitties-season-3-episode-10-the-glamping-glamsters-trouble-in-the-jungle"

print( episode_url )

page = session.get(
  episode_url,
  timeout=30,
)

page.raise_for_status()

soup = BeautifulSoup( page.content, "html.parser" )

title = soup.select_one( "h1 a" ).text.replace( '/', '_' )

iframe_url = soup.select_one("iframe")[ "src" ]
print( iframe_url )

iframe = session.get( iframe_url, timeout=30 )
print( iframe.status_code )

nonce = "a7d13d592cf51f15dd9c588f6c83325b"
# nonce = secrets.token_hex( 16 )

# beaconBody = json.dumps( {
#   "nonce": nonce,
#   "status": "clear",
#   "id": parse_qs( urlparse( iframe_url ).query )[ "pid" ][ 0 ],
# }, separators=(",", ":" ), ensure_ascii=False )

# print( beaconBody )

# beacon_response = session.post( 
#   "https://embed.wcostream.com/ad-verify",
#   data = beaconBody,
#   headers= {
#     "Content-Type": "application/json",
#     "Origin": "https://embed.wcostream.com",
#     "Referer": iframe_url,
#   }
# )

# print( session.cookies.get_dict() )

# print( beacon_response.status_code )
# print( beacon_response.text )

# time.sleep( 1 )

video_js_old_url = f"{ iframe_url.replace( "index.php", "video-js-old.php" ) }&n={ nonce }"

print( video_js_old_url )

video_js_old = session.get(
  video_js_old_url,
  timeout=30,
)

print( video_js_old.status_code )
# print( video_js_old.text )

video_js_old_html = video_js_old.text

vidlink_match = re.search( r'\$\.getJSON\("([^"]*)"', video_js_old_html )

if ( vidlink_match ):
  getvidlink_url = f"https://embed.wcostream.com{ vidlink_match.group( 1 ) }"

  print( getvidlink_url )

  session.headers.update( {
    "X-Requested-With": "XMLHttpRequest",
    "Referer": video_js_old_url,
  } )

  getvidlink = session.get( getvidlink_url )

  vidlink_json = getvidlink.json()

  print( vidlink_json )

  vsd = vidlink_json.get( 'fhd' )   # was enc, there's also hd?
  server = vidlink_json.get( 'server' )

  videoUrl = server + '/getvid?evid=' + vsd + '&json'

  print( videoUrl )

  finalLink = json.loads( session.get( videoUrl ).text )

  response = session.get( finalLink, stream=True )
  response.raise_for_status()

  output_folder = Path("/home/iggames/Downloads/superkitties/")
  output_folder.mkdir( parents=True, exist_ok=True )

  output_file = output_folder / f"{ title }.mp4"

  with open( output_file, "wb" ) as f:
    for chunk in response.iter_content( chunk_size=1024 * 1024 ):
      if chunk:
        f.write( chunk )

  print( f"Done with { title }" )