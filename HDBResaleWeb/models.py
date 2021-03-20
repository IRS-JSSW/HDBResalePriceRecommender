from HDBResaleWeb import db

class resaleDataGov(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    town = db.Column(db.String, nullable=False)
    flat_type = db.Column(db.String, nullable=False)
    flat_model = db.Column(db.String, nullable=False)
    floor_area_sqm = db.Column(db.Integer, nullable=False)
    street_name = db.Column(db.String, nullable=False)
    resale_price = db.Column(db.Integer, nullable=False)
    month = db.Column(db.String, nullable=False)
    lease_commence_date = db.Column(db.String, nullable=False)
    storey_range = db.Column(db.String, nullable=False)
    block = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"resaleDataGov('{self.town}', '{self.flat_type}', '{self.flat_model}','{self.floor_area_sqm}','{self.street_name}' \
            '{self.resale_price}', '{self.month}', '{self.lease_commence_date}', '{self.storey_range}', '{self.storey_range}')"