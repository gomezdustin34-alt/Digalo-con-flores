from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Optional, Length


class CheckoutForm(FlaskForm):
    first_name = StringField("Nombre", validators=[DataRequired(), Length(max=100)])
    last_name = StringField("Apellido", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Teléfono", validators=[DataRequired(), Length(max=30)])

    address = StringField("Dirección", validators=[DataRequired(), Length(max=400)])
    city = StringField("Ciudad", validators=[DataRequired(), Length(max=100)])
    additional_info = TextAreaField("Información adicional", validators=[Optional(), Length(max=300)])

    delivery_date = DateField("Fecha de entrega", validators=[Optional()])
    delivery_time = SelectField(
        "Hora aproximada",
        choices=[("", "Sin preferencia"), ("morning", "Mañana (8am - 12pm)"), ("afternoon", "Tarde (12pm - 5pm)"), ("evening", "Noche (5pm - 8pm)")],
        validators=[Optional()],
    )
    recipient_name = StringField("Nombre del destinatario", validators=[Optional(), Length(max=150)])
    dedication_message = TextAreaField("Mensaje de dedicatoria", validators=[Optional(), Length(max=500)])
