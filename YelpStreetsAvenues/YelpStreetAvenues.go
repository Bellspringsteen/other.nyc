package main

import (
	"fmt"
	geo "github.com/kellydunn/golang-geo"
	"math/rand"
	"os"
	"time"
)
var numberPointsToQuery = 20
var radiusToQueryYelpWith = 50
var totalStreets,totalAvenues float32 = 0,0
var instancesStreets, instancesAvenues float32 = 0,0
var avenues = make([]float64, 0)
var streets = make([]float64, 0)
var arrayOfManhattanPolygons = []geo.Polygon {}

func queryYelpWithLatLngAddResultsToGlobalVariables(latToQuery float64,longToQuery float64) {
	var yelpResponseObject = QueryYelpForResturantsAtLatLngRadius(latToQuery,longToQuery,radiusToQueryYelpWith)
	for _, bussiness := range yelpResponseObject.Businesses {
		if AddrssIsOnAvenue(bussiness.Location.Address1) {
			totalAvenues += float32(bussiness.Rating)
			instancesAvenues++
			avenues = append(avenues, bussiness.Rating)
		} else if AddrssIsOnStreet(bussiness.Location.Address1) {
			totalStreets += float32(bussiness.Rating)
			instancesStreets++
			streets = append(streets, bussiness.Rating)
		}
	}
}

func getRandomLatLngInManhattan() (float64,float64) {
	if (len(arrayOfManhattanPolygons)==0) {
		for _, arraysOfPolygons := range PolygonsOfManhattan {
			var pointArray []*geo.Point = getGeoPointArrayFromArraryOfLatLngs(arraysOfPolygons)
			var polygonToAdd = geo.NewPolygon(pointArray)
			arrayOfManhattanPolygons = append(arrayOfManhattanPolygons, * polygonToAdd)
		}
	}
	for {
		var randomLat = (BoundingBoxOfPolygon[1][1] - BoundingBoxOfPolygon[0][1])*rand.Float64() + BoundingBoxOfPolygon[0][1]
		var randomLong = (BoundingBoxOfPolygon[1][0] - BoundingBoxOfPolygon[0][0])*rand.Float64() + BoundingBoxOfPolygon[0][0]

		var testPoint = geo.NewPoint(randomLat, randomLong)
		for _,polygonToTest := range arrayOfManhattanPolygons{
			if polygonToTest.Contains(testPoint){
				return randomLat,randomLong
			}
		}
	}
}

func getGeoPointArrayFromArraryOfLatLngs(arrayOfArrayOfPoints [][]float64) []*geo.Point{
	var pointArray = []*geo.Point {}
	for _,arraysOfPointsThatMakeupPolygons := range arrayOfArrayOfPoints{
		point := geo.NewPoint(arraysOfPointsThatMakeupPolygons[1],arraysOfPointsThatMakeupPolygons[0])
		pointArray = append(pointArray,point)
	}
	return pointArray
}

func main() {
	rand.Seed(time.Now().UnixNano())
	for i := 1;  i<=numberPointsToQuery; i++ {
		lat,lng := getRandomLatLngInManhattan()
		queryYelpWithLatLngAddResultsToGlobalVariables(lat,lng)
	}

	helperPrintLines("/tmp/streets.csv.",streets)
	helperPrintLines("/tmp/avenues.csv.",avenues)
	helperPrintAndCountOccurences("/tmp/streetoccurences.csv",streets)
	helperPrintAndCountOccurences("/tmp/avenueoccurences.csv",avenues)
	fmt.Printf("Total Avenue Bussinesses %f average rating Avenues %f Total Street Businesses %f average rating streets %f",instancesAvenues,totalAvenues/instancesAvenues,instancesStreets,totalStreets/instancesStreets)
}

///// Helper Functions


func helperPrintLines(filePath string, values []float64) error {
	f, err := os.Create(filePath)
	if err != nil {
		return err
	}
	defer f.Close()
	for _, value := range values {
		fmt.Fprintln(f, value)  // print values to f, one per line
	}
	return nil
}

func helperPrintAndCountOccurences(filePath string, values []float64) error {
	f, err := os.Create(filePath)
	if err != nil {
		return err
	}
	defer f.Close()

	m := make(map[float64]int)
	for _, value := range values {
		m[value] = m[value]+1
	}
	i := 0.0
	for i < 6  {
		fmt.Fprintf(f, "%f,%d \n",i,m[i])  // print values to f, one per line
		i = i+.5
	}
	return nil
}