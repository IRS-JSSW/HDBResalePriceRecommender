from HDBResaleWeb import db

class resaleDataGov(db.Model):
#Raw features from datagov
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Date, nullable=False)
    town = db.Column(db.String, nullable=False)
    flat_type = db.Column(db.String, nullable=False)
    # block = db.Column(db.String, nullable=False)
    street_name = db.Column(db.String, nullable=False)
    storey_range = db.Column(db.String, nullable=False)
    floor_area_sqm = db.Column(db.Integer, nullable=False)
    flat_model = db.Column(db.String, nullable=False)
    lease_commence_date = db.Column(db.Integer, nullable=False)
    remaining_lease = db.Column(db.String, nullable=False)
    resale_price = db.Column(db.Integer, nullable=False)
#Additional features added
    latitude = db.Column(db.Integer, nullable=False)
    longitude = db.Column(db.Integer, nullable=False)
    mrt_distance = db.Column(db.Integer, nullable=False)
    mall_nearest = db.Column(db.String, nullable=False)
    mall_distance = db.Column(db.Integer, nullable=False)
    cbd_distance = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"resaleDataGov('{self.month}','{self.town}','{self.flat_type}','{self.street_name}','{self.storey_range}','{self.floor_area_sqm}','{self.flat_model}','{self.flat_model}','{self.lease_commence_date}','{self.remaining_lease}','{self.resale_price}')"