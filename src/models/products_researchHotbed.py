from db.connection import db

class ProductsResearchHotbed(db.Model):
    __tablename__ = 'productsResearchHotbed'
    
    idproductsResearchHotbed = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Corregir nombres de columnas según la base de datos
    category_productsResearchHotbed = db.Column(db.String(125), nullable=False)
    type_productsResearchHotbed = db.Column(db.String(45), nullable=False)
    description_productsResearchHotbed = db.Column(db.String(500), nullable=False)
    
    def __repr__(self):
        return f'<ProductsResearchHotbed {self.idproductsResearchHotbed}>'
