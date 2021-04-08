from HDBResaleWeb import db

######################################################################################################
#Data gov columns
class DataGovTable(db.Model):
#Raw features from datagov
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Date, nullable=False)
    town = db.Column(db.String, nullable=False)
    flat_type = db.Column(db.String, nullable=False)
    block = db.Column(db.String, nullable=False)
    street_name = db.Column(db.String, nullable=False)
    storey_range = db.Column(db.String, nullable=False)
    floor_area_sqm = db.Column(db.Integer, nullable=False)
    flat_model = db.Column(db.String, nullable=False)
    lease_commence_date = db.Column(db.Integer, nullable=False)
    remaining_lease = db.Column(db.String, nullable=False)
    resale_price = db.Column(db.Integer, nullable=False)
#Additional features added
    # full_address = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Integer, nullable=False)
    longitude = db.Column(db.Integer, nullable=False)
    postal_district = db.Column(db.Integer, nullable=False)
    mrt_nearest = db.Column(db.String, nullable=False)
    mrt_distance = db.Column(db.Float, nullable=False)
    mall_nearest = db.Column(db.String, nullable=False)
    mall_distance = db.Column(db.Float, nullable=False)
    cbd_distance = db.Column(db.Float, nullable=False)
    hawker_distance = db.Column(db.Float, nullable=False)
    market_distance = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return ('{self.month}','{self.town}','{self.flat_type}','{self.street_name}','{self.storey_range}',
        '{self.floor_area_sqm}', '{self.flat_model}','{self.lease_commence_date}','{self.remaining_lease}',
        '{self.resale_price}')

#Property guru columns
class PropGuruTable(db.Model):
#Raw features from datagov
    id = db.Column(db.Integer, primary_key=True)
    # month = db.Column(db.Date, nullable=False)
    # town = db.Column(db.String, nullable=False)
    flat_type = db.Column(db.String, nullable=False)
    # block = db.Column(db.String, nullable=False)
    street_name = db.Column(db.String, nullable=False)
    # storey_range = db.Column(db.String, nullable=False) #To get a range of low, mid and high floor results
    floor_area_sqm = db.Column(db.Integer, nullable=False)
    # flat_model = db.Column(db.String, nullable=False)
    lease_commence_date = db.Column(db.Integer, nullable=False) #The year built
    remaining_lease = db.Column(db.String, nullable=False) #To calculate from lease_commence_date
    resale_price = db.Column(db.Integer, nullable=False)
#Additional features added
    # full_address = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Integer, nullable=False)
    longitude = db.Column(db.Integer, nullable=False)
    postal_district = db.Column(db.Integer, nullable=False)
    mrt_nearest = db.Column(db.String, nullable=False)
    mrt_distance = db.Column(db.Float, nullable=False)
    mall_nearest = db.Column(db.String, nullable=False)
    mall_distance = db.Column(db.Float, nullable=False)
    cbd_distance = db.Column(db.Float, nullable=False)
    hawker_distance = db.Column(db.Float, nullable=False)
    market_distance = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return ('{self.flat_type}','{self.street_name}','{self.floor_area_sqm}','{self.lease_commence_date}',
        '{self.remaining_lease}','{self.resale_price}')

#Transit Rails columns
class RailTransitTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    station_name = db.Column(db.String, nullable=False)
    rail_type = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Integer, nullable=False)
    longitude = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return ('{self.station_name}','{self.rail_type}','{self.latitude}','{self.longitude}')

#Shopping mall columns
class ShoppingMallsTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Shopping_Malls = db.Column(db.String, nullable=False)
    latitude = db.Column(db.Integer, nullable=False)
    longitude = db.Column(db.Integer, nullable=False)
    full_address = db.Column(db.String, nullable=False)

#Hawker Centre columns
class HawkerCentreTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_of_centre = db.Column(db.String, nullable=False)
    type_of_centre = db.Column(db.String, nullable=False)
    owner = db.Column(db.String, nullable=False)
    no_of_stalls = db.Column(db.Integer, nullable=False)
    no_of_cooked_food_stalls = db.Column(db.Integer, nullable=False)
    no_of_mkt_produce_stalls = db.Column(db.Integer, nullable=False)
    postal_code = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.Integer, nullable=False)
    longitude = db.Column(db.Integer, nullable=False)
    full_address = db.Column(db.String, nullable=False)

#Supermarket columns
class SuperMarketTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    licensee_name = db.Column(db.String, nullable=False)
    postal_code = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.Integer, nullable=False)
    longitude = db.Column(db.Integer, nullable=False)
    full_address = db.Column(db.String, nullable=False)