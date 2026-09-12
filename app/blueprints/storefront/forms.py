from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class ContactForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Teléfono", validators=[Optional(), Length(max=30)])
    subject = StringField("Asunto", validators=[Optional(), Length(max=200)])
    message = TextAreaField("Mensaje", validators=[DataRequired(), Length(max=2000)])


class NewsletterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])


class SeguimientoForm(FlaskForm):
    """Consulta del estado de un pedido sin necesidad de tener cuenta."""
    number = StringField("Número de pedido", validators=[DataRequired(), Length(max=20)])
    email = StringField("Correo con el que hiciste el pedido", validators=[DataRequired(), Email()])
