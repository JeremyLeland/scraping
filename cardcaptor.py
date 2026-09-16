import requests
from pathlib import Path
from bs4 import BeautifulSoup

session = requests.Session()

session.headers.update( {
  "User-Agent": (
    "Mozilla/5.0 (X11; Linux x86_64; rv:155.0) "
    "Gecko/20100101 Firefox/155.0"
  )
} )

session.cookies.update( {
  "3-Day-Trial-2" :	"1789286465",
  "cf_clearance":	"<COPY FROM COOKIE>",
  "wco_cc":	"1",
  "whats_new":	"close",
  "wordpress_logged_in_XXXXXXXX":	"<COPY FROM COOKIE>",
  "wordpress_sec_XXXXXXXXX":	"<COPY FROM COOKIE>",
  "wordpress_test_cookie":	"WP Cookie check",
} )


episode_page = session.get(
  "https://free.wcopremium.tv/anime/cardcaptor-sakura",
  timeout=30,
)
episode_page.raise_for_status()

soup = BeautifulSoup( episode_page.content, "html.parser" )

episode_list = soup.select( "div#episodeList a" )

for episode in episode_list:
  episode_url = f"http://free.wcopremium.tv/{ episode[ "href" ] }"

  print( episode_url )

  page = session.get(
    episode_url,
    timeout=30,
  )

  page.raise_for_status()

  soup = BeautifulSoup(page.content, "html.parser")

  title = soup.select_one("h1").text

  link = soup.select_one("div.download-player a")
  mp4_url = link[ "href" ]

  print( mp4_url )

  response = session.get( mp4_url, stream=True )
  response.raise_for_status()

  output_folder = Path("/home/iggames/Downloads/Cardcaptor/")
  output_folder.mkdir(parents=True, exist_ok=True)

  output_file = output_folder / f"{ title }.mp4"

  with open( output_file, "wb" ) as f:
    for chunk in response.iter_content( chunk_size=1024 * 1024 ):
      if chunk:
        f.write( chunk )

  print( f"Done with { title }" )