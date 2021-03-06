## SECTION 1 : PROJECT TITLE
### HDB Resale Prediction and Recommender (HRPR)
<img src="Miscellaneous/Images/Poster.png" style="float: left; margin-right: 0px;" />

## SECTION 2 : EXECUTIVE SUMMARY
“HDB resale prices climb for 4th consecutive quarter in Q1”, “HDB resale prices rise for 9th straight month in March with cash over valuation back in play”, “HDB resale transactions spike 127.3% in Q3 after end of COVID-19 circuit breaker”. These are headlines that are getting more common in recent days regarding resale HDB flats in Singapore.

Despite a circuit breaker introduced by government on Apr 7 to curb COVID-19, resale flat prices seemingly were spared the adverse gloom that impacted the economic environment in Singapore. This “stunning rebound” could be attributed to various stimulus packages that were introduced by the government prior to the start of the pandemic.
However, the incessant increase of resale HDB prices certainly make it challenging for prospective homebuyers. While BTO flats are an alternative, the long wait for getting the keys, coupled with construction delays, often are out of consideration for some buyers.

Hence, using the valuable knowledge we have learnt during our lectures in Intelligent Reasoning Systems, our group would like to implement a HDB Resale Prediction and Recommender (HRPR) tool to assist prospective buyers in their resale flat search.

For price prediction, we have used past resale flat transactions since 2015 (corrected with Resale Price Index). On the other hand, we also collected survey results from friends, families, and coursemates from various walks of life to get a general sentiment of important features to a flat buyer. The survey results were then used to implement a scoring system for our recommender system.

In summary, we hope that with HRPR, prospective buyers can estimate the suitable pricing to negotiate with sellers. Besides that, the recommender system of the tool can suggest potential listings that the users might overlook, especially swarmed by pages of listings that were refreshed daily.

## SECTION 3 : PROJECT CONTRIBUTION

| Full Name | Student ID | Work Items | Email |
|-----------|------------|------------|-------|
|Yee Wei Liang|A0045422R|Web Scraping, Data Cleaning, Feature Engineering|E0258287@u.nus.edu|
|Toh Kah Khek|A0229968E|Database Setup, Front-end Development, Back-end Integration|E0687376@u.nus.edu|
|Jeon Sungmin|A0133374J|Collaborative Filtering Recommendation System, System Performance & Testing, Video Editing|E0689806@u.nus.edu|
|Ahmed Syalabi Seet|A0229978A|Data Analysis, Data Cleaning, Prediction Tree Modelling|E0687386@u.nus.edu|

## SECTION 4 : VIDEO OF SYSTEM MODELLING & USE CASE DEMO
**Video 1: IRS-PM-2021-01-16-IS03PT-GRP-JSSW-HDBResalePredictionAndRecommender-promotion**

[![](http://img.youtube.com/vi/OBeyQfCPETg/0.jpg)](http://www.youtube.com/watch?v=OBeyQfCPETg "Video 1: Promotion")

**Video 2: IRS-PM-2021-01-16-IS03PT-GRP-JSSW-HDBResalePredictionAndRecommender-system**

[![](http://img.youtube.com/vi/dOF66BYlgZU/0.jpg)](http://www.youtube.com/watch?v=dOF66BYlgZU "Video 2: System")

## SECTION 5 : INSTALLATION AND USER GUIDE
**Installation guide for Ubuntu 20.04**

1. Navigate to folder of your choice and download the github repository

   command: git clone https://github.com/IRS-JSSW/HDBResalePriceRecommender

   <img src="Miscellaneous/Install Guide/Step1-1.png" style="float: left; margin-right: 0px;" />
   <img src="Miscellaneous/Install Guide/Step1-2.png" style="float: left; margin-right: 0px;" />

2. Install pip3 package

   command 1: sudo apt-get update
   
   command 2: sudo apt-get install python3-pip

   <img src="Miscellaneous/Install Guide/Step2-1.png" style="float: left; margin-right: 0px;" />
   <img src="Miscellaneous/Install Guide/Step2-2.png" style="float: left; margin-right: 0px;" />

3. Install virtualenv package

   command: sudo pip3 install virtualenv

   <img src="Miscellaneous/Install Guide/Step3.png" style="float: left; margin-right: 0px;" />

4. Navigate to HDBResalePriceRecommender and create virtualenv

   command: virtualenv -p python3 venv

   <img src="Miscellaneous/Install Guide/Step4-1.png" style="float: left; margin-right: 0px;" />
   <img src="Miscellaneous/Install Guide/Step4-2.png" style="float: left; margin-right: 0px;" />

5. Activate virtualenv

   command: source venv/bin/activate (Note: Ensure that you are seeing (venv) in the terminal)

   <img src="Miscellaneous/Install Guide/Step5.png" style="float: left; margin-right: 0px;" />

6. Install project dependencies from requirements.txt

   command: pip install -r requirements.txt

   | **No** | **Package** | **Version** |
   |----|---------|---------|
   | 1 | flask | 1.1.2 |
   | 2 | flask-wtf | 0.14.3 |
   | 3 | haversine | 2.3.0 |
   | 4 | requests | 2.25.1 |
   | 5 | selenium | 3.141.0 |
   | 6 | sklearn |---------|
   | 7 | sqlalchemy | 1.3.23 |

   <img src="Miscellaneous/Install Guide/Step6.png" style="float: left; margin-right: 0px;" />

**User guide**
**Part 1 - To start the app**
1. Navigate to HDBResalePriceRecommender and activate virtualenv
   
   command: source venv/bin/activate (Note: Ensure that you are seeing (venv) in the terminal) 
   
   <img src="Miscellaneous/User Guide/Step1-1.png" style="float: left; margin-right: 0px;" />
   <img src="Miscellaneous/User Guide/Step1-2.png" style="float: left; margin-right: 0px;" />

2. Start the flask application on local machine

   command: project run.py

   <img src="Miscellaneous/User Guide/Step2.png" style="float: left; margin-right: 0px;" />

3. Open browser (Firefox or Google Chrome) and navigate to URL http://127.0.0.1:5000/home

   <img src="Miscellaneous/User Guide/Step3.png" style="float: left; margin-right: 0px;" />

**Part 2 - To get predicted price of HDB Resale Flats**
1. Input valid Propertyguru Resale HDB listing in textbox and click on the Search button

   <img src="Miscellaneous/User Guide/Step4.png" style="float: left; margin-right: 0px;" />

2. Results of predicted price and other recommended Propertyguru listings will be generated

   <img src="Miscellaneous/Images/Poster.png" style="float: left; margin-right: 0px;" />

**Part 3 - To update HDB Resale Transactions Records from Data.gov**

1. Click on “Update” on the navigation bar and click on “Update Data Gov Table”

   <img src="Miscellaneous/User Guide/Step6.png" style="float: left; margin-right: 0px;" />

2. Next, select “Yes” in the dropdown menu and click on “Update” button. Selecting “No” will not update the database and redirects back to the homepage

   <img src="Miscellaneous/User Guide/Step7.png" style="float: left; margin-right: 0px;" />

**Part 4 - To update Propertyguru listings**

1. Click on “Update” on the navigation bar and click on “Update Propertyguru Table”

   <img src="Miscellaneous/User Guide/Step6.png" style="float: left; margin-right: 0px;" />

2. Next, select “Yes” in the dropdown menu and click on “Update” button. Selecting “No” will not update the database and redirects back to the homepage

   <img src="Miscellaneous/User Guide/Step8.png" style="float: left; margin-right: 0px;" />

**Part 5 - To update Amenities Table**

1. Click on “Update” on the navigation bar and click on “Update Amenities Tables”

   <img src="Miscellaneous/User Guide/Step6.png" style="float: left; margin-right: 0px;" />

2. Next, select “Yes” in the dropdown menu and click on “Update” button. Selecting “No” will not update the database and redirects back to the homepage

   <img src="Miscellaneous/User Guide/Step9.png" style="float: left; margin-right: 0px;" />

**Part 6 - To train Regression Model**

1. Click on “Update” on the navigation bar and click on “Update Training Model”

   <img src="Miscellaneous/User Guide/Step6.png" style="float: left; margin-right: 0px;" />

2. Next, select “Yes” in the dropdown menu and click on “Train” button. Selecting “No” will not update the regression model and redirects back to the homepage

   <img src="Miscellaneous/User Guide/Step10.png" style="float: left; margin-right: 0px;" />


## SECTION 6 : PROJECT REPORT
`<Project Report>` : \Project Report\Project Report_IRS-PM-2021-01-16-IS03PT-GRP-JSSW-HDBResalePredictionAndRecommender.pdf

1. Executive Summary
2. Business Problem Background
    - 2.1   Project Objective
    - 2.2   Market Research
3. Knowledge Modelling
    - 3.1   Knowledge Identification
    - 3.2   Knowledge Specification
    - 3.3   Knowledge Refinement
4. Project Solution
    - 4.1   System Implementation
    - 4.2   System Performance & Validation
5. Project Conclusions
    - Project Conclusion
    - Improvements
6. Appendix 
    - 6.1   Project Proposal
    - 6.2   Mapping of Domain/Technique Group
    - 6.3   Installation and User Guide
    - 6.4   Individual Project Reports
    - 6.5   List of Abbreviations
    - 6.6   References

## SECTION 7 : MISCELLANEOUS
`<Survey Results>` : \Miscellaneous\Survey Results\Importance when purchasing resale flat.csv

`<Summary of Results>` : \Miscellaneous\Survey Results\Feature Ranking.csv

- Results of survey (out of 74 responses)

<p align='center'> 
    <img src="https://user-images.githubusercontent.com/70024666/115525076-58f87d80-a2c1-11eb-96b0-356861c7f4c1.png">
</p>

- Insights derived, which were subsequently used in our recommender system

| Features | 1st Choice | 2nd Choice | 3rd Choice | 4th Choice | 5th Choice | Final Ranking |
|----------|:----------:|:----------:|:----------:|:----------:|:----------:|:-------------:|
|Ease of Access to LRT/MRT Station|42|24|2|3|3|1|
|Age of Flat|26|17|12|7|12|2|
|Distance to Hawker Centre|4|14|27|19|10|3|
|Distance to Mall|0|13|20|31|10|4|
|Distance to City Centre (Orchard)|2|6|13|14|39|5|
