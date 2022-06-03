# Overview
This repository provides a persistent wrapper around mongodb functionality. 

# Dependencies
- pymongo 4.1.1 or laters

## Mongo Database

### Docker Install
sudo docker run -dp 27017:27017 -v local-mongo:/data/db --name local-mongo --restart=always mongo


#Command line tools
mongoimport --db=DFT -c=final --file=QDX_bag_lap_liq_J050_1_metadata.json
