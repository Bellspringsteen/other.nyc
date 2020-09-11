import csv
import geocoder
import time
import copy
import json
from geojson import Feature, Point, FeatureCollection

dictionaryOfPrecinctsToCounties = {}
dictionaryOfZips = {}

def primeDictionaryOfPrecinctsToCounties():
	with open('NYCAreaZipToCounties.csv', 'rb') as csvfile:
		rowReader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in rowReader:
			dictionaryOfPrecinctsToCounties[row[0]] = row[1]

def primeZips():
	with open('ListOfZipsInNYPDFOILData.csv', 'rb') as csvfile:
		rowReader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in rowReader:
			dictionaryOfZips[row[0]] = 1

def getCounty(zipCode):
	return dictionaryOfPrecinctsToCounties[zipCode]


def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


def processFOILData():

	with open('NYPDFoilOfficerHomeZipData.csv', 'rb') as csvfile:

		primeZips();
		primeDictionaryOfPrecinctsToCounties();
		csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		outputJsonPrecinctToZipNumberFile = open('../resources/PrecinctToNumberOfficersInZip.json', 'wb')
		outputJsonPrecinctToZipNumber = {}
		outputFilePrecinct = open('../resources/precincts.geojson', 'wb')
		numberOfRows = 0
		columnNames = {}
		features = []
		
		outputFileHome = open('../resources/homeZipGeoJsonOverlay.geojson', 'wb')
		numberOfCols = 0
		numberWhoWorkInBKLYN = {}
		numberWhoWorkInBRNX = {}
		numberWhoWorkInMN= {}
		numberWhoWorkInST = {}
		numberWhoWorkInQN = {}
		featuresHome = []
		featuresPrecinct = []
		
		totalNumberWhoLiveInNYC = 0
		totalNumberWhoLiveInBKLYN = 0
		totalNumberWhoLiveInBRNX = 0
		totalNumberWhoLiveInMN= 0
		totalNumberWhoLiveInST = 0
		totalNumberWhoLiveInQN = 0
		totalNumberWhoLiveInLongIsland = 0
		totalNumberWhoLiveInUpstateNy = 0
		totalNumberWhoLiveInSameZip= 0
		totalNumberWhoDontLiveInSameZip= 0
		totalNumberWhoDontLiveWhereTheyShould= 0

		for row in csvreader:
			if (numberOfRows==0):
				columnNames = copy.deepcopy(row)
			else:
				numberWhoLiveInNYC = 0
				numberWhoLiveInBKLYN = 0
				numberWhoLiveInBRNX = 0
				numberWhoLiveInMN= 0
				numberWhoLiveInST = 0
				numberWhoLiveInQN = 0
				numberWhoLiveInLongIsland = 0
				numberWhoLiveInUpstateNy = 0
				numberWhoLiveInSameZip= 0
				numberWhoDontLiveInSameZip = 0
				numberWhoDontLiveWhereTheyShould = 0

				precinctLat = 0.0
				precinctLng = 0.0
				numberOfOfficersInPrecinct = 0
				precinctZip = row[3]
				## Get Lat Long of Precinct
				precinctLat = row[1]
				precintLng = row[2]
				if (precinctLat ==""):
					break
			
				## Copy Over Totals

				numberOfOfficersInPrecinct = float(row[len(row)-1])
				## Iterate Through Columns fill numberLiveManhattan,numberLiveStaten,numberLiveQueens,numberLiveBrooklyn,numberLiveBronx

				jsonOfHomeZipWithOfficersPerPrecinct = {}
				largestNumberOfOfficersInOneZip = 0
				for columnId in range(4,len(row)-1):
				
					if (row[columnId]):
							zipHomeLocation = columnNames[columnId]
							zipWorkLocation = row[3]
							if (zipWorkLocation):
								if (zipHomeLocation not in numberWhoWorkInMN):
									numberWhoWorkInMN[zipHomeLocation]=0
									numberWhoWorkInBRNX[zipHomeLocation]=0
									numberWhoWorkInBKLYN[zipHomeLocation]=0
									numberWhoWorkInQN[zipHomeLocation]=0
									numberWhoWorkInST[zipHomeLocation] = 0
								if (getCounty(zipWorkLocation) =="New York County"):
									numberWhoWorkInMN[zipHomeLocation]= numberWhoWorkInMN.get(zipHomeLocation,0)+int(row[columnId])
								elif (getCounty(zipWorkLocation)=="Bronx County"):
									numberWhoWorkInBRNX[zipHomeLocation]= numberWhoWorkInBRNX.get(zipHomeLocation,0)+int(row[columnId])
								elif (getCounty(zipWorkLocation)=="Kings County"):
									numberWhoWorkInBKLYN[zipHomeLocation]= numberWhoWorkInBKLYN.get(zipHomeLocation,0)+int(row[columnId])
								elif (getCounty(zipWorkLocation)=="Queens County"):
									numberWhoWorkInQN[zipHomeLocation]= numberWhoWorkInQN.get(zipHomeLocation,0)+int(row[columnId])
								elif (getCounty(zipWorkLocation)=="Richmond County"):
									numberWhoWorkInST[zipHomeLocation]= numberWhoWorkInST.get(zipHomeLocation,0)+int(row[columnId])
									
					zipCodeOfficerLocation = columnNames[columnId]
					zipCodeNumOfficersInLocation = row[columnId]
					jsonOfHomeZipWithOfficersPerPrecinct[zipCodeOfficerLocation] = zipCodeNumOfficersInLocation
					if (zipCodeNumOfficersInLocation>largestNumberOfOfficersInOneZip):
						largestNumberOfOfficersInOneZip = zipCodeNumOfficersInLocation
				
					if (zipCodeNumOfficersInLocation==""):
							zipCodeNumOfficersInLocation = 0;
					if (precinctZip!=zipCodeOfficerLocation):  # officers are not allowed to live in the same zip code, if they do this is invalid
						if (getCounty(zipCodeOfficerLocation) =="New York County"):
							numberWhoLiveInMN += int(zipCodeNumOfficersInLocation)
							numberWhoLiveInNYC += int(zipCodeNumOfficersInLocation)
						elif (getCounty(zipCodeOfficerLocation)=="Bronx County"):
							numberWhoLiveInBRNX += int(zipCodeNumOfficersInLocation)
							numberWhoLiveInNYC += int(zipCodeNumOfficersInLocation)
						elif (getCounty(zipCodeOfficerLocation)=="Kings County"):
							numberWhoLiveInBKLYN += int(zipCodeNumOfficersInLocation)
							numberWhoLiveInNYC += int(zipCodeNumOfficersInLocation)
						elif (getCounty(zipCodeOfficerLocation)=="Queens County"):
							numberWhoLiveInQN += int(zipCodeNumOfficersInLocation)
							numberWhoLiveInNYC += int(zipCodeNumOfficersInLocation)
						elif (getCounty(zipCodeOfficerLocation)=="Richmond County"):
							numberWhoLiveInST += int(zipCodeNumOfficersInLocation)
							numberWhoLiveInNYC += int(zipCodeNumOfficersInLocation)
						elif ((getCounty(zipCodeOfficerLocation)=="Suffolk County")|(getCounty(zipCodeOfficerLocation)=="Nassau County")):
							numberWhoLiveInLongIsland += int(zipCodeNumOfficersInLocation)
						elif ((getCounty(zipCodeOfficerLocation)=="Westchester County")|(getCounty(zipCodeOfficerLocation)=="Putnam County")|(getCounty(zipCodeOfficerLocation)=="Orange County")|(getCounty(zipCodeOfficerLocation)=="Rockland County")):
							numberWhoLiveInUpstateNy += int(zipCodeNumOfficersInLocation)
						else:
							numberWhoDontLiveWhereTheyShould += int(zipCodeNumOfficersInLocation)
							if (zipCodeNumOfficersInLocation>0):
								print("Zip Code"+str(zipCodeOfficerLocation)+" and number"+str(zipCodeNumOfficersInLocation)+" and county"+getCounty(zipCodeOfficerLocation))
														
						numberWhoDontLiveInSameZip += int(zipCodeNumOfficersInLocation)
					else:
						numberWhoLiveInSameZip += int(zipCodeNumOfficersInLocation)


				totalNumberWhoLiveInNYC += numberWhoLiveInNYC
				totalNumberWhoLiveInBKLYN += numberWhoLiveInBKLYN
				totalNumberWhoLiveInBRNX += numberWhoLiveInBRNX
				totalNumberWhoLiveInMN += numberWhoLiveInMN
				totalNumberWhoLiveInST += numberWhoLiveInST
				totalNumberWhoLiveInQN += numberWhoLiveInQN
				totalNumberWhoLiveInLongIsland += numberWhoLiveInLongIsland
				totalNumberWhoLiveInUpstateNy += numberWhoLiveInUpstateNy
				totalNumberWhoLiveInSameZip += numberWhoLiveInSameZip
				totalNumberWhoDontLiveInSameZip += numberWhoDontLiveInSameZip
				totalNumberWhoDontLiveWhereTheyShould += numberWhoDontLiveWhereTheyShould
				
				jsonOfHomeZipWithOfficersPerPrecinct["LargestNumber"] = largestNumberOfOfficersInOneZip
				outputJsonPrecinctToZipNumber[row[0]] = jsonOfHomeZipWithOfficersPerPrecinct

				featuresPrecinct.append({"geometry": {"coordinates": [float(precintLng), float(precinctLat)], "type": "Point"}, "properties": {"PRECINCTNAME": row[0],"OFFICERSSAMEZIP": str(round(numberWhoLiveInSameZip/numberOfOfficersInPrecinct,2)),"OFFICERSFROMBROOKLYN": str(round(numberWhoLiveInBKLYN/numberOfOfficersInPrecinct,2)),"OFFICERSFROMBRONX": str(round(numberWhoLiveInBRNX/numberOfOfficersInPrecinct,2)),"OFFICERSFROMMANHATTAN":str(round(numberWhoLiveInMN/numberOfOfficersInPrecinct,2)),"OFFICERSFROMSTATEN": str(round(numberWhoLiveInST/numberOfOfficersInPrecinct,2)),"OFFICERSFROMQUEENS": str(round(numberWhoLiveInQN/numberOfOfficersInPrecinct,2)),"OFFICERSFROMLONGISLAND": str(round(numberWhoLiveInLongIsland/numberOfOfficersInPrecinct,2)),"OFFICERSFROMUPSTATE":str(round(numberWhoLiveInUpstateNy/numberOfOfficersInPrecinct,2)),"OFFICERSFROMNYC": str(round(numberWhoLiveInNYC/numberOfOfficersInPrecinct,2))}, "type": "Feature"})
		
			numberOfRows+=1
		
		print(str(100*round(totalNumberWhoLiveInNYC/22218.0,2))+"% of NYPD Officers Live in NYC ")
		print(str(100*round(totalNumberWhoLiveInMN/22218.0,2))+"% of NYPD Officers Live in Manhattan")
		print(str(100*round(totalNumberWhoLiveInBKLYN/22218.0,2))+"% of NYPD Officers Live in Brooklyn")
		print(str(100*round(totalNumberWhoLiveInBRNX/22218.0,2))+"% of NYPD Officers Live in The Bronx ")
		print(str(100*round(totalNumberWhoLiveInST/22218.0,2))+"% of NYPD Officers Live in Staten Island")
		print(str(100*round(totalNumberWhoLiveInQN/22218.0,2))+"% of NYPD Officers Live in Queens")
		print(str(100*round(totalNumberWhoLiveInLongIsland/22218.0,2))+"% of NYPD Officers Live in Long Island")
		print(str(100*round(totalNumberWhoLiveInUpstateNy/22218.0,2))+"% of NYPD Officers Live in Upstate NY")
		print(str(100*round(totalNumberWhoLiveInSameZip/22218.0,2))+"% of NYPD Officers Live in the Same Zip they Serve ")
		print(str(100*round(totalNumberWhoDontLiveWhereTheyShould/22218.0,2))+"% of NYPD Officers Who Dont Live Where they should ")

			
		
		with open("./usZipShapes.geojson") as json_file:
			json_data = json.load(json_file)
			for i in (json_data['features']):
				if (i['properties'])['ZCTA5CE10'] in dictionaryOfZips:
					if (i['properties'])['ZCTA5CE10'] in numberWhoWorkInMN:
						i['properties']["OFFICERINZIP"]= int(numberWhoWorkInMN[i['properties']['ZCTA5CE10']])+int(numberWhoWorkInQN[i['properties']['ZCTA5CE10']])+int(numberWhoWorkInST[i['properties']['ZCTA5CE10']])+int(numberWhoWorkInBRNX[i['properties']['ZCTA5CE10']])+int(numberWhoWorkInBKLYN[i['properties']['ZCTA5CE10']])
						#print("Officers in Zip "+str(i['properties']['ZCTA5CE10'] )+" equals "+str(i['properties']["OFFICERINZIP"]))
						i['properties']["OFFICERINMANHATTAN"]= numberWhoWorkInMN[i['properties']['ZCTA5CE10']]
						i['properties']["OFFICERINBRONX"]= numberWhoWorkInBRNX[i['properties']['ZCTA5CE10']]
						i['properties']["OFFICERINBROOKLYN"]= numberWhoWorkInBKLYN[i['properties']['ZCTA5CE10']]
						i['properties']["OFFICERINQUEENS"]= numberWhoWorkInQN[i['properties']['ZCTA5CE10']]
						i['properties']["OFFICERINSTATEN"]= numberWhoWorkInST[i['properties']['ZCTA5CE10']]

					else:
						i['properties']["OFFICERINZIP"]= 0
						i['properties']["OFFICERINZIPTEXT"]= ''


					featuresHome.append(i)
			
		
		collectionToWrite = FeatureCollection(featuresHome)
		json.dump(collectionToWrite, outputFileHome)
	
	
		json.dump(outputJsonPrecinctToZipNumber, outputJsonPrecinctToZipNumberFile)
		collectionToWrite = FeatureCollection(featuresPrecinct)
		json.dump(collectionToWrite, outputFilePrecinct)
		

processFOILData() 
		