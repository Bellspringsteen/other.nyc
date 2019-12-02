## Yelp Streets Vs Avenues Manhattan

Signup for a free Yelp API Token  https://www.yelp.com/developers/documentation/v3/business_search

Change numberPointsToQuery in YelpStreetAvenues to larger number for more data.

## BUILD & RUN

go install

export GOPATH=$(pwd)

export YELP_BEARER_TOKEN=PUT_YOUR_TOKEN_HERE

go run .

### RESULTS 

Abstract
Yelp data and statistical sampling was used to determine that the average restaurant is better on Manhattan streets than avenues, with an average rating of 3.62 on streets vs 3.49 on avenues. The difference was statistically significant. In addition, you are almost 50% more likely to find an outstanding restaurant while on a street compared to when you are on an avenue. 18% of restaurants on the streets had a score of 4.5 or higher, compared to 13% of restaurants on avenues.

[Link to PDF](https://github.com/Bellspringsteen/other.nyc/blob/master/YelpStreetsAvenues/StreetsVsAvenues.pdf)