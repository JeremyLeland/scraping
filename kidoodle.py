from playwright.sync_api import sync_playwright
import requests

url = "https://kidoodle.tv/series/Olivia"

results = []

with sync_playwright() as p:
  browser = p.chromium.launch(headless=True)
  page = browser.new_page()

  def handle_response( response ):

    # Looking for
    # https://albedo.be.kidoodle.tv/api/2.0/content/series/slug/Olivia
    if "/slug/" in response.url.lower():
      data = response.json()
      for season in data[ 'seasons' ]:
        for episode in season[ 'episodes' ]:
          title = episode[ 'title' ].replace( '/', '_' )
          results.append( {
            'filename': f"{ episode[ 'seriesName' ] }.{ episode[ 'seasonAndEpisode' ] }.{ title }.mp4",
            'playerUrl': f"https://kidoodle.tv/player/{ episode[ 'seriesSlug' ] }/{ episode[ 'id' ] }",
          } )

    # TODO: Can we move this into a separate response-handling def in the for result loop below?
    #       Then could it have access to result.filename?
    #       (so we can just output the ffmpeg commands here?)
    if "m3u8" in response.url.lower():
      print( response.url )

    # if "manifest.json" in response.url.lower():
    #   data = response.json()
    #   print( data )

  page.on( "response", handle_response )

  page.goto(url)
  page.wait_for_timeout(5000)

  # print( results )

  for result in results:
    print( result[ 'filename' ] )
    page.goto( result[ 'playerUrl' ] )
    page.wait_for_timeout(5000)

  browser.close()


# https://albedo.be.kidoodle.tv/api/2.0/avod/web/3673/125516/700404/watch/manifest.json
