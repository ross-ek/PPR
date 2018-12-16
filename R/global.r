library(shiny)
library(leaflet)
library(dplyr)
library(rgdal)

df <- readRDS("./sample_data.rds")

# Shape Files
# https://www.autoaddress.ie/support/developer-centre/resources/routing-key-boundaries

eircode_boundaries <- readOGR(dsn="shp", layer="RoutingKeys_WGS84_region") 

# RoutingKeys_WGS84_region

df <- readRDS("./sample_data.rds")

dub_codes <- subset(eircode_boundaries, eircode_boundaries$RoutingKey %in% c(
  'Y14','A84','H65','N37','R14','K32','F26','H53','P31','F31','A41','F35','F56','P72','P75','H14','R42','A94','F52','A98','V23','E21','R93',
  'A81','N41','E32','P43','E25','F23','A75','F45','H12','P56','F12','H71','P85','H23','E91','P24','H16','T12','T23','P14','P32','P47','T56',
  'T34','R56','F94','A92','D01','D02','D03','D04','D05','D06','D6W','D07','D08','D09','D10','D11','D12','D13','D14','D15','D16','D17','D18',
  'D20','D22','D24','A86','A91','X35','A85','R45','A83','V95','Y21','P61','H91','A42','A96','Y25','A63','A82','R51','R95','V93','X42','V35',
  'V15','P17','F92','F93','V94','V31','T45','N39','H62','K78','K45','P12','K36','P51','W23','P25','P67','H18','W34','R21','N91','W91','C15',
  'E45','Y34','W12','V42','A45','R32','F42','E53','K56','V14','K34','P81','F91','K67','E41','E34','V92','H54','R35','X91','F28','Y35','A67'
  ,'P36'
  
))

leaflet(dub_codes) %>%
  addPolygons(color = "#444444", weight = 1, smoothFactor = 0.5,
              opacity = 1.0, fillOpacity = 0.5,
              highlightOptions = highlightOptions(color = "white", weight = 1,
                                                  bringToFront = TRUE))
