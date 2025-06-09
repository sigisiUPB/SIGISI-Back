from db.connection import db

class ProductsResearchHotbed(db.Model):
    __tablename__ = 'productsResearchHotbed'
    
    idproductsResearchHotbed = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_productsResearchHotbed = db.Column(db.String(125), nullable=False)
    type_productsResearchHotbed = db.Column(db.String(45), nullable=False)
    description_productsResearchHotbed = db.Column(db.String(500), nullable=False)
    datePublication_productsResearchHotbed = db.Column(db.Date, nullable=True)  # AGREGAR
    
    def __repr__(self):
        return f'<ProductsResearchHotbed {self.idproductsResearchHotbed}>'
