from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import validates

from app import db

    
class ImageConversionResult(db.Model):
    __tablename__ = 'image_conversion_result'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(50))  # Usuario que realizó la conversión
    file_name = Column(String(250))  # Nombre del archivo procesado
    red_pixels = Column(Integer)  # Número de píxeles rojos
    green_pixels = Column(Integer)  # Número de píxeles verdes
    blue_pixels = Column(Integer)  # Número de píxeles azules
    timestamp = Column(DateTime)  # Fecha y hora de la conversión
    image_path = Column(String(250))  # Ruta de la imagen procesada

    def __str__(self):
        return (f"Usuario: {self.user_name}, Archivo: {self.file_name}, "
                f"Rojos: {self.red_pixels}, Verdes: {self.green_pixels}, "
                f"Azules: {self.blue_pixels}, Fecha: {self.timestamp:%Y-%m-%d %H:%M:%S}")
