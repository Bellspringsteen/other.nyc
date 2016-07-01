import csv
import geocoder
import time
import copy

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
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	outputFile = open('ListOfPrecinctsWithResidenceLocation.csv', 'wb')
	writer = csv.writer(outputFile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	numberOfRows = 0
	dictionaryOfZipsToColumns = {}
	numberOfficersLivingInSameZipTotal = 0
	columnNames = {}
	writer.writerow(["Precinct","Lat", "Long", "Percentage in Same Zip","Percentage in Brooklyn", "Percentage in Bronx", "Percentage in Manhattan", "Percentage in Staten Island", "Percentage in Queens", "Percentage in Long Island", "Percentage in Upstate Ny", "Percentage in NYC"])

	for row in spamreader:
		if (numberOfRows==0):
			print("Go Time")
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

			precinctLat = 0.0
			precinctLng = 0.0
			numberOfOfficersInPrecinct = 0
			precinctZip = row[3]
			## Get Lat Long of Precinct
			precinctLat = row[1]
			precintLng = row[2]
			
			#print("Precinct "+ row[0]+" Lat is "+str(precinctLat) + " precinctLong is " + str(precintLng));
			## Copy Over Totals

			numberOfOfficersInPrecinct = float(row[len(row)-1])

			## Iterate Through Columns fill numberLiveManhattan,numberLiveStaten,numberLiveQueens,numberLiveBrooklyn,numberLiveBronx

			for columnId in range(4,len(row)-1):
				zipCodeOfficerLocation = columnNames[columnId]
				zipCodeNumOfficersInLocation = row[columnId]
				if (zipCodeNumOfficersInLocation==""):
						zipCodeNumOfficersInLocation = 0;
				if (precinctZip!=zipCodeOfficerLocation):  # officers are not allowed to live in the same zip code, if they do this is invalid
					#print("zipCodeNumOfficersInLocation "+str(zipCodeNumOfficersInLocation)+" zipCodeOfficerLocation"+str(zipCodeOfficerLocation));
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
					numberWhoLiveInSameZip += int(zipCodeNumOfficersInLocation)

			print(str(row[0]) + " officersInSameZip " + str(round(numberWhoLiveInSameZip/numberOfOfficersInPrecinct,2))+ " BROOKLYN  "+str(round(numberWhoLiveInBKLYN/numberOfOfficersInPrecinct,2))+ " BRONX  "+str(round(numberWhoLiveInBRNX/numberOfOfficersInPrecinct,2))+ " LongIsland  "+str(round(numberWhoLiveInLongIsland/numberOfOfficersInPrecinct,2))+ " NYC  "+str(round(numberWhoLiveInNYC/numberOfOfficersInPrecinct,2))+ " Queens  "+str(round(numberWhoLiveInQN/numberOfOfficersInPrecinct,2))+ " UpstateNY  "+str(round(numberWhoLiveInUpstateNy/numberOfOfficersInPrecinct,2))+ " Manhattan  "+str(round(numberWhoLiveInMN/numberOfOfficersInPrecinct,2)));
			writer.writerow([row[0],precinctLat, precintLng, str(round(numberWhoLiveInSameZip/numberOfOfficersInPrecinct,2)),str(round(numberWhoLiveInBKLYN/numberOfOfficersInPrecinct,2)), str(round(numberWhoLiveInBRNX/numberOfOfficersInPrecinct,2)), str(round(numberWhoLiveInMN/numberOfOfficersInPrecinct,2)), str(round(numberWhoLiveInST/numberOfOfficersInPrecinct,2)), str(round(numberWhoLiveInQN/numberOfOfficersInPrecinct,2)), str(round(numberWhoLiveInLongIsland/numberOfOfficersInPrecinct,2)), str(round(numberWhoLiveInUpstateNy/numberOfOfficersInPrecinct,2)), str(round(numberWhoLiveInNYC/numberOfOfficersInPrecinct,2))])
			
		numberOfRows+=1
			
			
		