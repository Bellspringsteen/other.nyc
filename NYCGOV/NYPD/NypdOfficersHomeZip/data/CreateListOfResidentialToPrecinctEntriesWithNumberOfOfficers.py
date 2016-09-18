import csv
import geocoder
import time
import copy
import json
from geojson import Feature, Point, FeatureCollection

dictionaryOfPrecinctsToCounties = {}

def primeDictionaryOfPrecinctsToCounties():
	with open('Counties.csv', 'rb') as csvfile:
		rowReader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in rowReader:
			dictionaryOfPrecinctsToCounties[row[0]] = row[1]


def getCounty(zipCode):
	return dictionaryOfPrecinctsToCounties[zipCode]


def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

with open('WithZips.csv', 'rb') as csvfile:


	primeDictionaryOfPrecinctsToCounties();
	csvReader = csv.reader(csvfile, delimiter=',', quotechar='|')
	outputFile = open('homeZip.geojson', 'wb')

	
	
	numberOfCols = 0
	numberOfRows = 0



	dictionaryOfZipsToColumns = {}
	numberOfficersLivingInSameZipTotal = 0
	zipHomeLocations = {}
	
	numberWhoWorkInBKLYN = {}
	numberWhoWorkInBRNX = {}
	numberWhoWorkInMN= {}
	numberWhoWorkInST = {}
	numberWhoWorkInQN = {}
	features = []

	for row in csvReader:
		numberOfRows+=1
		if (numberOfRows==1):
			zipHomeLocations = copy.deepcopy(row)
		else:
			outputJsonPrecinctToZipNumber[
			numberOfCols = 0
			for col in row:
				numberOfCols+=1

				if (numberOfCols>4):
				
					if (col):
						zipHomeLocation = zipHomeLocations[numberOfCols-1]
						zipWorkLocation = row[3]
						if (zipWorkLocation):

							if (getCounty(zipWorkLocation) =="New York County"):
								numberWhoWorkInMN[zipHomeLocation]= numberWhoWorkInMN.get(zipHomeLocation,0)+int(col)
							elif (getCounty(zipWorkLocation)=="Bronx County"):
								numberWhoWorkInBRNX[zipHomeLocation]= numberWhoWorkInBRNX.get(zipHomeLocation,0)+int(col)
							elif (getCounty(zipWorkLocation)=="Kings County"):
								numberWhoWorkInBKLYN[zipHomeLocation]= numberWhoWorkInBKLYN.get(zipHomeLocation,0)+int(col)
							elif (getCounty(zipWorkLocation)=="Queens County"):
								numberWhoWorkInQN[zipHomeLocation]= numberWhoWorkInQN.get(zipHomeLocation,0)+int(col)
							elif (getCounty(zipWorkLocation)=="Richmond County"):
								numberWhoWorkInST[zipHomeLocation]= numberWhoWorkInST.get(zipHomeLocation,0)+int(col)

	
	for key in numberWhoWorkInMN:
		workInBrklyn = numberWhoWorkInBKLYN.get(key,0)
		workInBrnx = numberWhoWorkInBRNX.get(key,0)
		workInQueens= numberWhoWorkInQN.get(key,0)
		workInStaten = numberWhoWorkInST.get(key,0)
		workInManhattan = numberWhoWorkInMN.get(key,0)
		g = geocoder.google(key)

		homeLat = g.lat
		homeLong = g.lng
		time.sleep(1.0) 
		print("The zip is "+str(key)+" lat  "+str(homeLat) + " lng "+ str(homeLong) +" "+str(workInBrklyn)+" "+str(workInManhattan)+" "+str(workInStaten)+" "+str(workInQueens)+" "+str(workInBrnx))

 		features.append({"geometry": {"coordinates": [homeLong, homeLat], "type": "Point"}, "properties": {"Home Zip": key,"Number Who Work in Manhattan Precincts": workInManhattan,"Number Who Work in Bronx Precincts": workInBrnx,"Number Who Work in Brooklyn Precincts": workInBrklyn,"Number Who Work in Queens Precincts":workInQueens,"Number Who Work in Staten Island Precincts": workInStaten}, "type": "Feature"})

		#writer.writerow(["Home Zip","Lat", "Long", "Number Who Work in Manhattan Precincts","Number Who Work in Bronx Precincts","Number Who Work in Brooklyn Precincts","Number Who Work in Queens Precincts","Number Who Work in Staten Island Precincts"])
	
	collectionToWrite = FeatureCollection(features)
	print(len(features))
	#print(collectionToWrite)
	json.dump(collectionToWrite, outputFile)
			
			