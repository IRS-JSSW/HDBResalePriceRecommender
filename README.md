## SECTION 1 : PROJECT TITLE
### HDB Resale Recommender
<img src="Miscellaneous/Images/Poster.png?raw=true" style="float: left; margin-right: 0px;" />

## SECTION 2 : EXECUTIVE SUMMARY

## SECTION 3 : PROJECT CONTRIBUTION

| Full Name | Student ID | Work Items | Email |
|-----------|------------|------------|-------|
|Yee Wei Liang|A0045422R|Web Scraping, Data Cleaning, Feature Engineering |E0258287@u.nus.edu|
|Toh Kah Khek|A0229968E|Database Setup, Front-end Development, Back-end Integration|E0687376@u.nus.edu|
|Jeon Sung Min|------------|------------|-------|
|Ahmed Syalabi Seet|A0229978A|Data Analysis, Data Cleaning, Prediction Tree Modelling|E0687386@u.nus.edu|

## SECTION 4 : VIDEO OF SYSTEM MODELLING & USE CASE DEMO

## SECTION 5 : INSTALLATION AND USER GUIDE
# Installation guide for Ubuntu 20.04
<img src="Miscellaneous/Install_Guide/Step1-1.png?raw=true" style="float: left; margin-right: 0px;" />
<img src="Miscellaneous/Install_Guide/Step1-2.png?raw=true" style="float: left; margin-right: 0px;" />
1. Navigate to folder of your choice and download the github repository
   command: git clone https://github.com/IRS-JSSW/HDBResalePriceRecommender

<img src="Miscellaneous/Install_Guide/Step2.png?raw=true" style="float: left; margin-right: 0px;" />
2. Install pip3 package
   command: sudo apt-get install python3-pip

<img src="Miscellaneous/Install_Guide/Step3.png?raw=true" style="float: left; margin-right: 0px;" />
3. Install virtualenv package
   command: sudo pip3 install virtualenv

<img src="Miscellaneous/Install_Guide/Step4-1.png?raw=true" style="float: left; margin-right: 0px;" />
<img src="Miscellaneous/Install_Guide/Step4-2.png?raw=true" style="float: left; margin-right: 0px;" />
4. Navigate to HDBResalePriceRecommender and create virtualenv
   command: virtualenv -p python3 venv

<img src="Miscellaneous/Install_Guide/Step5.png?raw=true" style="float: left; margin-right: 0px;" />
5. Activate virtualenv
   command: source venv/bin/activate
   (Note: Ensure that you are seeing (venv) in the terminal)

<img src="Miscellaneous/Install_Guide/Step6.png" style="float: left; margin-right: 0px;" />
6. Install project dependencies from requirements.txt
   command: pip install -r requirements.txt
   | No | Package | Version |
   | 1 | flask | 1.1.2 |
   | 2 | flask-wtf | 0.14.3 |
   | 3 | haversine | 2.3.0 |
   | 4 | requests | 2.25.1 |
   | 5 | selenium | 3.141.0 |
   | 6 | sklearn | - |
   | 7 | sqlalchemy | 1.3.23 |

# User guide
<img src="Miscellaneous/User_Guide/Step1-1.png" style="float: left; margin-right: 0px;" />
<img src="Miscellaneous/User_Guide/Step1-2.png" style="float: left; margin-right: 0px;" />
1. Navigate to HDBResalePriceRecommender and activate virtualenv

<img src="Miscellaneous/User_Guide/Step2.png" style="float: left; margin-right: 0px;" />
2. Start the flask application on local machine
   command: project run.py

3. 

## SECTION 6 : PROJECT REPORT

1. Executive Summary (WEILIANG)
2. Business Problem Background
    - 2.1   Project Objective (WEILIANG)
    - 2.2   Market Research (WEILIANG)
    - 2.3   Success Measurements (OPTIONAL)
3. Knowledge Modelling (http://ksi.cpsc.ucalgary.ca/KAW/KAW98/schreiber/) (SYALABI)
    - 3.1   Knowledge Identification 
    - 3.2   Knowledge Specification
    - 3.3   Knowledge Refinement
4. Project Solution (To detail domain modelling & system design.)
    - 4.1   Project Implementation (To detail system development & testing approach.) (JOVIN)
    - 4.2   Project Performance & Validation (To prove project objectives are met.) (SYALABI)
5. Project Conclusions
    - Findings & Recommendation (WEILIANG)
6. Appendix 
    - 6.1   Project Proposal (OPTIONAL)
    - 6.2   Mapped System Functionalities against knowledge, techniques and skills of modular courses: MR, RS, CGS (WEILIANG)
    - 6.3   Installation and User Guide (JOVIN)
    - 6.4   1-2 pages individual project report per project member, including: Individual reflection of project journey:
      - (1) personal contribution to group project 
      - (2) what have you learnt that is most useful for you 
      - (3) how you can apply the knowledge and skills in other situations or your workplaces
    - 6.5   List of Abbreviations (if applicable)
    - 6.6   References (if applicable)

## SECTION 7 : MISCELLANEOUS

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
