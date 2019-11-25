package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"
)

type YelpResponseStruct struct {
	Businesses []struct {
		ID          string `json:"id"`
		Alias       string `json:"alias"`
		Name        string `json:"name"`
		ImageURL    string `json:"image_url"`
		IsClosed    bool   `json:"is_closed"`
		URL         string `json:"url"`
		ReviewCount int    `json:"review_count"`
		Categories  []struct {
			Alias string `json:"alias"`
			Title string `json:"title"`
		} `json:"categories"`
		Rating      float64 `json:"rating"`
		Coordinates struct {
			Latitude  float64 `json:"latitude"`
			Longitude float64 `json:"longitude"`
		} `json:"coordinates"`
		Transactions []interface{} `json:"transactions"`
		Price        string        `json:"price"`
		Location     struct {
			Address1       string      `json:"address1"`
			Address2       string      `json:"address2"`
			Address3       interface{} `json:"address3"`
			City           string      `json:"city"`
			ZipCode        string      `json:"zip_code"`
			Country        string      `json:"country"`
			State          string      `json:"state"`
			DisplayAddress []string    `json:"display_address"`
		} `json:"location"`
		Phone        string  `json:"phone"`
		DisplayPhone string  `json:"display_phone"`
		Distance     float64 `json:"distance"`
	} `json:"businesses"`
	Total  int `json:"total"`
	Region struct {
		Center struct {
			Longitude float64 `json:"longitude"`
			Latitude  float64 `json:"latitude"`
		} `json:"center"`
	} `json:"region"`
}


func QueryYelpForResturantsAtLatLngRadius(latToQuery float64,longToQuery float64,radius int) YelpResponseStruct {
	client := &http.Client{
	}
	req, err := http.NewRequest("GET",fmt.Sprintf("https://api.yelp.com/v3/businesses/search?latitude=%f&longitude=%f&radius=%d&categories=restaurants",latToQuery,longToQuery,radius),nil)
	if err != nil{
		fmt.Println("Call to yelp failed")
		os.Exit(1)

	}
	bearerToken := os.Getenv("YELP_BEARER_TOKEN")
	req.Header.Add("Authorization", "Bearer "+bearerToken)
	resp, err := client.Do(req)
	if err != nil{
		fmt.Println("Call to yelp failed, did you set YELP_BEARER_TOKEN")
		os.Exit(1)
	}

	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil{
		fmt.Println("Call to read body failed")
		os.Exit(1)
	}

	res := YelpResponseStruct{}
	json.Unmarshal([]byte(body), &res)

	return res
}

func AddrssIsOnAvenue(address string ) bool {
	if strings.Contains(address,"ave") || strings.Contains(address,"Ave"){
		return true
	}
	return false
}

func AddrssIsOnStreet(address string ) bool {
	if strings.Contains(address,"st") || strings.Contains(address,"St")||strings.Contains(address,"street") || strings.Contains(address,"Street"){
		return true
	}
	return false
}